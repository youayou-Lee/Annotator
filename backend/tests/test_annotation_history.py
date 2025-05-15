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
from app.services.annotation import create_annotation, update_annotation, delete_annotation
from app.schemas.annotation import AnnotationCreate, AnnotationUpdate
from app.models.document import Document
from app.models.user import User
from app.models.task import Task
from app.models.annotation import Annotation

def test_create_annotation_with_history(client: TestClient, db: Session):
    """测试创建标注时自动创建历史记录"""
    # 创建测试用户
    user_data = {
        "email": "test_history@example.com",
        "username": "test_history_user",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id
    
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
        "filename": "test_history.txt",
        "original_filename": "test_history.txt",
        "file_path": "/tmp/test_history.txt",
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
        "title": "历史记录测试任务",
        "description": "历史记录测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "历史记录测试标注内容",
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
    annotation = response.json()
    
    # 获取标注历史记录
    response = client.get(
        f"/api/v1/annotations/{annotation['id']}/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    history = response.json()
    
    # 验证历史记录内容
    assert len(history) == 1
    assert history[0]["annotation_id"] == annotation["id"]
    assert history[0]["user_id"] == user_id
    assert history[0]["action"] == "CREATE"
    assert "content" in history[0]
    assert history[0]["content"]["task_id"] == task.id

def test_update_annotation_with_history(client: TestClient, db: Session):
    """测试更新标注时自动创建历史记录"""
    # 创建测试用户
    user_data = {
        "email": "test_history_update@example.com",
        "username": "test_history_update_user",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id
    
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
    
    # 创建测试文档和任务
    document_data = {
        "filename": "test_history_update.txt",
        "original_filename": "test_history_update.txt",
        "file_path": "/tmp/test_history_update.txt",
        "file_size": 100,
        "file_type": ".txt",
        "uploader_id": user_id
    }
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    task_data = {
        "document_id": document.id,
        "annotator_id": user_id,
        "user_id": user_id,
        "status": TaskStatus.PENDING,
        "title": "更新历史记录测试任务",
        "description": "更新历史记录测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "原始标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "原始标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 更新标注
    update_data = {
        "content": {
            "text": "更新后的标注内容",
            "start_offset": 5,
            "end_offset": 15,
            "label": "更新后的标签"
        }
    }
    response = client.put(
        f"/api/v1/annotations/{annotation.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 获取标注历史记录
    response = client.get(
        f"/api/v1/annotations/{annotation.id}/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    history = response.json()
    
    # 验证历史记录内容
    assert len(history) == 2  # 创建和更新各一条记录
    # 更新记录应该排在最前面
    assert history[0]["action"] == "UPDATE"
    assert "old_content" in history[0]["content"]
    assert "new_content" in history[0]["content"]
    assert history[0]["content"]["old_content"]["text"] == "原始标注内容"
    assert history[0]["content"]["new_content"]["text"] == "更新后的标注内容"
    
    # 第二条是创建记录
    assert history[1]["action"] == "CREATE"

def test_delete_annotation_with_history(client: TestClient, db: Session):
    """测试删除标注前创建历史记录"""
    # 创建测试用户
    user_data = {
        "email": "test_history_delete@example.com",
        "username": "test_history_delete_user",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id
    
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
    
    # 创建测试文档和任务
    document_data = {
        "filename": "test_history_delete.txt",
        "original_filename": "test_history_delete.txt",
        "file_path": "/tmp/test_history_delete.txt",
        "file_size": 100,
        "file_type": ".txt",
        "uploader_id": user_id
    }
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    task_data = {
        "document_id": document.id,
        "annotator_id": user_id,
        "user_id": user_id,
        "status": TaskStatus.PENDING,
        "title": "删除历史记录测试任务",
        "description": "删除历史记录测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "将被删除的标注内容",
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
    annotation = response.json()
    annotation_id = annotation["id"]
    
    # 先获取历史记录，验证创建记录
    response = client.get(
        f"/api/v1/annotations/{annotation_id}/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    history_before = response.json()
    assert len(history_before) == 1
    assert history_before[0]["action"] == "CREATE"
    
    # 记下历史记录ID，以便删除标注后仍能访问
    history_id = history_before[0]["id"]
    
    # 删除标注
    response = client.delete(
        f"/api/v1/annotations/{annotation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 尝试获取特定历史记录详情
    response = client.get(
        f"/api/v1/annotations/history/{history_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    history_detail = response.json()
    assert history_detail["id"] == history_id
    assert history_detail["action"] == "CREATE"

def test_get_user_history(client: TestClient, db: Session):
    """测试获取用户的操作历史"""
    # 创建测试用户
    user_data = {
        "email": "test_user_history@example.com",
        "username": "test_user_history_user",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id
    
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
    
    # 创建测试文档和任务
    document_data = {
        "filename": "test_user_history.txt",
        "original_filename": "test_user_history.txt",
        "file_path": "/tmp/test_user_history.txt",
        "file_size": 100,
        "file_type": ".txt",
        "uploader_id": user_id
    }
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    task_data = {
        "document_id": document.id,
        "annotator_id": user_id,
        "user_id": user_id,
        "status": TaskStatus.PENDING,
        "title": "用户历史记录测试任务",
        "description": "用户历史记录测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建多个标注
    for i in range(3):
        annotation_data = {
            "task_id": task.id,
            "annotator_id": user_id,
            "annotation_type": AnnotationType.TEXT,
            "content": {
                "text": f"用户历史测试标注内容 {i}",
                "start_offset": i * 10,
                "end_offset": (i + 1) * 10,
                "label": f"测试标签 {i}"
            }
        }
        response = client.post(
            "/api/v1/annotations/",
            json=annotation_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
    
    # 获取用户的操作历史
    response = client.get(
        f"/api/v1/annotations/history/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    user_history = response.json()
    
    # 验证历史记录
    assert len(user_history) >= 3  # 至少有3条创建记录
    for history in user_history:
        assert history["user_id"] == user_id 