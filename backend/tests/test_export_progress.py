import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.user import create_user
from app.schemas.user import UserCreate
from app.models.document import Document, DocumentStatus
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate
from app.services.task import create_task
from app.models.annotation import Annotation, AnnotationType
from app.schemas.annotation import AnnotationCreate
from app.services.annotation import create_annotation
from app.models.export_task import ExportStatus, ExportFormat
from app.schemas.export_task import ExportTaskCreate
import time
import os
from app.core.config import settings

def create_test_document(db: Session, uploader_id: int) -> Document:
    """创建测试文档"""
    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 创建测试文件
    test_filename = f"test_doc_{time.time()}.json"
    file_path = os.path.join(settings.UPLOAD_DIR, test_filename)
    
    # 写入一些测试数据
    with open(file_path, "w", encoding="utf-8") as f:
        f.write('{"test": "data"}')
    
    # 创建文档记录
    db_document = Document(
        filename=test_filename,
        original_filename=test_filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        file_type=".json",
        uploader_id=uploader_id,
        status=DocumentStatus.COMPLETED
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def test_create_export_task(client: TestClient, db: Session):
    """测试创建导出任务"""
    # 创建测试用户
    user_data = {
        "email": "test_export@example.com",
        "username": "test_export_user",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id  # 保存ID而不是对象
    
    # 创建测试文档
    document = create_test_document(db, user_id)
    
    # 登录获取token
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
    
    # 创建测试任务
    task_data = {
        "title": "测试导出任务",
        "description": "测试导出功能",
        "annotator_id": user_id,
        "document_id": document.id,
        "status": TaskStatus.IN_PROGRESS,
        "user_id": user_id
    }
    task = create_task(db=db, task_in=TaskCreate(**task_data))
    task_id = task.id  # 保存ID而不是对象
    
    # 创建测试标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {"text": "测试标注内容"}
    }
    annotation = create_annotation(db=db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 创建导出任务
    export_task_data = {
        "user_id": user_id,
        "description": "测试导出",
        "format": ExportFormat.JSON,
        "task_ids": [task_id]
    }
    
    response = client.post(
        "/api/v1/exports/",
        json=export_task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["user_id"] == user_id
    assert result["status"] == ExportStatus.PENDING
    assert result["progress"] == 0.0
    
    # 保存导出任务ID
    export_task_id = result["id"]
    
    # 等待一段时间，让后台导出任务开始处理
    time.sleep(1)
    
    # 查询导出任务状态
    response = client.get(
        f"/api/v1/exports/{export_task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    result = response.json()
    
    # 此时任务状态应该是处理中或已完成
    assert result["status"] in [ExportStatus.PROCESSING, ExportStatus.COMPLETED]
    
    # 如果任务已经完成，检查进度是否为100%
    if result["status"] == ExportStatus.COMPLETED:
        assert result["progress"] == 100.0
        assert result["file_path"] is not None
    
    # 等待任务完成
    for _ in range(10):  # 最多等待10秒
        response = client.get(
            f"/api/v1/exports/{export_task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        result = response.json()
        if result["status"] == ExportStatus.COMPLETED:
            break
        time.sleep(1)
    
    # 检查任务是否已完成
    assert result["status"] == ExportStatus.COMPLETED
    assert result["progress"] == 100.0
    assert result["file_path"] is not None

def test_get_export_tasks(client: TestClient, db: Session):
    """测试获取导出任务列表"""
    # 创建测试用户
    user_data = {
        "email": "test_export_list@example.com",
        "username": "test_export_list_user",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id  # 保存ID而不是对象
    
    # 创建测试文档
    document = create_test_document(db, user_id)
    
    # 登录获取token
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
    
    # 创建测试任务
    task_data = {
        "title": "测试导出任务列表",
        "description": "测试导出功能",
        "annotator_id": user_id,
        "document_id": document.id,
        "status": TaskStatus.IN_PROGRESS,
        "user_id": user_id
    }
    task = create_task(db=db, task_in=TaskCreate(**task_data))
    task_id = task.id  # 保存ID而不是对象
    
    # 创建测试标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {"text": "测试标注内容"}
    }
    annotation = create_annotation(db=db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 创建导出任务
    export_task_data = {
        "user_id": user_id,
        "description": "测试导出任务列表",
        "format": ExportFormat.JSON,
        "task_ids": [task_id]
    }
    
    response = client.post(
        "/api/v1/exports/",
        json=export_task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    export_task_id = response.json()["id"]
    
    # 等待导出任务处理
    time.sleep(2)
    
    # 获取导出任务列表
    response = client.get(
        "/api/v1/exports/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert len(result) >= 1  # 至少有我们刚刚创建的1个任务
    
    # 等待任务完成
    for _ in range(10):  # 最多等待10秒
        response = client.get(
            f"/api/v1/exports/{export_task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        result = response.json()
        if result["status"] == ExportStatus.COMPLETED:
            break
        time.sleep(1)
    
    # 根据状态筛选
    response = client.get(
        f"/api/v1/exports/?status={ExportStatus.COMPLETED}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    completed_tasks = response.json()
    
    # 所有已完成任务的进度应该是100%
    for task in completed_tasks:
        assert task["status"] == ExportStatus.COMPLETED
        assert task["progress"] == 100.0

def test_download_export_file(client: TestClient, db: Session):
    """测试下载导出文件"""
    # 创建测试用户
    user_data = {
        "email": "test_export_download@example.com",
        "username": "test_export_download_user",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id  # 保存ID而不是对象
    
    # 创建测试文档
    document = create_test_document(db, user_id)
    
    # 登录获取token
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
    
    # 创建测试任务
    task_data = {
        "title": "测试导出下载",
        "description": "测试导出功能",
        "annotator_id": user_id,
        "document_id": document.id,
        "status": TaskStatus.IN_PROGRESS,
        "user_id": user_id
    }
    task = create_task(db=db, task_in=TaskCreate(**task_data))
    task_id = task.id  # 保存ID而不是对象
    
    # 创建测试标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {"text": "测试标注内容"}
    }
    annotation = create_annotation(db=db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 创建导出任务
    export_task_data = {
        "user_id": user_id,
        "description": "测试导出下载",
        "format": ExportFormat.JSON,
        "task_ids": [task_id]
    }
    
    response = client.post(
        "/api/v1/exports/",
        json=export_task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    export_task_id = response.json()["id"]
    
    # 等待导出任务完成
    for _ in range(10):  # 最多等待10秒
        response = client.get(
            f"/api/v1/exports/{export_task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        result = response.json()
        if result["status"] == ExportStatus.COMPLETED:
            break
        time.sleep(1)
    
    # 尝试下载文件
    response = client.get(
        f"/api/v1/exports/{export_task_id}/download",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 检查是否成功
    assert response.status_code == 200
    assert "application/octet-stream" in response.headers["content-type"]
    
    # 检查文件内容
    assert len(response.content) > 0  # 文件不为空

def test_delete_export_task(client: TestClient, db: Session):
    """测试删除导出任务"""
    # 创建测试用户
    user_data = {
        "email": "test_export_delete@example.com",
        "username": "test_export_delete_user",
        "password": "testpass123"
    }
    user = create_user(db, UserCreate(**user_data))
    user_id = user.id  # 保存ID而不是对象
    
    # 创建测试文档
    document = create_test_document(db, user_id)
    
    # 登录获取token
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
    
    # 创建测试任务
    task_data = {
        "title": "测试导出删除",
        "description": "测试导出功能",
        "annotator_id": user_id,
        "document_id": document.id,
        "status": TaskStatus.IN_PROGRESS,
        "user_id": user_id
    }
    task = create_task(db=db, task_in=TaskCreate(**task_data))
    task_id = task.id  # 保存ID而不是对象
    
    # 创建测试标注
    annotation_data = {
        "task_id": task_id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {"text": "测试标注内容"}
    }
    annotation = create_annotation(db=db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 创建导出任务
    export_task_data = {
        "user_id": user_id,
        "description": "测试导出删除",
        "format": ExportFormat.JSON,
        "task_ids": [task_id]
    }
    
    response = client.post(
        "/api/v1/exports/",
        json=export_task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    export_task_id = response.json()["id"]
    
    # 等待导出任务完成
    for _ in range(10):  # 最多等待10秒
        response = client.get(
            f"/api/v1/exports/{export_task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        result = response.json()
        if result["status"] == ExportStatus.COMPLETED:
            break
        time.sleep(1)
    
    # 删除导出任务
    response = client.delete(
        f"/api/v1/exports/{export_task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    # 尝试再次获取已删除的导出任务
    response = client.get(
        f"/api/v1/exports/{export_task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404  # 应该返回404 Not Found 