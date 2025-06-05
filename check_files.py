#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查文件路径格式
"""

import sys
from pathlib import Path

# 添加后端路径到Python路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.storage import StorageManager
from app.models.file import FileType

def check_files():
    """检查文件路径格式"""
    print("=== 检查文件路径格式 ===\n")
    
    storage = StorageManager()
    
    # 检查文档文件
    docs = storage.get_all_files(FileType.DOCUMENT)
    print("文档文件:")
    for doc in docs:
        print(f"  ID: {doc.id}")
        print(f"  路径: {doc.file_path}")
        print(f"  文件名: {doc.filename}")
        print()
    
    # 检查模板文件
    templates = storage.get_all_files(FileType.TEMPLATE)
    print("模板文件:")
    for template in templates:
        print(f"  ID: {template.id}")
        print(f"  路径: {template.file_path}")
        print(f"  文件名: {template.filename}")
        print()

if __name__ == "__main__":
    check_files() 