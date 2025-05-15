import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.user import create_user
from app.schemas.user import UserCreate
from app.services.document import create_document
from app.schemas.document import DocumentCreate
from app.models.task import TaskStatus
from app.services.task import create_task
from app.schemas.task import TaskCreate

def test_create_task(client: TestClient, db: Session):
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
    
    # 创建测试文档
    document_data = {
        "filename": "test.txt",
        "original_filename": "test.txt",
        "file_path": "/tmp/test.txt",
        "file_size": 100,
        "file_type": ".txt",
        "uploader_id": user.id
    }
    document = create_document(db, DocumentCreate(**document_data))
    
    # 创建任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user.id,
        "status": TaskStatus.PENDING
    }
    response = client.post(
        "/api/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == document.id
    assert data["annotator_id"] == user.id
    assert data["status"] == TaskStatus.PENDING

def test_get_tasks(client: TestClient, db: Session):
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
    
    # 创建测试文档
    document_data = {
        "filename": "test.txt",
        "original_filename": "test.txt",
        "file_path": "/tmp/test.txt",
        "file_size": 100,
        "file_type": ".txt",
        "uploader_id": user.id
    }
    document = create_document(db, DocumentCreate(**document_data))
    
    # 创建任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user.id,
        "status": TaskStatus.PENDING
    }
    task = create_task(db, TaskCreate(**task_data))
    
    # 获取任务列表
    response = client.get(
        "/api/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == task.id

def test_get_task(client: TestClient, db: Session):
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
    
    # 创建测试文档
    document_data = {
        "filename": "test.txt",
        "original_filename": "test.txt",
        "file_path": "/tmp/test.txt",
        "file_size": 100,
        "file_type": ".txt",
        "uploader_id": user.id
    }
    document = create_document(db, DocumentCreate(**document_data))
    
    # 创建任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user.id,
        "status": TaskStatus.PENDING
    }
    task = create_task(db, TaskCreate(**task_data))
    
    # 获取单个任务
    response = client.get(
        f"/api/tasks/{task.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id

def test_update_task(client: TestClient, db: Session):
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
    
    # 创建测试文档
    document_data = {
        "filename": "test.txt",
        "original_filename": "test.txt",
        "file_path": "/tmp/test.txt",
        "file_size": 100,
        "file_type": ".txt",
        "uploader_id": user.id
    }
    document = create_document(db, DocumentCreate(**document_data))
    
    # 创建任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user.id,
        "status": TaskStatus.PENDING
    }
    task = create_task(db, TaskCreate(**task_data))
    
    # 更新任务
    update_data = {
        "status": TaskStatus.COMPLETED
    }
    response = client.put(
        f"/api/tasks/{task.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == TaskStatus.COMPLETED

def test_delete_task(client: TestClient, db: Session):
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
    
    # 创建测试文档
    document_data = {
        "filename": "test.txt",
        "original_filename": "test.txt",
        "file_path": "/tmp/test.txt",
        "file_size": 100,
        "file_type": ".txt",
        "uploader_id": user.id
    }
    document = create_document(db, DocumentCreate(**document_data))
    
    # 创建任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user.id,
        "status": TaskStatus.PENDING
    }
    task = create_task(db, TaskCreate(**task_data))
    
    # 删除任务
    response = client.delete(
        f"/api/tasks/{task.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 确认任务已被删除
    response = client.get(
        f"/api/tasks/{task.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404 