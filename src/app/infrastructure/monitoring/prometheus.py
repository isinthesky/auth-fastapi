# src/app/infrastructure/monitoring/prometheus.py

from typing import Callable
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, Gauge, REGISTRY, multiprocess, CollectorRegistry
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from src.settings.environment import MonitoringEnvironment
import time
import os

class PrometheusMiddleware:
    def __init__(self):
        self.request_count = Counter(
            "http_requests_total",
            "Total count of HTTP requests by method, endpoint, and status",
            ["method", "endpoint", "status"]
        )
        
        self.request_latency = Histogram(
            "http_request_duration_seconds",
            "HTTP request latency in seconds by method and endpoint",
            ["method", "endpoint"],
            buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
        )
        
        self.requests_in_progress = Gauge(
            "http_requests_in_progress",
            "Number of HTTP requests in progress by method and endpoint",
            ["method", "endpoint"]
        )

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        endpoint = request.url.path
        
        # 진행 중인 요청 카운트 증가
        self.requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        
        # 요청 처리 시작 시간
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as e:
            status_code = 500
            raise e
        finally:
            # 요청 처리 완료 후 메트릭 기록
            self.request_count.labels(
                method=method,
                endpoint=endpoint,
                status=status_code
            ).inc()
            
            # 요청 처리 시간 기록
            self.request_latency.labels(
                method=method,
                endpoint=endpoint
            ).observe(time.time() - start_time)
            
            # 진행 중인 요청 카운트 감소
            self.requests_in_progress.labels(
                method=method,
                endpoint=endpoint
            ).dec()
            
        return response

class PrometheusService:
    def __init__(self):
        if MonitoringEnvironment.ENABLE_METRICS.value:
            # 멀티프로세스 모드 설정
            if 'prometheus_multiproc_dir' in os.environ:
                registry = CollectorRegistry()
                multiprocess.MultiProcessCollector(registry)
            else:
                registry = REGISTRY
            self.registry = registry
        
    def init_app(self, app: FastAPI) -> None:
        """FastAPI 애플리케이션에 Prometheus 미들웨어와 메트릭 엔드포인트를 설정합니다."""
        if not MonitoringEnvironment.ENABLE_METRICS.value:
            return
        
        # Prometheus 미들웨어 추가
        app.add_middleware(PrometheusMiddleware)
        
        # 메트릭 엔드포인트 추가
        @app.get("/metrics")
        async def metrics():
            return Response(
                generate_latest(self.registry),
                media_type=CONTENT_TYPE_LATEST
            )

def setup_monitoring(app: FastAPI) -> None:
    """
    FastAPI 애플리케이션에 Prometheus 모니터링을 설정합니다.
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    """
    prometheus_service = PrometheusService()
    prometheus_service.init_app(app)