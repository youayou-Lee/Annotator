import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.user import create_user
from app.schemas.user import UserCreate
from app.core.config import settings

def test_upload_document(client: TestClient, db: Session):
    # 创建测试用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 创建测试文件
    test_file_content = b"test file content"
    test_file = ("test.txt", test_file_content)
    
    # 上传文件
    response = client.post(
        "/api/documents/",
        files={"file": test_file},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "test.txt"
    assert data["file_size"] == len(test_file_content)
    assert data["uploader_id"] == user.id
    
    # 清理测试文件
    if os.path.exists(data["file_path"]):
        os.remove(data["file_path"])

def test_upload_invalid_file_type(client: TestClient, db: Session):
    # 创建测试用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 创建测试文件（不支持的类型）
    test_file_content = b"test file content"
    test_file = ("test.invalid", test_file_content)
    
    # 尝试上传文件
    response = client.post(
        "/api/documents/",
        files={"file": test_file},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "不支持的文件类型" in response.json()["detail"]

def test_get_documents(client: TestClient, db: Session):
    # 创建测试用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 上传测试文件
    test_file_content = b"test file content"
    test_file = ("test.txt", test_file_content)
    
    response = client.post(
        "/api/documents/",
        files={"file": test_file},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    document = response.json()
    
    # 获取文档列表
    response = client.get(
        "/api/documents/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == document["id"]
    
    # 清理测试文件
    if os.path.exists(document["file_path"]):
        os.remove(document["file_path"])

def test_get_document(client: TestClient, db: Session):
    # 创建测试用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 上传测试文件
    test_file_content = b"test file content"
    test_file = ("test.txt", test_file_content)
    
    response = client.post(
        "/api/documents/",
        files={"file": test_file},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    document = response.json()
    
    # 获取单个文档
    response = client.get(
        f"/api/documents/{document['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == document["id"]
    
    # 清理测试文件
    if os.path.exists(document["file_path"]):
        os.remove(document["file_path"])

def test_update_document(client: TestClient, db: Session):
    # 创建测试用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 上传测试文件
    test_file_content = b"test file content"
    test_file = ("test.txt", test_file_content)
    
    response = client.post(
        "/api/documents/",
        files={"file": test_file},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    document = response.json()
    
    # 更新文档状态
    update_data = {
        "status": "completed",
        "error_message": None
    }
    response = client.put(
        f"/api/documents/{document['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    
    # 清理测试文件
    if os.path.exists(document["file_path"]):
        os.remove(document["file_path"])

def test_delete_document(client: TestClient, db: Session):
    # 创建测试用户
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 上传测试文件
    test_file_content = b"test file content"
    test_file = ("test.txt", test_file_content)
    
    response = client.post(
        "/api/documents/",
        files={"file": test_file},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    document = response.json()
    
    # 删除文档
    response = client.delete(
        f"/api/documents/{document['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 确认文档已被删除
    response = client.get(
        f"/api/documents/{document['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404 