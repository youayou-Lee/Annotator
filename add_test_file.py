#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加测试文件到文件系统
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime

# 添加后端路径到Python路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.storage import StorageManager
from app.models.file import FileInfo, FileType

def add_test_file():
    """添加测试文件到文件系统"""
    print("=== 添加测试文件到文件系统 ===\n")
    
    storage = StorageManager()
    
    # 检查文件是否存在
    test_file_path = Path("backend/data/public_files/documents/test_invalid_data.json")
    if not test_file_path.exists():
        print(f"❌ 测试文件不存在: {test_file_path}")
        return False
    
    # 创建文件信息
    file_info = FileInfo(
        id=f"file_{uuid.uuid4().hex[:8]}",
        filename="test_invalid_data.json",
        file_path="public_files\\documents\\test_invalid_data.json",
        file_type=FileType.DOCUMENT,
        file_size=test_file_path.stat().st_size,
        uploader_id="user_3101cf00",  # 使用admin用户ID
        uploaded_at=datetime.now()
    )
    
    # 保存文件信息
    try:
        storage.save_file_info(file_info)
        print(f"✅ 已添加测试文件: {file_info.filename}")
        print(f"   文件ID: {file_info.id}")
        print(f"   文件路径: {file_info.file_path}")
        print(f"   文件大小: {file_info.file_size} bytes")
        
        # 验证是否保存成功
        saved_files = storage.get_all_files(FileType.DOCUMENT)
        for f in saved_files:
            if f.filename == "test_invalid_data.json":
                print(f"✅ 文件保存验证成功")
                return True
        
        print("❌ 文件保存验证失败")
        return False
        
    except Exception as e:
        print(f"❌ 保存文件信息失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    add_test_file() 