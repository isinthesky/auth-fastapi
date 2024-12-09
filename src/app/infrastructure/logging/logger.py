# src/app/infrastructure/logging/logger.py

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json

from src.settings.environment import LoggingEnvironment

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
        }
        return json.dumps(log_record)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LoggingEnvironment.LOG_LEVEL.value))

    # 파일 핸들러 설정
    log_dir = Path(LoggingEnvironment.LOG_DIR.value)
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        filename=log_dir / f"{name}.log",
        maxBytes=LoggingEnvironment.LOG_FILE_MAX_BYTES.value,
        backupCount=LoggingEnvironment.LOG_FILE_BACKUP_COUNT.value
    )
    file_handler.setFormatter(JsonFormatter())

    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# 로거 인스턴스 생성
api_logger = setup_logger("api")
db_logger = setup_logger("database")
auth_logger = setup_logger("auth")