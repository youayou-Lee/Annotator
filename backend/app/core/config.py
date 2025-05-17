from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Annotator"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool
    ENVIRONMENT: str
    API_PREFIX: str = "/api/v1"
    
    # CORS配置
    CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:123456@localhost:5432/annotator"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # 使用PostgreSQL参数构建连接URL
        postgres_url = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return postgres_url

    # Redis配置
    REDIS_URL: str
    REDIS_HOST: str
    REDIS_PORT: int

    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # 文件存储配置
    UPLOAD_DIR: str
    MAX_UPLOAD_SIZE: int
    ALLOWED_EXTENSIONS: List[str]

    # 日志配置
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_FILE: str

    # Celery配置
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_TASK_SERIALIZER: str
    CELERY_RESULT_SERIALIZER: str
    CELERY_ACCEPT_CONTENT: List[str]
    CELERY_TIMEZONE: str

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

def get_settings():
    return settings 