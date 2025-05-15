import importlib.util
import sys
import os
from typing import Dict

# 确保按正确的顺序导入模型
from app.models.user import User
from app.models.document import Document
from app.models.task import Task
from app.models.annotation import Annotation
import app.db.base  # 强制注册所有模型

# 设置必要的环境变量
os.environ["DEBUG"] = "True"
os.environ["ENVIRONMENT"] = "test"
os.environ["POSTGRES_USER"] = "test_user"
os.environ["POSTGRES_PASSWORD"] = "test_password"
os.environ["POSTGRES_DB"] = "test_db"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["UPLOAD_DIR"] = "./test_uploads"
os.environ["MAX_UPLOAD_SIZE"] = "10485760"
os.environ["ALLOWED_EXTENSIONS"] = '[".txt", ".pdf", ".doc", ".docx"]'
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["LOG_FORMAT"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
os.environ["LOG_FILE"] = "test.log"
os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/1"
os.environ["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/1"
os.environ["CELERY_TASK_SERIALIZER"] = "json"
os.environ["CELERY_RESULT_SERIALIZER"] = "json"
os.environ["CELERY_ACCEPT_CONTENT"] = "[\"json\"]"
os.environ["CELERY_TIMEZONE"] = "UTC"

main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app/main.py"))
spec = importlib.util.spec_from_file_location("main", main_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
fastapi_app = main.app

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base import Base
from app.api.deps import get_db
from app.core.config import settings
from tests.utils.utils import get_superuser_token_headers

# 用内存数据库+StaticPool，保证所有连接共享同一内存
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 关键：强制覆盖 app.db.session.SessionLocal
import app.db.session
app.db.session.SessionLocal = TestingSessionLocal

# 覆盖 settings
settings.DATABASE_URL = SQLALCHEMY_DATABASE_URL
settings.DEBUG = True
settings.ENVIRONMENT = "test"
settings.SECRET_KEY = "test_secret_key"
settings.ALGORITHM = "HS256"
settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
settings.UPLOAD_DIR = "./test_uploads"
settings.MAX_UPLOAD_SIZE = 10485760
settings.ALLOWED_EXTENSIONS = [".txt", ".pdf", ".doc", ".docx"]
settings.LOG_LEVEL = "DEBUG"
settings.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
settings.LOG_FILE = "test.log"

@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    # 自动创建所有表，避免依赖顺序问题
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    fastapi_app.dependency_overrides[get_db] = override_get_db
    # 打印所有已注册路由
    print("\n已注册路由:")
    for route in fastapi_app.routes:
        print(route.path)
    with TestClient(fastapi_app, base_url="http://test") as c:
        yield c

@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_superuser_token_headers(client) 