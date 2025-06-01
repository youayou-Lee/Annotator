import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    app_name: str = "文书标注系统"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 安全配置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 文件存储配置
    data_dir: str = "data"
    upload_dir: str = "data/uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    # 允许的文件类型
    allowed_document_extensions: list = [".json", ".jsonl"]
    allowed_template_extensions: list = [".py"]
    
    # CORS配置
    cors_origins: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()

# 确保数据目录存在
def ensure_data_directories():
    """确保所有必要的数据目录存在"""
    directories = [
        settings.data_dir,
        f"{settings.data_dir}/users",
        f"{settings.data_dir}/public_files",
        f"{settings.data_dir}/public_files/documents",
        f"{settings.data_dir}/public_files/templates",
        f"{settings.data_dir}/public_files/exports",
        f"{settings.data_dir}/tasks",
        f"{settings.data_dir}/uploads"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True) 