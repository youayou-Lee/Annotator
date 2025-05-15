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
from app.core.config import settings

def test_create_annotation_review(client: TestClient, db: Session):
    """测试创建标注审核"""
    # 创建测试用户
    user_data = {
        "email": "test_review@example.com",
        "username": "test_reviewer",
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
        "filename": "test_review.txt",
        "original_filename": "test_review.txt",
        "file_path": "/tmp/test_review.txt",
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
        "title": "审核测试任务",
        "description": "审核测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    task_id = task.id
    
    # 创建标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "测试审核标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    annotation_id = annotation.id
    
    # 创建审核
    review_data = {
        "annotation_id": annotation_id,
        "reviewer_id": user_id,
        "status": AnnotationStatus.APPROVED,
        "comment": "通过审核"
    }
    response = client.post(
        f"/api/v1/annotations/{annotation_id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["annotation_id"] == annotation_id
    assert data["reviewer_id"] == user_id
    assert data["status"] == AnnotationStatus.APPROVED
    assert data["comment"] == "通过审核"
    
    # 验证标注状态已更新
    updated_annotation = client.get(
        f"/api/v1/annotations/{annotation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert updated_annotation.status_code == 200
    annotation_data = updated_annotation.json()
    assert annotation_data["status"] == AnnotationStatus.APPROVED
    assert annotation_data["reviewer_id"] == user_id

def test_get_annotation_reviews(client: TestClient, db: Session):
    """测试获取标注的审核记录"""
    # 创建测试用户
    user_data = {
        "email": "test_get_reviews@example.com",
        "username": "test_get_reviewer",
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
        "filename": "test_get_reviews.txt",
        "original_filename": "test_get_reviews.txt",
        "file_path": "/tmp/test_get_reviews.txt",
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
        "title": "获取审核测试任务",
        "description": "获取审核测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    task_id = task.id
    
    # 创建标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "获取审核测试标注内容",
            "start_offset": 0,
            "end_offset": 15,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    annotation_id = annotation.id
    
    # 创建第一个审核
    review_data1 = {
        "annotation_id": annotation_id,
        "reviewer_id": user_id,
        "status": AnnotationStatus.REJECTED,
        "comment": "需要修改"
    }
    review1 = create_annotation_review(db, review_in=AnnotationReviewCreate(**review_data1))
    
    # 创建第二个审核
    review_data2 = {
        "annotation_id": annotation_id,
        "reviewer_id": user_id,
        "status": AnnotationStatus.APPROVED,
        "comment": "修改后通过"
    }
    review2 = create_annotation_review(db, review_in=AnnotationReviewCreate(**review_data2))
    
    # 获取审核记录列表
    response = client.get(
        f"/api/v1/annotations/{annotation_id}/reviews",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) == 2
    
    # 验证顺序和内容
    assert reviews[0]["comment"] == "修改后通过"
    assert reviews[1]["comment"] == "需要修改"

def test_update_annotation_review(client: TestClient, db: Session):
    """测试更新标注审核"""
    # 创建测试用户
    user_data = {
        "email": "test_update_review@example.com",
        "username": "test_update_reviewer",
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
        "filename": "test_update_review.txt",
        "original_filename": "test_update_review.txt",
        "file_path": "/tmp/test_update_review.txt",
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
        "title": "更新审核测试任务",
        "description": "更新审核测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "更新审核测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    annotation_id = annotation.id  # 存储标注ID以供后续使用
    
    # 创建审核
    review_data = {
        "annotation_id": annotation_id,
        "reviewer_id": user_id,
        "status": AnnotationStatus.REJECTED,
        "comment": "初始审核意见"
    }
    response = client.post(
        f"/api/v1/annotations/{annotation_id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    review = response.json()
    review_id = review["id"]
    
    # 更新审核意见
    update_data = {
        "status": AnnotationStatus.APPROVED,
        "comment": "更新后的审核意见"
    }
    response = client.put(
        f"/api/v1/annotations/reviews/{review_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    updated_review = response.json()
    assert updated_review["status"] == AnnotationStatus.APPROVED
    assert updated_review["comment"] == "更新后的审核意见"
    
    # 使用API获取标注状态，避免使用已分离的实例
    response = client.get(
        f"/api/v1/annotations/{annotation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    annotation_data = response.json()
    assert annotation_data["status"] == AnnotationStatus.APPROVED

def test_delete_annotation_review(client: TestClient, db: Session):
    """测试删除标注审核"""
    # 创建测试用户
    user_data = {
        "email": "test_delete_review@example.com",
        "username": "test_delete_reviewer",
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
        "filename": "test_delete_review.txt",
        "original_filename": "test_delete_review.txt",
        "file_path": "/tmp/test_delete_review.txt",
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
        "title": "删除审核测试任务",
        "description": "删除审核测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "删除审核测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 创建审核
    review_data = {
        "annotation_id": annotation.id,
        "reviewer_id": user_id,
        "status": AnnotationStatus.APPROVED,
        "comment": "准备删除的审核"
    }
    response = client.post(
        f"/api/v1/annotations/{annotation.id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    review = response.json()
    review_id = review["id"]
    
    # 删除审核记录
    response = client.delete(
        f"/api/v1/annotations/reviews/{review_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    deleted_review = response.json()
    assert deleted_review["id"] == review_id
    
    # 验证审核记录已被删除
    response = client.get(
        f"/api/v1/annotations/reviews/{review_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404 