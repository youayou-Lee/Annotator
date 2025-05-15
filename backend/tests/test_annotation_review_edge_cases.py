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
from app.services.annotation_review import create_annotation_review, get_annotation_review
from app.schemas.annotation import AnnotationCreate, AnnotationReviewCreate
from app.models.document import Document
from app.models.user import User
from app.models.task import Task
from app.models.annotation import Annotation

def test_create_review_nonexistent_annotation(client: TestClient, db: Session):
    """测试对不存在的标注创建审核"""
    # 创建测试用户
    user_data = {
        "email": "test_nonexistent@example.com",
        "username": "test_nonexistent_user",
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
    
    # 尝试对不存在的标注创建审核
    nonexistent_annotation_id = 99999
    review_data = {
        "annotation_id": nonexistent_annotation_id,
        "reviewer_id": user_id,
        "status": AnnotationStatus.APPROVED,
        "comment": "对不存在标注的审核"
    }
    response = client.post(
        f"/api/v1/annotations/{nonexistent_annotation_id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert "标注不存在" in response.json()["detail"]

def test_create_review_unauthorized(client: TestClient, db: Session):
    """测试未授权用户创建审核"""
    # 创建两个测试用户：标注者和其他用户
    annotator_data = {
        "email": "annotator@example.com",
        "username": "annotator_user",
        "password": "testpass123"
    }
    annotator = create_user(db, UserCreate(**annotator_data))
    
    other_user_data = {
        "email": "other_user@example.com",
        "username": "other_user",
        "password": "testpass123"
    }
    other_user = create_user(db, UserCreate(**other_user_data))
    
    # 登录获取 token
    login_data = {
        "username": other_user_data["email"],
        "password": other_user_data["password"]
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
        "filename": "test_unauthorized.txt",
        "original_filename": "test_unauthorized.txt",
        "file_path": "/tmp/test_unauthorized.txt",
        "file_size": 100,
        "file_type": ".txt",
        "uploader_id": annotator.id
    }
    document = Document(**document_data)
    db.add(document)
    db.commit()
    db.refresh(document)
    
    task_data = {
        "document_id": document.id,
        "annotator_id": annotator.id,
        "user_id": annotator.id,
        "status": TaskStatus.PENDING,
        "title": "未授权测试任务",
        "description": "未授权测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": annotator.id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "未授权测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 尝试以other_user身份创建以annotator为reviewer的审核
    review_data = {
        "annotation_id": annotation.id,
        "reviewer_id": annotator.id,  # 使用annotator作为reviewer_id，而非当前登录的other_user
        "status": AnnotationStatus.APPROVED,
        "comment": "未授权审核"
    }
    response = client.post(
        f"/api/v1/annotations/{annotation.id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "无权执行此操作" in response.json()["detail"]

def test_update_nonexistent_review(client: TestClient, db: Session):
    """测试更新不存在的审核记录"""
    # 创建测试用户
    user_data = {
        "email": "test_update_nonexistent@example.com",
        "username": "test_update_nonexistent_user",
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
    
    # 尝试更新不存在的审核记录
    nonexistent_review_id = 99999
    update_data = {
        "status": AnnotationStatus.APPROVED,
        "comment": "更新不存在的审核记录"
    }
    response = client.put(
        f"/api/v1/annotations/reviews/{nonexistent_review_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert "审核记录不存在" in response.json()["detail"]

def test_delete_nonexistent_review(client: TestClient, db: Session):
    """测试删除不存在的审核记录"""
    # 创建测试用户
    user_data = {
        "email": "test_delete_nonexistent@example.com",
        "username": "test_delete_nonexistent_user",
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
    
    # 尝试删除不存在的审核记录
    nonexistent_review_id = 99999
    response = client.delete(
        f"/api/v1/annotations/reviews/{nonexistent_review_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert "审核记录不存在" in response.json()["detail"]

def test_mismatched_annotation_id(client: TestClient, db: Session):
    """测试提交审核时标注ID不匹配的情况"""
    # 创建测试用户
    user_data = {
        "email": "test_mismatched@example.com",
        "username": "test_mismatched_user",
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
        "filename": "test_mismatched.txt",
        "original_filename": "test_mismatched.txt",
        "file_path": "/tmp/test_mismatched.txt",
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
        "title": "ID不匹配测试任务",
        "description": "ID不匹配测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "ID不匹配测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    
    # URL中的annotation_id与请求body中的annotation_id不匹配
    mismatched_annotation_id = annotation.id + 1
    review_data = {
        "annotation_id": mismatched_annotation_id,  # 不匹配URL中的annotation.id
        "reviewer_id": user_id,
        "status": AnnotationStatus.APPROVED,
        "comment": "ID不匹配审核"
    }
    response = client.post(
        f"/api/v1/annotations/{annotation.id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "标注ID不匹配" in response.json()["detail"] 