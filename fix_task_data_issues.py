#!/usr/bin/env python3
"""
修复任务数据格式问题
解决Pydantic验证失败的问题
"""

import json
from pathlib import Path
from datetime import datetime

def fix_task_data():
    """修复任务数据格式问题"""
    
    print("🔧 修复任务数据格式问题...")
    
    tasks_file = Path("data/tasks/tasks.json")
    if not tasks_file.exists():
        print("❌ 任务文件不存在")
        return False
    
    try:
        # 读取现有数据
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        print(f"📋 处理 {len(tasks_data.get('tasks', []))} 个任务...")
        
        for task in tasks_data.get('tasks', []):
            print(f"   📝 修复任务: {task.get('id')}")
            
            # 1. 修复状态枚举
            if task.get('status') == 'active':
                task['status'] = 'pending'
                print(f"      ✅ 状态: active -> pending")
            
            # 2. 添加creator_id字段（如果缺失）
            if 'creator_id' not in task:
                task['creator_id'] = 'admin_001'  # 默认创建者
                print(f"      ✅ 添加creator_id: admin_001")
            
            # 3. 修复template字段
            if 'template' in task and task['template']:
                template = task['template']
                
                # 确保filename字段存在
                if 'filename' not in template and 'name' in template:
                    template['filename'] = template['name']
                    print(f"      ✅ 模板filename: {template['name']}")
                elif 'filename' not in template:
                    # 从file_path提取filename
                    file_path = template.get('file_path', '')
                    if file_path:
                        template['filename'] = Path(file_path).name
                        print(f"      ✅ 模板filename: {template['filename']}")
                    else:
                        template['filename'] = 'unknown_template.json'
                        print(f"      ⚠️  模板filename: unknown_template.json")
            
            # 4. 修复文档状态
            for doc in task.get('documents', []):
                if doc.get('status') not in ['pending', 'in_progress', 'completed']:
                    doc['status'] = 'pending'
                    print(f"      ✅ 文档状态: -> pending")
                
                # 添加created_at字段（如果缺失）
                if 'created_at' not in doc:
                    doc['created_at'] = task.get('created_at', datetime.now().isoformat())
                    print(f"      ✅ 文档created_at已添加")
        
        # 保存修复后的数据
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=2)
        
        print("✅ 任务数据修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def validate_fixed_data():
    """验证修复后的数据"""
    
    print("\n🔍 验证修复后的数据...")
    
    # 尝试导入和验证
    import sys
    backend_path = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_path))
    
    try:
        from app.core.storage import StorageManager
        from app.models.task import Task
        
        storage = StorageManager()
        
        # 测试get_all_tasks
        all_tasks = storage.get_all_tasks()
        print(f"✅ 成功获取 {len(all_tasks)} 个任务")
        
        for task in all_tasks:
            print(f"   📝 任务: {task.id}")
            print(f"      状态: {task.status}")
            print(f"      创建者: {task.creator_id}")
            print(f"      分配给: {task.assignee_id}")
            print(f"      文档数: {len(task.documents)}")
            
            if task.template:
                print(f"      模板: {task.template.filename}")
        
        # 测试get_task_by_id
        if all_tasks:
            test_task = all_tasks[0]
            found_task = storage.get_task_by_id(test_task.id)
            if found_task:
                print(f"✅ get_task_by_id成功: {found_task.id}")
            else:
                print("❌ get_task_by_id失败")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_annotation_save():
    """测试标注保存功能"""
    
    print("\n💾 测试标注保存功能...")
    
    import sys
    backend_path = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_path))
    
    try:
        from app.core.storage import StorageManager
        from app.models.annotation import Annotation, AnnotationStatus
        
        storage = StorageManager()
        all_tasks = storage.get_all_tasks()
        
        if not all_tasks:
            print("❌ 无可用任务")
            return False
        
        task = all_tasks[0]
        if not task.documents:
            print("❌ 任务无文档")
            return False
        
        document_id = task.documents[0].id
        print(f"📝 测试任务: {task.id}")
        print(f"📄 测试文档: {document_id}")
        
        # 创建测试标注
        test_annotation = Annotation(
            document_id=document_id,
            task_id=task.id,
            status=AnnotationStatus.IN_PROGRESS,
            annotator_id=task.assignee_id,
            annotation_data={
                "analysis": {
                    "topic": "人工智能与机器学习",
                    "keywords": ["人工智能", "机器学习", "深度学习", "神经网络"],
                    "summary": "本文档详细介绍了人工智能和机器学习的核心概念，包括深度学习和神经网络的基本原理。"
                }
            },
            updated_at=datetime.now()
        )
        
        # 保存标注
        saved_annotation = storage.save_annotation(test_annotation)
        print("✅ 标注保存成功")
        print(f"   状态: {saved_annotation.status}")
        print(f"   有数据: {'是' if saved_annotation.annotation_data else '否'}")
        
        # 验证文件生成
        annotation_file = Path(f"data/tasks/{task.id}/annotations/{document_id}.json")
        if annotation_file.exists():
            with open(annotation_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
            print("✅ 标注文件已生成")
            print(f"   文件大小: {len(json.dumps(content))} 字符")
            print(f"   包含字段: {list(content.keys())}")
            
            if content.get('annotation_data'):
                print("✅ annotation_data不为空")
                ann_data = content['annotation_data']
                if isinstance(ann_data, dict) and ann_data.get('analysis'):
                    print("✅ 包含analysis数据")
                    analysis = ann_data['analysis']
                    print(f"   主题: {analysis.get('topic', 'N/A')}")
                    print(f"   关键词: {analysis.get('keywords', [])}")
                    print(f"   摘要长度: {len(analysis.get('summary', ''))}")
                    return True
            
            print("❌ annotation_data为空或格式错误")
        else:
            print("❌ 标注文件未生成")
        
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主函数"""
    print("🔧 修复任务数据格式问题")
    print("=" * 60)
    
    # 1. 修复数据格式
    if not fix_task_data():
        print("❌ 数据修复失败")
        return
    
    # 2. 验证修复结果
    if not validate_fixed_data():
        print("❌ 数据验证失败")
        return
    
    # 3. 测试标注保存
    if test_annotation_save():
        print("\n🎉 问题修复成功!")
        print("✅ 任务数据格式已修复")
        print("✅ Storage层工作正常")
        print("✅ 标注保存功能正常")
        print("\n💡 现在可以测试前端的保存功能了")
    else:
        print("\n❌ 标注保存仍有问题")

if __name__ == "__main__":
    main() 