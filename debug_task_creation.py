#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.app.core.storage import StorageManager
from backend.app.models.task import TaskCreate

def debug_task_creation():
    """调试任务创建过程"""
    
    storage = StorageManager()
    
    print("1. 测试基本任务创建（不包含模板）...")
    try:
        task_create = TaskCreate(
            name="测试任务",
            description="这是一个测试任务",
            documents=["public_files/documents/test_doc1.json"]
        )
        
        print("TaskCreate对象创建成功")
        print(f"TaskCreate内容: {task_create}")
        
        # 尝试序列化
        try:
            task_dict = task_create.model_dump()
            print("TaskCreate序列化成功")
        except AttributeError:
            task_dict = task_create.dict()
            print("TaskCreate序列化成功（使用dict方法）")
        except Exception as e:
            print(f"TaskCreate序列化失败: {e}")
            return
        
        print("2. 测试任务创建...")
        task = storage.create_task(task_create, "user_0b072cec")
        print("任务创建成功!")
        print(f"任务ID: {task.id}")
        
    except Exception as e:
        print(f"任务创建失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. 测试包含模板的任务创建...")
    try:
        task_create_with_template = TaskCreate(
            name="测试任务（包含模板）",
            description="这是一个包含模板的测试任务",
            documents=["public_files/documents/test_doc1.json"],
            template_path="public_files/templates/test_template.py"
        )
        
        print("TaskCreate对象创建成功")
        
        print("4. 测试模板解析...")
        template_info = storage._parse_template_file("public_files/templates/test_template.py")
        print(f"模板解析结果: {template_info}")
        
        print("5. 测试包含模板的任务创建...")
        task_with_template = storage.create_task(task_create_with_template, "user_0b072cec")
        print("包含模板的任务创建成功!")
        print(f"任务ID: {task_with_template.id}")
        
    except Exception as e:
        print(f"包含模板的任务创建失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_task_creation() 