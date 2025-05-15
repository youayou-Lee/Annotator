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
from app.models.annotation import AnnotationType, AnnotationStatus
from app.services.annotation import create_annotation, get_annotation
from app.schemas.annotation import AnnotationCreate
from app.models.document import Document
from app.models.user import User
from app.models.task import Task
from app.models.annotation import Annotation
from app.core.config import settings
from tests.utils.utils import get_superuser_token_headers
from tests.utils.user import create_random_user
from tests.utils.document import create_random_document
from tests.utils.task import create_random_task
from tests.utils.annotation import create_random_annotation

def test_create_annotation(client: TestClient, db: Session):
    # 创建测试用户
    user_data = {
        "email": "test1@example.com",
        "username": "testuser1",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id  # 保存用户ID，避免后续使用user对象
    
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
        "uploader_id": user_id
    }
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # 创建测试任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user_id,
        "user_id": user_id,
        "status": TaskStatus.PENDING,
        "title": "测试任务",
        "description": "测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    task_id = task.id  # 只保存ID，不使用task对象
    
    # 创建标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
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
    assert data["task_id"] == task_id
    assert data["annotator_id"] == user_id
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
    user_id = user.id  # 保存用户ID，避免后续使用user对象
    
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
        "uploader_id": user_id
    }
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # 创建测试任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user_id,
        "user_id": user_id,
        "status": TaskStatus.PENDING,
        "title": "测试任务",
        "description": "测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    task_id = task.id  # 只保存ID，不使用task对象
    
    # 创建标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 获取标注列表
    response = client.get(
        "/api/v1/annotations/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["task_id"] == task_id
    assert data[0]["annotator_id"] == user_id

def test_get_annotation(client: TestClient, db: Session):
    user_data = {
        "email": "test3@example.com",
        "username": "testuser3",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id  # 保存用户ID，避免后续使用user对象
    
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
        "uploader_id": user_id
    }
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # 创建测试任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user_id,
        "user_id": user_id,
        "status": TaskStatus.PENDING,
        "title": "测试任务",
        "description": "测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    task_id = task.id  # 只保存ID，不使用task对象
    
    # 创建标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    annotation_id = annotation.id  # 只保存ID，不使用annotation对象
    
    # 获取单个标注
    response = client.get(
        f"/api/v1/annotations/{annotation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == annotation_id
    assert data["task_id"] == task_id
    assert data["annotator_id"] == user_id
    assert data["annotation_type"] == AnnotationType.TEXT
    assert data["content"]["text"] == "测试标注内容"

def test_update_annotation(client: TestClient, db: Session):
    user_data = {
        "email": "test4@example.com",
        "username": "testuser4",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id  # 保存用户ID，避免后续使用user对象
    
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
        "uploader_id": user_id
    }
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # 创建测试任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user_id,
        "user_id": user_id,
        "status": TaskStatus.PENDING,
        "title": "测试任务",
        "description": "测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    task_id = task.id  # 只保存ID，不使用task对象
    
    # 创建标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    annotation_id = annotation.id  # 只保存ID，不使用annotation对象
    
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
        f"/api/v1/annotations/{annotation_id}",
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
    user_id = user.id  # 保存用户ID，避免后续使用user对象
    
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
        "uploader_id": user_id
    }
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # 创建测试任务
    task_data = {
        "document_id": document.id,
        "annotator_id": user_id,
        "user_id": user_id,
        "status": TaskStatus.PENDING,
        "title": "测试任务",
        "description": "测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    task_id = task.id  # 只保存ID，不使用task对象
    
    # 创建标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    annotation_id = annotation.id  # 只保存ID，不使用annotation对象
    
    # 删除标注
    response = client.delete(
        f"/api/v1/annotations/{annotation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 确认标注已被删除
    response = client.get(
        f"/api/v1/annotations/{annotation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_create_conflicting_annotations(
    client: TestClient, db: Session
) -> None:
    # 创建用户
    user = create_random_user(db)
    user_id = user.id  # 保存用户ID，避免后续使用user对象
    
    login_data = {
        "username": user.email,
        "password": "testpass123",
    }
    r = client.post("/api/v1/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建文档
    document = create_random_document(db, owner_id=user_id)
    document_id = document.id
    
    # 创建任务
    task_data = {
        "document_id": document_id,
        "annotator_id": user_id,
        "user_id": user_id,
        "title": "Test Task",
        "description": "Test Description"
    }
    r = client.post("/api/v1/tasks/", json=task_data, headers=headers)
    assert r.status_code == 200
    task = r.json()
    
    # 创建第一个标注
    annotation_data = {
        "task_id": task["id"],
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "Test annotation",
            "start_offset": 0,
            "end_offset": 10
        }
    }
    r = client.post("/api/v1/annotations/", json=annotation_data, headers=headers)
    assert r.status_code == 200
    annotation1 = r.json()
    assert annotation1["status"] == AnnotationStatus.PENDING
    
    # 创建重叠的标注
    annotation_data2 = {
        "task_id": task["id"],
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "Test annotation",
            "start_offset": 5,
            "end_offset": 15
        }
    }
    r = client.post("/api/v1/annotations/", json=annotation_data2, headers=headers)
    assert r.status_code == 200
    annotation2 = r.json()
    assert annotation2["status"] == AnnotationStatus.CONFLICT
    assert annotation2["conflict_with"] == annotation1["id"]
    
    # 验证第一个标注也被标记为冲突
    r = client.get(f"/api/v1/annotations/{annotation1['id']}", headers=headers)
    assert r.status_code == 200
    updated_annotation1 = r.json()
    assert updated_annotation1["status"] == AnnotationStatus.CONFLICT
    assert updated_annotation1["conflict_with"] == annotation2["id"]

def test_update_annotation_creates_conflict(
    client: TestClient, db: Session
) -> None:
    # 创建用户
    user = create_random_user(db)
    user_id = user.id  # 保存用户ID，避免后续使用user对象
    
    login_data = {
        "username": user.email,
        "password": "testpass123",
    }
    r = client.post("/api/v1/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建文档
    document = create_random_document(db, owner_id=user_id)
    document_id = document.id
    
    # 创建任务
    task_data = {
        "document_id": document_id,
        "annotator_id": user_id,
        "user_id": user_id,
        "title": "Test Task",
        "description": "Test Description"
    }
    r = client.post("/api/v1/tasks/", json=task_data, headers=headers)
    assert r.status_code == 200
    task = r.json()
    
    # 创建两个不重叠的标注
    annotation_data1 = {
        "task_id": task["id"],
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "Test annotation 1",
            "start_offset": 0,
            "end_offset": 10
        }
    }
    r = client.post("/api/v1/annotations/", json=annotation_data1, headers=headers)
    assert r.status_code == 200
    annotation1 = r.json()
    
    annotation_data2 = {
        "task_id": task["id"],
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "Test annotation 2",
            "start_offset": 20,
            "end_offset": 30
        }
    }
    r = client.post("/api/v1/annotations/", json=annotation_data2, headers=headers)
    assert r.status_code == 200
    annotation2 = r.json()
    
    # 更新第二个标注使其与第一个重叠
    update_data = {
        "content": {
            "text": "Test annotation 2",
            "start_offset": 5,
            "end_offset": 15
        }
    }
    r = client.put(f"/api/v1/annotations/{annotation2['id']}", json=update_data, headers=headers)
    assert r.status_code == 200
    updated_annotation2 = r.json()
    assert updated_annotation2["status"] == AnnotationStatus.CONFLICT
    assert updated_annotation2["conflict_with"] == annotation1["id"]
    
    # 验证第一个标注也被标记为冲突
    r = client.get(f"/api/v1/annotations/{annotation1['id']}", headers=headers)
    assert r.status_code == 200
    updated_annotation1 = r.json()
    assert updated_annotation1["status"] == AnnotationStatus.CONFLICT
    assert updated_annotation1["conflict_with"] == annotation2["id"]