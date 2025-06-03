#!/usr/bin/env python3
"""
直接测试Storage层来排查问题
绕过API层，直接测试数据存储逻辑
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加backend目录到Python路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.core.storage import StorageManager
    from app.models.annotation import Annotation, AnnotationStatus
    from app.models.task import Task, TaskStatus, DocumentStatus
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)

def test_storage_directly():
    """直接测试Storage层"""
    
    print("🔧 直接测试Storage层...")
    
    # 1. 初始化Storage Manager
    storage = StorageManager()
    
    # 2. 测试get_all_tasks
    print("\n📋 测试get_all_tasks...")
    try:
        all_tasks = storage.get_all_tasks()
        print(f"✅ 获取到 {len(all_tasks)} 个任务")
        
        for task in all_tasks:
            print(f"   📝 任务: {task.id} - {task.name}")
            print(f"      状态: {task.status}")
            print(f"      分配给: {task.assignee_id}")
            print(f"      文档数: {len(task.documents)}")
    except Exception as e:
        print(f"❌ get_all_tasks失败: {e}")
        return False
    
    # 3. 测试get_task_by_id
    if all_tasks:
        test_task = all_tasks[0]
        print(f"\n📋 测试get_task_by_id: {test_task.id}")
        try:
            found_task = storage.get_task_by_id(test_task.id)
            if found_task:
                print("✅ get_task_by_id成功")
                print(f"   任务名: {found_task.name}")
                print(f"   状态: {found_task.status}")
                print(f"   分配给: {found_task.assignee_id}")
            else:
                print("❌ get_task_by_id返回None")
                return False
        except Exception as e:
            print(f"❌ get_task_by_id失败: {e}")
            return False
        
        # 4. 测试标注保存
        if found_task.documents:
            document_id = found_task.documents[0].id
            print(f"\n💾 测试标注保存: 文档 {document_id}")
            
            # 创建测试标注数据
            test_annotation = Annotation(
                document_id=document_id,
                task_id=found_task.id,
                status=AnnotationStatus.IN_PROGRESS,
                annotator_id="admin_001",
                annotation_data={
                    "analysis": {
                        "topic": "人工智能技术",
                        "keywords": ["AI", "机器学习", "深度学习"],
                        "summary": "这是一个关于人工智能技术发展的文档。"
                    }
                },
                updated_at=datetime.now()
            )
            
            try:
                saved_annotation = storage.save_annotation(test_annotation)
                print("✅ 标注保存成功")
                print(f"   文档ID: {saved_annotation.document_id}")
                print(f"   任务ID: {saved_annotation.task_id}")
                print(f"   状态: {saved_annotation.status}")
                print(f"   有数据: {'是' if saved_annotation.annotation_data else '否'}")
                
                # 检查文件是否实际生成
                annotation_file = Path(f"data/tasks/{found_task.id}/annotations/{document_id}.json")
                if annotation_file.exists():
                    print("✅ 标注文件已生成")
                    
                    # 读取文件内容
                    with open(annotation_file, 'r', encoding='utf-8') as f:
                        file_content = json.load(f)
                        print(f"   文件大小: {len(json.dumps(file_content))} 字符")
                        print(f"   包含字段: {list(file_content.keys())}")
                        
                        if 'annotation_data' in file_content:
                            ann_data = file_content['annotation_data']
                            if ann_data:
                                print(f"   标注数据: {list(ann_data.keys())}")
                                print(f"   ✅ 数据保存成功!")
                                return True
                            else:
                                print(f"   ❌ annotation_data为空")
                        else:
                            print(f"   ❌ 缺少annotation_data字段")
                else:
                    print("❌ 标注文件未生成")
                    
            except Exception as e:
                print(f"❌ 标注保存失败: {e}")
                import traceback
                print(traceback.format_exc())
                return False
    
    return False

def check_json_structure():
    """检查JSON数据结构"""
    
    print("\n🔍 检查JSON数据结构...")
    
    # 检查tasks.json
    tasks_file = Path("data/tasks/tasks.json")
    if tasks_file.exists():
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            print("✅ tasks.json结构:")
            print(f"   任务数量: {len(tasks_data.get('tasks', []))}")
            
            for task in tasks_data.get('tasks', []):
                print(f"   📝 任务: {task.get('id')}")
                print(f"      状态类型: {type(task.get('status'))} = {task.get('status')}")
                print(f"      分配给: {task.get('assignee_id')}")
                
                for doc in task.get('documents', []):
                    print(f"      📄 文档: {doc.get('id')}")
                    print(f"         状态类型: {type(doc.get('status'))} = {doc.get('status')}")
                    
        except Exception as e:
            print(f"❌ 读取tasks.json失败: {e}")
    else:
        print("❌ tasks.json不存在")

def check_data_directories():
    """检查数据目录结构"""
    
    print("\n📁 检查数据目录结构...")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ data目录不存在")
        return
    
    print(f"✅ data目录存在")
    
    # 检查任务目录
    tasks_dir = data_dir / "tasks"
    if tasks_dir.exists():
        task_dirs = [d for d in tasks_dir.iterdir() if d.is_dir()]
        print(f"📁 任务目录数量: {len(task_dirs)}")
        
        for task_dir in task_dirs:
            print(f"   📝 任务: {task_dir.name}")
            
            # 检查annotations目录
            annotations_dir = task_dir / "annotations"
            if annotations_dir.exists():
                annotation_files = list(annotations_dir.glob("*.json"))
                print(f"      📄 标注文件: {len(annotation_files)}")
                
                for ann_file in annotation_files:
                    try:
                        with open(ann_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                data = json.loads(content)
                                print(f"         {ann_file.name}: ✅ ({len(content)} 字符)")
                            else:
                                print(f"         {ann_file.name}: ❌ (空文件)")
                    except Exception as e:
                        print(f"         {ann_file.name}: ❌ (读取失败: {e})")
            else:
                print(f"      📁 无annotations目录")
    else:
        print("❌ tasks目录不存在")

def fix_and_test():
    """修复数据问题并测试"""
    
    print("\n🔧 修复数据问题...")
    
    # 检查并创建缺失的目录
    data_dir = Path("data")
    tasks_dir = data_dir / "tasks"
    
    # 读取任务数据
    tasks_file = tasks_dir / "tasks.json"
    if not tasks_file.exists():
        print("❌ 任务文件不存在")
        return False
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        for task in tasks_data.get('tasks', []):
            task_id = task.get('id')
            if task_id:
                # 确保annotations目录存在
                annotations_dir = tasks_dir / task_id / "annotations"
                annotations_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ 创建目录: {annotations_dir}")
        
        print("✅ 目录结构修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def main():
    """主函数"""
    print("🐛 Storage层直接测试")
    print("=" * 60)
    
    # 1. 检查数据目录
    check_data_directories()
    
    # 2. 检查JSON结构
    check_json_structure()
    
    # 3. 修复问题
    fix_and_test()
    
    # 4. 直接测试Storage
    if test_storage_directly():
        print("\n🎉 Storage层测试成功!")
        print("✅ 问题已解决，保存功能应该正常工作了")
    else:
        print("\n❌ Storage层测试失败")
        print("需要进一步排查具体问题")

if __name__ == "__main__":
    main() 