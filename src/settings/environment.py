from enum import Enum
from kombu.utils.url import safequote

from dotenv import dotenv_values
from sqlalchemy.engine import URL
from icecream import ic

config = dotenv_values()


class DataBaseEnviornment(Enum):
    RDB_LIB: str = config.get('RDB_LIB', 'postgresql+asyncpg')
    RDB_HOST: str = config.get('RDB_HOST', 'postgres:5432')
    RDB_PORT: int = config.get('RDB_PORT', 5432)
    RDB_USER: str = config.get('RDB_USER', 'postgres')
    RDB_PASS: str = config.get('RDB_PASS', 'postgres')
    RDB_DB: str = config.get('RDB_DB', 'auth-db')
    RDB_DRIVER: str = config.get('RDB_DRIVER', 'postgresql+asyncpg')

    @classmethod
    def get_url_connection(cls):
        ic(cls.RDB_LIB.value)
        ic(cls.RDB_HOST.value)
        ic(cls.RDB_LIB)
        ic(cls.RDB_HOST)

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
        return f"{cls.RDB_LIB.value}://{cls.RDB_USER.value}:{cls.RDB_PASS.value}@{cls.RDB_HOST.value}:{cls.RDB_PORT.value}/{cls.RDB_DB.value}"

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
            host=cls.REDIS_HOST.value,
            port=int(cls.REDIS_PORT.value),
            password=cls.REDIS_PASSWORD.value,
            database=cls.REDIS_DB.value,
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
    

class GoogleEnvironment(Enum):
    GOOGLE_CLIENT_ID: str = config.get('GOOGLE_CLIENT_ID', '1234567890')
    GOOGLE_CLIENT_SECRET: str = config.get('GOOGLE_CLIENT_SECRET', '1234567890')
    GOOGLE_REDIRECT_URI: str = config.get('GOOGLE_REDIRECT_URI', 'http://facreport.iptime.org:8000/api/v1/auth/google/callback')
    FRONTEND_REDIRECT_URL: str = config.get('FRONTEND_REDIRECT_URL', 'http://facreport.iptime.org:8000')


class MonitoringEnvironment(Enum):
    # Monitoring
    ENABLE_METRICS: bool = config.get('ENABLE_METRICS', True)
    PROMETHEUS_MULTIPROC_DIR: str = config.get('PROMETHEUS_MULTIPROC_DIR', "/tmp")

    @classmethod
    def get_prometheus_multiproc_dir(cls) -> str:
        return cls.PROMETHEUS_MULTIPROC_DIR.value
    
    
class SecretKeyEnvironment(Enum):
    SECRET_KEY: str = config.get('SECRET_KEY', 'REPLACE_THIS_WITH_YOUR_SECURE_SECRET_KEY')
    ALGORITHM: str = config.get('ALGORITHM', 'HS256')

    @classmethod
    def get_secret_key(cls) -> str:
        return cls.SECRET_KEY.value
    
    @classmethod
    def get_algorithm(cls) -> str:
        return cls.ALGORITHM.value