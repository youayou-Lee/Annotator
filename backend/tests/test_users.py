import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.user import create_user
from app.schemas.user import UserCreate

def test_create_user(client: TestClient, db: Session):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data

def test_read_users(client: TestClient, db: Session):
    # 创建两个用户
    users_data = [
        {
            "email": "test1@example.com",
            "username": "testuser1",
            "password": "testpass123"
        },
        {
            "email": "test2@example.com",
            "username": "testuser2",
            "password": "testpass123"
        }
    ]
    for user_data in users_data:
        create_user(db, UserCreate(**user_data))
    
    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["email"] == users_data[0]["email"]
    assert data[1]["email"] == users_data[1]["email"]

def test_read_user(client: TestClient, db: Session):
    # 创建用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    response = client.get(f"/api/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]

def test_read_nonexistent_user(client: TestClient, db: Session):
    response = client.get("/api/users/999")
    assert response.status_code == 404
    assert "用户不存在" in response.json()["detail"]

def test_update_user(client: TestClient, db: Session):
    # 创建用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 更新用户
    update_data = {
        "email": "updated@example.com",
        "username": "updateduser"
    }
    response = client.put(f"/api/users/{user.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == update_data["email"]
    assert data["username"] == update_data["username"]

def test_delete_user(client: TestClient, db: Session):
    # 创建用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 删除用户
    response = client.delete(f"/api/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    
    # 确认用户已被删除
    response = client.get(f"/api/users/{user.id}")
    assert response.status_code == 404 