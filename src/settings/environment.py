from enum import Enum
from kombu.utils.url import safequote

from dotenv import dotenv_values
from sqlalchemy.engine import URL

config = dotenv_values()


class DataBaseEnviornment(Enum):
    RDB_LIB: str = config['RDB_LIB']
    RDB_HOST: str = config["RDB_HOST_PRODUCT"] if config["PROJECT_STATE"] == "PRODUCT" else config["RDB_HOST_DEV"]
    RDB_PORT: int = config['RDB_PORT']
    RDB_USER: str = config['RDB_USER']
    RDB_PASS: str = config['RDB_PASS']
    RDB_DB: str = config['RDB_DB']
    RDB_DRIVER: str = config['RDB_DRIVER']

    @classmethod
    def get_url_connection(cls):
        return URL.create(
            drivername=cls.RDB_LIB.value,
            host=cls.RDB_HOST.value,
            port=int(cls.RDB_PORT.value),
            username=cls.RDB_USER.value,
            password=cls.RDB_PASS.value,
            database=cls.RDB_DB.value,
            query={
                "driver": cls.RDB_DRIVER.value
            },
        )
    
    @classmethod
    def get_async_url_connection(cls):
        return f"postgresql+asyncpg://{cls.RDB_USER.value}:{cls.RDB_PASS.value}@{cls.RDB_HOST.value}:{cls.RDB_PORT.value}/{cls.RDB_DB.value}"

class RedisEnvironment(Enum):
    REDIS_HOST: str = config.get('REDIS_HOST', '192.168.0.23')
    REDIS_PORT: int = int(config.get('REDIS_PORT', 6379))
    REDIS_PASSWORD: str = config['REDIS_PASSWORD']
    REDIS_DB: int = int(config.get('REDIS_DB', 0))

    @classmethod
    def get_url(cls) -> str:
        return f"redis://:{safequote(cls.REDIS_PASSWORD.value)}@{cls.REDIS_HOST.value}:{cls.REDIS_PORT.value}/{cls.REDIS_DB.value}"

    @classmethod
    def get_url_connection(cls):
        return URL.create(
            drivername="redis",
            host=cls.USER_REDIS_HOST.value,
            port=int(cls.USER_REDIS_PORT.value),
            password=cls.USER_REDIS_PASSWORD.value,
            database=cls.USER_REDIS_DB.value,
        )


class DeployEnviorment(Enum):
    PROJECT_STATE: str = config['PROJECT_STATE']

    @classmethod
    def is_dev(cls) -> bool:
        return cls.PROJECT_STATE.value == "DEV"

class LoggingEnvironment(Enum):
    LOG_LEVEL: str = config.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_DIR: str = config.get('LOG_DIR', 'logs')
    LOG_FILE_MAX_BYTES: int = int(config.get('LOG_FILE_MAX_BYTES', 10485760))  # 10MB
    LOG_FILE_BACKUP_COUNT: int = int(config.get('LOG_FILE_BACKUP_COUNT', 5))


class MonitoringEnvironment(Enum):
    # Monitoring
    ENABLE_METRICS: bool = config.get('ENABLE_METRICS', True)
    PROMETHEUS_MULTIPROC_DIR: str = config.get('PROMETHEUS_MULTIPROC_DIR', "/tmp")
    