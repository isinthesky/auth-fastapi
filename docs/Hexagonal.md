Hexagonal Architecture를 기반으로 한 FastAPI 프로젝트 설계 지침

1. 프로젝트 구조

FastAPI 프로젝트를 Hexagonal Architecture로 설계할 때, 프로젝트 구조는 각 역할을 명확히 분리해야 합니다.

src/
├── app/
│   ├── api/              # Presentation Layer (FastAPI 엔드포인트)
│   │   ├── v1/
│   │   │   ├── endpoints/ # HTTP 라우트 정의
│   │   │   └── schemas/   # 요청 및 응답 데이터 모델 (Pydantic)
│   ├── core/             # Application Core
│   │   ├── domain/       # 도메인 엔티티와 비즈니스 규칙
│   │   ├── ports/        # Ports 인터페이스 정의 (입력/출력 경계)
│   │   └── services/     # Use Cases와 Application Logic
│   ├── adapters/         # Adapters (외부 시스템과의 통합)
│   │   ├── persistence/  # 데이터베이스 접근 (리포지토리 구현)
│   │   ├── external/     # 외부 API 클라이언트
│   │   └── cli/          # CLI와 같은 비 HTTP 인터페이스
│   ├── config/           # 설정 및 환경 변수 관리
│   └── tests/            # 테스트 코드
├── main.py               # FastAPI 어플리케이션 초기화

2. 핵심 설계 원칙

2.1 도메인 로직 중심

	•	도메인 로직은 항상 core/domain에 위치.
	•	외부 의존성(FastAPI, DB, 외부 API 등)은 도메인 로직에 영향을 주지 않도록 설계.

2.2 의존성 방향

	•	외부 의존성은 항상 도메인 로직의 인터페이스(ports)에 의존.
	•	ports는 adapters와 api 계층에서 구현.

2.3 단방향 의존성

	•	API → Services → Domain
	•	Adapters → Domain (via Ports)

3. 주요 컴포넌트

3.1 도메인

	•	목적: 비즈니스 엔티티 및 규칙 정의.
	•	지침:
	•	외부 의존성을 금지.
	•	Pydantic 또는 ORM과 같은 외부 라이브러리를 사용하지 않음.
	•	도메인 엔티티를 기반으로 핵심 규칙과 상태를 관리.

3.2 Ports

	•	목적: 도메인과 외부 세계 간의 계약 정의.
	•	지침:
	•	인터페이스로 정의 (Protocol 사용 가능).
	•	입력(서비스 로직에서 사용)과 출력(어댑터에서 구현)으로 나눔.

3.3 Adapters

	•	목적: 외부 시스템(DB, API, 메시지 큐 등)과의 연결.
	•	지침:
	•	각 Adapter는 Port의 구현체로 동작.
	•	Persistence Adapter는 데이터베이스 접근을 담당.
	•	외부 API 통신은 전용 클라이언트를 구현.

3.4 Services

	•	목적: 비즈니스 Use Case를 구현.
	•	지침:
	•	하나의 서비스는 하나의 유스케이스에 집중.
	•	도메인 엔티티를 조작하며, 외부 시스템과의 통신은 Ports를 통해 수행.

3.5 API

	•	목적: 사용자와 상호작용(HTTP 요청/응답).
	•	지침:
	•	입력 데이터는 Pydantic 모델로 검증.
	•	API 계층에서 비즈니스 로직을 실행하지 않음.
	•	서비스 계층에 요청 전달 및 응답 처리.

4. 설정 및 환경 관리

4.1 Config

	•	app/config.py에서 환경 변수를 관리.
	•	환경 변수는 os.getenv나 pydantic.BaseSettings를 활용.

4.2 의존성 주입

	•	FastAPI의 Dependency Injection 기능을 활용.
	•	서비스와 어댑터를 DI 컨테이너로 주입하여 느슨한 결합 유지.

5. 테스트 전략

5.1 단위 테스트

	•	각 계층에 대해 독립적으로 작성.
	•	도메인 로직은 Mocking 없이 테스트.
	•	Ports와 Adapters는 Mocking을 통해 격리.

5.2 통합 테스트

	•	주요 경로(API → Service → Adapters)를 테스트.
	•	데이터베이스 등 실제 외부 의존성을 사용.

5.3 End-to-End 테스트

	•	전체 애플리케이션 흐름을 테스트.
	•	TestClient를 사용해 FastAPI 엔드포인트를 호출.

6. 설계 지침

	•	단일 책임 원칙(SRP): 각 클래스나 모듈은 하나의 책임만 가짐.
	•	Open/Closed 원칙(OCP): 기존 코드를 수정하지 않고 기능 확장이 가능하도록 설계.
	•	의존성 역전 원칙(DIP): 고수준 모듈(도메인 로직)은 저수준 모듈(외부 시스템)에 의존하지 않음.

7. 기술 스택

	•	프레임워크: FastAPI
	•	데이터베이스: SQLAlchemy, Tortoise ORM 등
	•	테스트 도구: pytest, FastAPI TestClient
	•	의존성 관리: Poetry 또는 pip-tools
	•	코드 품질: mypy, flake8, black

8. 예제

Port 예제

from typing import Protocol
from app.core.domain.entities import User

class UserRepositoryPort(Protocol):
    def get_user_by_id(self, user_id: int) -> User: pass
    def save_user(self, user: User) -> None: pass

Adapter 예제

from app.core.ports.user_repository import UserRepositoryPort
from app.core.domain.entities import User

class SQLAlchemyUserRepository(UserRepositoryPort):
    def get_user_by_id(self, user_id: int) -> User:
        # SQLAlchemy를 통해 DB에서 사용자 조회
        pass

    def save_user(self, user: User) -> None:
        # 사용자 저장
        pass
