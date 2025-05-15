import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.user import create_user
from app.schemas.user import UserCreate

def test_register_user(client: TestClient, db: Session):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data

def test_register_duplicate_email(client: TestClient, db: Session):
    # 先创建一个用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    create_user(db, UserCreate(**user_data))
    
    # 尝试用相同的邮箱注册
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert "该邮箱已被注册" in response.json()["detail"]

def test_login_success(client: TestClient, db: Session):
    # 先创建用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    create_user(db, UserCreate(**user_data))
    
    # 测试登录
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, db: Session):
    # 先创建用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    create_user(db, UserCreate(**user_data))
    
    # 使用错误密码登录
    login_data = {
        "username": user_data["email"],
        "password": "wrongpass"
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 401
    assert "用户名或密码错误" in response.json()["detail"] 