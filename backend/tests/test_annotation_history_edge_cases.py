import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.user import create_user
from app.schemas.user import UserCreate
from app.models.document import Document
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate
from app.services.task import create_task
from app.models.annotation import AnnotationType
from app.schemas.annotation import AnnotationCreate
from app.services.annotation import create_annotation
from datetime import datetime, timedelta

def test_history_not_found(client: TestClient, db: Session):
    """测试获取不存在的历史记录"""
    # 创建测试用户
    user_data = {
        "email": "test_history_not_found@example.com",
        "username": "test_history_not_found",
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
    
    # 尝试获取不存在的历史记录
    nonexistent_history_id = 99999
    response = client.get(
        f"/api/v1/annotations/history/{nonexistent_history_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert "历史记录不存在" in response.json()["detail"]

def test_user_history_permission(client: TestClient, db: Session):
    """测试用户历史记录的权限控制"""
    # 创建两个测试用户
    user1_data = {
        "email": "test_user1@example.com",
        "username": "test_user1",
        "password": "testpass123"
    }
    user1 = create_user(db, UserCreate(**user1_data))
    
    user2_data = {
        "email": "test_user2@example.com",
        "username": "test_user2",
        "password": "testpass123"
    }
    user2 = create_user(db, UserCreate(**user2_data))
    
    # 为用户1登录获取token
    login_data = {
        "username": user1_data["email"],
        "password": user1_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    user1_token = response.json()["access_token"]
    
    # 尝试获取用户2的历史记录（应该被拒绝）
    response = client.get(
        f"/api/v1/annotations/history/users/{user2.id}",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 403
    assert "无权执行此操作" in response.json()["detail"]

def test_history_pagination(client: TestClient, db: Session):
    """测试历史记录分页功能"""
    # 创建测试用户
    user_data = {
        "email": "test_history_pagination@example.com",
        "username": "test_history_pagination",
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
        "filename": "test_pagination.txt",
        "original_filename": "test_pagination.txt",
        "file_path": "/tmp/test_pagination.txt",
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
        "title": "分页测试任务",
        "description": "分页测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建多个标注
    for i in range(5):
        annotation_data = {
            "task_id": task.id,
            "annotator_id": user_id,
            "annotation_type": AnnotationType.TEXT,
            "content": {
                "text": f"分页测试标注内容 {i}",
                "start_offset": i * 10,
                "end_offset": (i + 1) * 10,
                "label": f"测试标签 {i}"
            }
        }
        create_annotation(db, annotation_in=AnnotationCreate(**annotation_data))
    
    # 测试历史记录分页功能 (应至少有5条记录)
    # 获取第1页，每页2条
    response = client.get(
        f"/api/v1/annotations/history/users/{user_id}?skip=0&limit=2",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    page1 = response.json()
    assert len(page1) == 2
    
    # 获取第2页，每页2条
    response = client.get(
        f"/api/v1/annotations/history/users/{user_id}?skip=2&limit=2",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    page2 = response.json()
    assert len(page2) == 2
    
    # 确保第1页和第2页的数据不同
    page1_ids = [item["id"] for item in page1]
    page2_ids = [item["id"] for item in page2]
    assert not set(page1_ids).intersection(set(page2_ids))

def test_annotation_history_after_annotation_deleted(client: TestClient, db: Session):
    """测试标注删除后通过历史记录ID获取历史记录"""
    # 创建测试用户
    user_data = {
        "email": "test_history_after_delete@example.com",
        "username": "test_history_after_delete",
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
        "filename": "test_after_delete.txt",
        "original_filename": "test_after_delete.txt",
        "file_path": "/tmp/test_after_delete.txt",
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
        "title": "删除后历史测试任务",
        "description": "删除后历史测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "删除后历史测试标注内容",
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
    
    # 获取历史记录ID
    response = client.get(
        f"/api/v1/annotations/{annotation_id}/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    history = response.json()
    assert len(history) > 0
    history_id = history[0]["id"]
    
    # 创建删除记录并删除标注
    response = client.delete(
        f"/api/v1/annotations/{annotation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 验证可以通过历史记录ID获取历史记录
    response = client.get(
        f"/api/v1/annotations/history/{history_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200 

def test_annotation_update_history_creation(client: TestClient, db: Session):
    """测试标注更新后历史记录创建"""
    # 创建测试用户
    user_data = {
        "email": "test_update_history@example.com",
        "username": "test_update_history",
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
        "filename": "test_update_history.txt",
        "original_filename": "test_update_history.txt",
        "file_path": "/tmp/test_update_history.txt",
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
        "title": "更新历史测试任务",
        "description": "更新历史测试任务描述"
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
    
    # 获取初始历史记录
    response = client.get(
        f"/api/v1/annotations/{annotation_id}/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    initial_history = response.json()
    assert len(initial_history) == 1
    assert initial_history[0]["action"] == "CREATE"
    
    # 更新标注
    update_data = {
        "content": {
            "text": "更新后的标注内容",
            "start_offset": 0,
            "end_offset": 15,
            "label": "更新的标签"
        }
    }
    response = client.put(
        f"/api/v1/annotations/{annotation_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 获取更新后的历史记录
    response = client.get(
        f"/api/v1/annotations/{annotation_id}/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    updated_history = response.json()
    assert len(updated_history) == 2  # 应该有两条记录：创建和更新
    assert updated_history[0]["action"] == "UPDATE"  # 最新的记录应该是更新
    assert updated_history[1]["action"] == "CREATE"  # 较旧的记录应该是创建
    
    # 检查更新历史记录的内容
    assert "更新后的标注内容" in str(updated_history[0]["content"])
    assert "更新的标签" in str(updated_history[0]["content"])

def test_history_date_filter(client: TestClient, db: Session):
    """测试按日期范围筛选历史记录"""
    # 创建测试用户
    user_data = {
        "email": "test_date_filter@example.com",
        "username": "test_date_filter",
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
        "filename": "test_date_filter.txt",
        "original_filename": "test_date_filter.txt",
        "file_path": "/tmp/test_date_filter.txt",
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
        "title": "日期筛选测试任务",
        "description": "日期筛选测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "日期筛选测试内容",
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
    
    # 获取当前日期
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    # 测试日期筛选 - 包含今天的范围（应该有结果）
    start_date = yesterday.isoformat()
    end_date = tomorrow.isoformat()
    response = client.get(
        f"/api/v1/annotations/history/users/{user_id}?start_date={start_date}&end_date={end_date}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    filtered_history = response.json()
    assert len(filtered_history) > 0
    
    # 测试日期筛选 - 过去范围（不应该有结果）
    start_date = (yesterday - timedelta(days=10)).isoformat()
    end_date = yesterday.isoformat()
    response = client.get(
        f"/api/v1/annotations/history/users/{user_id}?start_date={start_date}&end_date={end_date}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    filtered_history = response.json()
    assert len(filtered_history) == 0

def test_history_action_filter(client: TestClient, db: Session):
    """测试按操作类型筛选历史记录"""
    # 创建测试用户
    user_data = {
        "email": "test_action_filter@example.com",
        "username": "test_action_filter",
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
        "filename": "test_action_filter.txt",
        "original_filename": "test_action_filter.txt",
        "file_path": "/tmp/test_action_filter.txt",
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
        "title": "操作筛选测试任务",
        "description": "操作筛选测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    
    # 创建标注
    annotation_data = {
        "task_id": task.id,
        "annotator_id": user_id,
        "annotation_type": AnnotationType.TEXT,
        "content": {
            "text": "操作筛选测试内容",
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
    
    # 更新标注
    update_data = {
        "content": {
            "text": "更新的操作筛选测试内容",
            "start_offset": 0,
            "end_offset": 15,
            "label": "更新的标签"
        }
    }
    response = client.put(
        f"/api/v1/annotations/{annotation_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 测试按操作类型筛选 - CREATE
    response = client.get(
        f"/api/v1/annotations/history/users/{user_id}?action=CREATE",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    create_history = response.json()
    assert len(create_history) > 0
    assert all(item["action"] == "CREATE" for item in create_history)
    
    # 测试按操作类型筛选 - UPDATE
    response = client.get(
        f"/api/v1/annotations/history/users/{user_id}?action=UPDATE",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    update_history = response.json()
    assert len(update_history) > 0
    assert all(item["action"] == "UPDATE" for item in update_history)

def test_history_sorting(client: TestClient, db: Session):
    """测试历史记录排序功能"""
    # 创建测试用户
    user_data = {
        "email": "test_sorting@example.com",
        "username": "test_sorting",
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
        "filename": "test_sorting.txt",
        "original_filename": "test_sorting.txt",
        "file_path": "/tmp/test_sorting.txt",
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
        "title": "排序测试任务",
        "description": "排序测试任务描述"
    }
    task = create_task(db, task_in=TaskCreate(**task_data))
    task_id = task.id  # 获取任务ID并保存
    
    # 创建多个标注以生成多条历史记录
    annotation_ids = []
    for i in range(3):
        annotation_data = {
            "task_id": task_id,  # 使用保存的任务ID
            "annotator_id": user_id,
            "annotation_type": AnnotationType.TEXT,
            "content": {
                "text": f"排序测试内容 {i}",
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
        annotation = response.json()
        annotation_ids.append(annotation["id"])
    
    # 测试默认排序（应该是按创建时间降序）
    response = client.get(
        f"/api/v1/annotations/history/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    default_sorted = response.json()
    assert len(default_sorted) >= 3
    
    # 确认默认排序是按时间降序（最新的在前面）
    for i in range(len(default_sorted) - 1):
        assert default_sorted[i]["created_at"] >= default_sorted[i + 1]["created_at"]
    
    # 测试升序排序
    response = client.get(
        f"/api/v1/annotations/history/users/{user_id}?order=asc",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    asc_sorted = response.json()
    assert len(asc_sorted) >= 3
    
    # 确认升序排序是按时间升序（最旧的在前面）
    for i in range(len(asc_sorted) - 1):
        assert asc_sorted[i]["created_at"] <= asc_sorted[i + 1]["created_at"] 