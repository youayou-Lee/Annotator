#!/usr/bin/env python3
"""
创建测试任务来验证保存功能
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

def create_test_task():
    """创建一个简单的测试任务"""
    
    # 生成任务ID和文档ID
    task_id = f"test_save_{uuid.uuid4().hex[:8]}"
    document_id = f"doc_{uuid.uuid4().hex[:8]}"
    
    print(f"📝 创建测试任务: {task_id}")
    print(f"📄 创建测试文档: {document_id}")
    
    # 1. 创建测试文档数据
    test_document = {
        "title": "测试文档标题",
        "content": "这是一个测试文档的内容",
        "type": "test",
        "metadata": {
            "author": "测试作者",
            "created_date": "2024-01-01"
        },
        "analysis": {
            "topic": "",  # 待标注字段
            "keywords": [],  # 待标注字段
            "summary": ""  # 待标注字段
        }
    }
    
    # 2. 创建简单的模板配置
    template_config = {
        "template_name": "测试标注模板",
        "version": "1.0",
        "fields": [
            {
                "path": "analysis.topic",
                "field_type": "str",
                "required": True,
                "description": "文档主题",
                "constraints": {
                    "is_annotation": True
                }
            },
            {
                "path": "analysis.keywords",
                "field_type": "array",
                "required": False,
                "description": "关键词列表",
                "constraints": {
                    "is_annotation": True
                }
            },
            {
                "path": "analysis.summary",
                "field_type": "str", 
                "required": True,
                "description": "文档摘要",
                "constraints": {
                    "is_annotation": True
                }
            }
        ]
    }
    
    # 3. 创建任务数据结构
    task_data = {
        "id": task_id,
        "name": "测试保存功能任务",
        "description": "用于测试标注保存功能的任务",
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "assignee_id": "test_user",
        "template": {
            "name": "test_template.json",
            "file_path": f"public_files/templates/test_template_{task_id}.json"
        },
        "documents": [
            {
                "id": document_id,
                "filename": f"test_document_{document_id}.json",
                "file_path": f"tasks/{task_id}/documents/{document_id}.json",
                "status": "pending",
                "uploaded_at": datetime.now().isoformat()
            }
        ]
    }
    
    # 4. 确保目录存在
    data_dir = Path("data")
    task_dir = data_dir / "tasks" / task_id
    documents_dir = task_dir / "documents"
    annotations_dir = task_dir / "annotations"
    templates_dir = data_dir / "public_files" / "templates"
    
    for directory in [task_dir, documents_dir, annotations_dir, templates_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"📁 创建目录: {directory}")
    
    # 5. 保存模板文件
    template_file = templates_dir / f"test_template_{task_id}.json"
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template_config, f, ensure_ascii=False, indent=2)
    print(f"💾 保存模板: {template_file}")
    
    # 6. 保存测试文档
    document_file = documents_dir / f"{document_id}.json"
    with open(document_file, 'w', encoding='utf-8') as f:
        json.dump(test_document, f, ensure_ascii=False, indent=2)
    print(f"💾 保存文档: {document_file}")
    
    # 7. 更新任务列表
    tasks_file = data_dir / "tasks" / "tasks.json"
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
    else:
        tasks_data = {"tasks": []}
    
    tasks_data["tasks"].append(task_data)
    
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(tasks_data, f, ensure_ascii=False, indent=2)
    print(f"💾 更新任务列表: {tasks_file}")
    
    print(f"\n✅ 测试任务创建完成!")
    print(f"📋 任务ID: {task_id}")
    print(f"📄 文档ID: {document_id}")
    print(f"🌐 访问地址: http://localhost:3000/tasks/{task_id}/documents/{document_id}/annotation-buffer")
    print(f"\n💡 测试步骤:")
    print(f"1. 启动后端: uvicorn backend.app.main:app --reload")
    print(f"2. 启动前端: cd frontend && npm start")
    print(f"3. 在浏览器中打开标注页面")
    print(f"4. 填写标注字段并点击保存按钮")
    print(f"5. 检查 data/tasks/{task_id}/annotations/ 目录是否生成标注文件")
    
    return task_id, document_id

def verify_task_creation(task_id, document_id):
    """验证任务创建是否成功"""
    
    print(f"\n🔍 验证任务创建...")
    
    data_dir = Path("data")
    task_dir = data_dir / "tasks" / task_id
    
    # 检查各个文件是否存在
    files_to_check = [
        task_dir / "documents" / f"{document_id}.json",
        data_dir / "public_files" / "templates" / f"test_template_{task_id}.json",
        data_dir / "tasks" / "tasks.json"
    ]
    
    all_good = True
    for file_path in files_to_check:
        if file_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_good = False
    
    if all_good:
        print("✅ 任务创建验证通过")
    else:
        print("❌ 任务创建验证失败")
    
    return all_good

if __name__ == "__main__":
    print("🏗️  创建测试任务用于验证保存功能")
    print("=" * 50)
    
    task_id, document_id = create_test_task()
    verify_task_creation(task_id, document_id)
    
    print("\n" + "=" * 50)
    print("🎯 下一步测试保存功能:")
    print("   运行: python test_save_function.py") 