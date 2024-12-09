from typing import Protocol
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LoggerPort(Protocol):
    def debug(self, message: str, **kwargs) -> None:
        pass
    
    def info(self, message: str, **kwargs) -> None:
        pass
    
    def warning(self, message: str, **kwargs) -> None:
        pass
    
    def error(self, message: str, **kwargs) -> None:
        pass
    
    def critical(self, message: str, **kwargs) -> None:
        pass 