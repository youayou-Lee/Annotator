import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.user import create_user
from app.schemas.user import UserCreate
from app.services.document import create_document
from app.schemas.document import DocumentCreate
from app.services.task import create_task
from app.schemas.task import TaskCreate
from app.models.task import TaskStatus
from app.models.annotation import AnnotationType
from app.services.annotation import create_annotation
from app.schemas.annotation import AnnotationCreate
from app.models.document import Document

def test_create_annotation(client: TestClient, db: Session):
    # 创建测试用户
    user_data = {
        "email": "test1@example.com",
        "username": "testuser1",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
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
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # 创建测试任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user.id,
        "user_id": user.id,
        "status": TaskStatus.PENDING,
        "title": "测试任务",
        "description": "测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    db.refresh(task)
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user.id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    response = client.post(
        "/api/v1/annotations/",
        json=annotation_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task.id
    assert data["annotator_id"] == user.id
    assert data["annotation_type"] == AnnotationType.TEXT
    assert data["content"]["text"] == "测试标注内容"

def test_get_annotations(client: TestClient, db: Session):
    # 创建测试用户
    user_data = {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
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
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # 创建测试任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user.id,
        "user_id": user.id,
        "status": TaskStatus.PENDING,
        "title": "测试任务",
        "description": "测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    db.refresh(task)
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user.id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    response = client.post(
        "/api/v1/annotations/",
        json=annotation_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task.id
    assert data["annotator_id"] == user.id
    assert data["annotation_type"] == AnnotationType.TEXT
    assert data["content"]["text"] == "测试标注内容"

def test_get_annotation(client: TestClient, db: Session):
    user_data = {
        "email": "test3@example.com",
        "username": "testuser3",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
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
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # 创建测试任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user.id,
        "user_id": user.id,
        "status": TaskStatus.PENDING,
        "title": "测试任务",
        "description": "测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    db.refresh(task)
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user.id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    response = client.post(
        "/api/v1/annotations/",
        json=annotation_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task.id
    assert data["annotator_id"] == user.id
    assert data["annotation_type"] == AnnotationType.TEXT
    assert data["content"]["text"] == "测试标注内容"

def test_update_annotation(client: TestClient, db: Session):
    user_data = {
        "email": "test4@example.com",
        "username": "testuser4",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
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
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # 创建测试任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user.id,
        "user_id": user.id,
        "status": TaskStatus.PENDING,
        "title": "测试任务",
        "description": "测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    db.refresh(task)
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user.id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    response = client.post(
        "/api/v1/annotations/",
        json=annotation_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task.id
    assert data["annotator_id"] == user.id
    assert data["annotation_type"] == AnnotationType.TEXT
    assert data["content"]["text"] == "测试标注内容"
    
    # 更新标注
    update_data = {
        "content": {
            "text": "更新后的标注内容",
            "start_offset": 0,
            "end_offset": 15,
            "label": "更新后的标签"
        }
    }
    response = client.put(
        f"/api/v1/annotations/{data['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"]["text"] == "更新后的标注内容"
    assert data["content"]["label"] == "更新后的标签"

def test_delete_annotation(client: TestClient, db: Session):
    user_data = {
        "email": "test5@example.com",
        "username": "testuser5",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    
    # 登录获取 token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
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
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # 创建测试任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user.id,
        "user_id": user.id,
        "status": TaskStatus.PENDING,
        "title": "测试任务",
        "description": "测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    db.refresh(task)
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user.id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    response = client.post(
        "/api/v1/annotations/",
        json=annotation_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task.id
    assert data["annotator_id"] == user.id
    assert data["annotation_type"] == AnnotationType.TEXT
    assert data["content"]["text"] == "测试标注内容"
    
    # 删除标注
    response = client.delete(
        f"/api/v1/annotations/{data['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 确认标注已被删除
    response = client.get(
        f"/api/v1/annotations/{data['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404 