import pytest
from app.core.config import Settings

@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        APP_NAME="文书标注系统测试",
        APP_VERSION="0.1.0",
        DEBUG=True,
        ENVIRONMENT="test",
        API_PREFIX="/api",
        CORS_ORIGINS=["http://localhost:3000"],
        DATABASE_URL="postgresql://test:test@localhost:5432/test_annotator",
        POSTGRES_USER="test",
        POSTGRES_PASSWORD="test",
        POSTGRES_DB="test_annotator",
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        REDIS_URL="redis://localhost:6379/0",
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        JWT_SECRET_KEY="test_secret_key",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        REFRESH_TOKEN_EXPIRE_DAYS=7,
        UPLOAD_DIR="./uploads",
        MAX_UPLOAD_SIZE=10485760,
        ALLOWED_EXTENSIONS=[".txt", ".pdf", ".doc", ".docx"],
        LOG_LEVEL="DEBUG",
        LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        LOG_FILE="test.log",
        CELERY_BROKER_URL="redis://localhost:6379/1",
        CELERY_RESULT_BACKEND="redis://localhost:6379/2",
        CELERY_TASK_SERIALIZER="json",
        CELERY_RESULT_SERIALIZER="json",
        CELERY_ACCEPT_CONTENT=["json"],
        CELERY_TIMEZONE="Asia/Shanghai"
    ) 