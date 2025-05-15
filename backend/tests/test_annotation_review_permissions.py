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

def test_reviewer_update_own_review(client: TestClient, db: Session):
    """测试审核人更新自己的审核记录"""
    # 创建测试用户（标注者和审核者）
    annotator_data = {
        "email": "annotator_permissions@example.com",
        "username": "annotator_permissions",
        "password": "testpass123"
    }
    annotator = create_user(db, UserCreate(**annotator_data))
    
    reviewer_data = {
        "email": "reviewer_permissions@example.com",
        "username": "reviewer_permissions",
        "password": "testpass123"
    }
    reviewer = create_user(db, UserCreate(**reviewer_data))
    
    # 登录审核者获取 token
    login_data = {
        "username": reviewer_data["email"],
        "password": reviewer_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    reviewer_token = response.json()["access_token"]
    
    # 创建测试文档和任务
    document_data = {
        "filename": "test_permissions.txt",
        "original_filename": "test_permissions.txt",
        "file_path": "/tmp/test_permissions.txt",
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
        "title": "权限测试任务",
        "description": "权限测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": annotator.id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "权限测试标注内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 审核者创建审核记录
    review_data = {
        "annotation_id": annotation.id,
        "reviewer_id": reviewer.id,
        "status": AnnotationStatus.REJECTED,
        "comment": "初始审核意见"
    }
    response = client.post(
        f"/api/v1/annotations/{annotation.id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )
    assert response.status_code == 200
    review = response.json()
    
    # 审核者更新自己的审核记录
    update_data = {
        "status": AnnotationStatus.APPROVED,
        "comment": "修改后的审核意见"
    }
    response = client.put(
        f"/api/v1/annotations/reviews/{review['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )
    assert response.status_code == 200
    updated_review = response.json()
    assert updated_review["status"] == AnnotationStatus.APPROVED
    assert updated_review["comment"] == "修改后的审核意见"

def test_annotator_cannot_update_review(client: TestClient, db: Session):
    """测试标注者无法更新审核记录"""
    # 创建测试用户（标注者和审核者）
    annotator_data = {
        "email": "annotator_cannot_update@example.com",
        "username": "annotator_cannot_update",
        "password": "testpass123"
    }
    annotator = create_user(db, UserCreate(**annotator_data))
    
    reviewer_data = {
        "email": "reviewer_cannot_update@example.com",
        "username": "reviewer_cannot_update",
        "password": "testpass123"
    }
    reviewer = create_user(db, UserCreate(**reviewer_data))
    
    # 登录获取 token
    annotator_login_data = {
        "username": annotator_data["email"],
        "password": annotator_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=annotator_login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    annotator_token = response.json()["access_token"]
    
    reviewer_login_data = {
        "username": reviewer_data["email"],
        "password": reviewer_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=reviewer_login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    reviewer_token = response.json()["access_token"]
    
    # 创建测试文档和任务
    document_data = {
        "filename": "test_annotator_cannot_update.txt",
        "original_filename": "test_annotator_cannot_update.txt",
        "file_path": "/tmp/test_annotator_cannot_update.txt",
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
        "title": "标注者无法更新测试任务",
        "description": "标注者无法更新测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": annotator.id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "标注者无法更新测试内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 审核者创建审核记录
    review_data = {
        "annotation_id": annotation.id,
        "reviewer_id": reviewer.id,
        "status": AnnotationStatus.REJECTED,
        "comment": "初始审核意见"
    }
    response = client.post(
        f"/api/v1/annotations/{annotation.id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )
    assert response.status_code == 200
    review = response.json()
    
    # 标注者尝试更新审核记录（应该失败）
    update_data = {
        "status": AnnotationStatus.APPROVED,
        "comment": "标注者尝试修改审核意见"
    }
    response = client.put(
        f"/api/v1/annotations/reviews/{review['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {annotator_token}"}
    )
    assert response.status_code == 403
    assert "无权执行此操作" in response.json()["detail"]

def test_superuser_can_update_any_review(client: TestClient, db: Session):
    """测试超级用户可以更新任何审核记录"""
    # 创建测试用户（标注者、审核者和超级用户）
    annotator_data = {
        "email": "annotator_superuser@example.com",
        "username": "annotator_superuser",
        "password": "testpass123"
    }
    annotator = create_user(db, UserCreate(**annotator_data))
    
    reviewer_data = {
        "email": "reviewer_superuser@example.com",
        "username": "reviewer_superuser",
        "password": "testpass123"
    }
    reviewer = create_user(db, UserCreate(**reviewer_data))
    
    superuser_data = {
        "email": "superuser@example.com",
        "username": "superuser",
        "password": "testpass123",
        "is_superuser": True
    }
    # 在UserCreate中设置is_superuser字段
    superuser = create_user(db, UserCreate(**superuser_data))
    
    # 登录获取 token
    superuser_login_data = {
        "username": superuser_data["email"],
        "password": superuser_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=superuser_login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    superuser_token = response.json()["access_token"]
    
    reviewer_login_data = {
        "username": reviewer_data["email"],
        "password": reviewer_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=reviewer_login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    reviewer_token = response.json()["access_token"]
    
    # 创建测试文档和任务
    document_data = {
        "filename": "test_superuser.txt",
        "original_filename": "test_superuser.txt",
        "file_path": "/tmp/test_superuser.txt",
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
        "title": "超级用户权限测试任务",
        "description": "超级用户权限测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": annotator.id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "超级用户权限测试内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 审核者创建审核记录
    review_data = {
        "annotation_id": annotation.id,
        "reviewer_id": reviewer.id,
        "status": AnnotationStatus.REJECTED,
        "comment": "初始审核意见"
    }
    response = client.post(
        f"/api/v1/annotations/{annotation.id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )
    assert response.status_code == 200
    review = response.json()
    
    # 超级用户更新审核记录
    update_data = {
        "status": AnnotationStatus.APPROVED,
        "comment": "超级用户修改审核意见"
    }
    response = client.put(
        f"/api/v1/annotations/reviews/{review['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    assert response.status_code == 200
    updated_review = response.json()
    assert updated_review["status"] == AnnotationStatus.APPROVED
    assert updated_review["comment"] == "超级用户修改审核意见"

def test_reviewer_delete_own_review(client: TestClient, db: Session):
    """测试审核人删除自己的审核记录"""
    # 创建测试用户
    annotator_data = {
        "email": "annotator_delete@example.com",
        "username": "annotator_delete",
        "password": "testpass123"
    }
    annotator = create_user(db, UserCreate(**annotator_data))
    
    reviewer_data = {
        "email": "reviewer_delete@example.com",
        "username": "reviewer_delete",
        "password": "testpass123"
    }
    reviewer = create_user(db, UserCreate(**reviewer_data))
    
    # 登录审核者获取 token
    login_data = {
        "username": reviewer_data["email"],
        "password": reviewer_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    reviewer_token = response.json()["access_token"]
    
    # 创建测试文档和任务
    document_data = {
        "filename": "test_delete_own.txt",
        "original_filename": "test_delete_own.txt",
        "file_path": "/tmp/test_delete_own.txt",
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
        "title": "删除自己审核记录测试任务",
        "description": "删除自己审核记录测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": annotator.id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "删除自己审核记录测试内容",
            "start_offset": 0,
            "end_offset": 10,
            "label": "测试标签"
        }
    }
    annotation = create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 审核者创建审核记录
    review_data = {
        "annotation_id": annotation.id,
        "reviewer_id": reviewer.id,
        "status": AnnotationStatus.APPROVED,
        "comment": "审核通过"
    }
    response = client.post(
        f"/api/v1/annotations/{annotation.id}/review",
        json=review_data,
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )
    assert response.status_code == 200
    review = response.json()
    
    # 审核者删除自己的审核记录
    response = client.delete(
        f"/api/v1/annotations/reviews/{review['id']}",
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )
    assert response.status_code == 200
    deleted_review = response.json()
    assert deleted_review["id"] == review["id"]
    
    # 验证审核记录已被删除
    response = client.get(
        f"/api/v1/annotations/reviews/{review['id']}",
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )
    assert response.status_code == 404 