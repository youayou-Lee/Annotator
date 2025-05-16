import os
import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from sqlalchemy.orm import Session

# 测试客户端
client = TestClient(app)

# 模拟认证用户
@pytest.fixture
def authenticated_client(db: Session):
    # 创建测试用户
    test_user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # 模拟认证令牌
    def override_get_current_user():
        return test_user
    
    # 替换依赖项
    from app.core.security import get_current_user
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    yield client
    
    # 清理
    app.dependency_overrides = {}
    db.delete(test_user)
    db.commit()

# 测试文件上传 - 有效文件
def test_upload_valid_document(authenticated_client):
    # 创建一个模拟的PDF文件
    file_content = b"%PDF-1.5\nTest PDF content"
    file = io.BytesIO(file_content)
    
    response = authenticated_client.post(
        "/api/v1/documents/",
        files={"file": ("test.pdf", file, "application/pdf")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["filename"] == "test.pdf"
    assert data["status"] == "PENDING"

# 测试文件上传 - 无效文件类型
def test_upload_invalid_file_type(authenticated_client):
    # 创建一个不支持的文件类型
    file_content = b"Test content"
    file = io.BytesIO(file_content)
    
    response = authenticated_client.post(
        "/api/v1/documents/",
        files={"file": ("test.exe", file, "application/octet-stream")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "不支持的文件类型" in data["detail"]

# 测试文件上传 - 文件大小超限
def test_upload_file_size_exceeded(authenticated_client):
    # 临时修改最大上传大小设置为非常小的值
    original_max_size = settings.MAX_UPLOAD_SIZE
    settings.MAX_UPLOAD_SIZE = 10  # 10字节
    
    # 创建一个大于限制的文件
    file_content = b"%PDF-1.5\n" + b"A" * 100  # 超过10字节
    file = io.BytesIO(file_content)
    
    response = authenticated_client.post(
        "/api/v1/documents/",
        files={"file": ("test.pdf", file, "application/pdf")}
    )
    
    # 恢复原始设置
    settings.MAX_UPLOAD_SIZE = original_max_size
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "文件大小超过限制" in data["detail"]

# 测试文件上传 - 空文件
def test_upload_empty_file(authenticated_client):
    # 创建一个空文件
    file = io.BytesIO(b"")
    
    response = authenticated_client.post(
        "/api/v1/documents/",
        files={"file": ("test.pdf", file, "application/pdf")}
    )
    
    # 空文件应该可以上传，但可能会在后续处理中被标记为无效
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["filename"] == "test.pdf"

# 测试文件上传 - 文件指针重置问题
def test_file_pointer_reset(authenticated_client):
    # 创建一个模拟的PDF文件
    file_content = b"%PDF-1.5\nTest PDF content with specific marker ABCDEF"
    file = io.BytesIO(file_content)
    
    response = authenticated_client.post(
        "/api/v1/documents/",
        files={"file": ("test_pointer.pdf", file, "application/pdf")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    
    # 检查文件是否被正确保存（包含所有内容）
    document_id = data["id"]
    file_path = os.path.join(settings.UPLOAD_DIR, data["file_path"])
    
    # 确认文件存在并且内容完整
    assert os.path.exists(file_path)
    with open(file_path, "rb") as f:
        saved_content = f.read()
    
    assert b"ABCDEF" in saved_content
    assert len(saved_content) == len(file_content)