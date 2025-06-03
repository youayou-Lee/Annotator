#!/usr/bin/env python3
"""
调试标注保存功能问题
分析为什么保存的文件是空的，以及任务状态不更新的原因
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime

def check_existing_annotations():
    """检查现有的标注文件"""
    
    print("🔍 检查现有标注文件...")
    
    data_dir = Path("data/tasks")
    if not data_dir.exists():
        print("❌ 任务目录不存在")
        return None
    
    task_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    if not task_dirs:
        print("❌ 未找到任务目录")
        return None
    
    for task_dir in task_dirs:
        print(f"\n📁 检查任务: {task_dir.name}")
        
        annotations_dir = task_dir / "annotations"
        if annotations_dir.exists():
            annotation_files = list(annotations_dir.glob("*.json"))
            print(f"   📄 找到 {len(annotation_files)} 个标注文件")
            
            for ann_file in annotation_files:
                print(f"   📋 文件: {ann_file.name}")
                try:
                    with open(ann_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            print(f"   ❌ 文件为空!")
                        else:
                            data = json.loads(content)
                            print(f"   ✅ 文件大小: {len(content)} 字符")
                            print(f"   📊 数据键: {list(data.keys())}")
                            
                            # 检查关键字段
                            if 'annotation_data' in data:
                                ann_data = data['annotation_data']
                                if ann_data:
                                    print(f"   ✅ 有标注数据: {type(ann_data)}")
                                    if isinstance(ann_data, dict):
                                        print(f"   📝 标注字段: {list(ann_data.keys())}")
                                else:
                                    print(f"   ❌ 标注数据为空")
                            else:
                                print(f"   ❌ 缺少annotation_data字段")
                                
                except Exception as e:
                    print(f"   ❌ 读取失败: {e}")
        else:
            print(f"   ⚠️  annotations目录不存在")
    
    return task_dirs[0] if task_dirs else None

def test_save_api_directly(task_id, document_id):
    """直接测试保存API"""
    
    print(f"\n🧪 直接测试保存API...")
    print(f"任务ID: {task_id}")
    print(f"文档ID: {document_id}")
    
    # 构造测试数据
    test_annotation_data = {
        "annotation_data": {
            "analysis": {
                "topic": "测试主题",
                "keywords": ["关键词1", "关键词2"],
                "summary": "这是一个测试摘要"
            }
        },
        "is_auto_save": False
    }
    
    # 测试保存API
    save_url = f"http://localhost:8000/api/annotations/{task_id}/documents/{document_id}/annotation"
    
    try:
        print(f"📡 调用保存API: {save_url}")
        print(f"📤 发送数据: {json.dumps(test_annotation_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            save_url,
            json=test_annotation_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 响应状态: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ API调用成功")
            return True
        else:
            print(f"❌ API调用失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API调用异常: {e}")
        return False

def test_submit_api_directly(task_id, document_id):
    """直接测试提交API"""
    
    print(f"\n🚀 直接测试提交API...")
    
    # 构造测试数据
    test_submit_data = {
        "annotation_data": {
            "analysis": {
                "topic": "测试主题",
                "keywords": ["关键词1", "关键词2"],
                "summary": "这是一个测试摘要"
            }
        }
    }
    
    # 测试提交API
    submit_url = f"http://localhost:8000/api/annotations/{task_id}/documents/{document_id}/submit"
    
    try:
        print(f"📡 调用提交API: {submit_url}")
        print(f"📤 发送数据: {json.dumps(test_submit_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            submit_url,
            json=test_submit_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 响应状态: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 提交API调用成功")
            return True
        else:
            print(f"❌ 提交API调用失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 提交API调用异常: {e}")
        return False

def check_task_status(task_id):
    """检查任务状态"""
    
    print(f"\n📊 检查任务状态...")
    
    # 检查tasks.json中的状态
    tasks_file = Path("data/tasks/tasks.json")
    if tasks_file.exists():
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
                
            for task in tasks_data.get("tasks", []):
                if task["id"] == task_id:
                    print(f"✅ 找到任务: {task['name']}")
                    print(f"📋 任务状态: {task.get('status', 'N/A')}")
                    
                    for doc in task.get("documents", []):
                        print(f"📄 文档: {doc.get('filename', 'N/A')}")
                        print(f"📊 文档状态: {doc.get('status', 'N/A')}")
                    
                    return task
                    
            print(f"❌ 未找到任务ID: {task_id}")
            return None
            
        except Exception as e:
            print(f"❌ 读取任务文件失败: {e}")
            return None
    else:
        print("❌ 任务文件不存在")
        return None

def analyze_frontend_backend_mismatch():
    """分析前后端数据传递是否有问题"""
    
    print(f"\n🔍 分析前后端数据传递问题...")
    
    # 检查AnnotationUpdate模型
    print("📋 检查后端数据模型...")
    
    # 检查前端API调用格式
    print("📱 检查前端API调用格式...")
    
    print("🎯 可能的问题原因:")
    print("   1. 前端发送的数据格式与后端期望的不匹配")
    print("   2. annotation_data字段嵌套结构不正确") 
    print("   3. 权限验证失败")
    print("   4. 数据验证失败但没有正确的错误处理")
    print("   5. 文件写入权限问题")

def get_available_task():
    """获取可用的任务ID和文档ID"""
    
    tasks_file = Path("data/tasks/tasks.json")
    if not tasks_file.exists():
        return None, None
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        for task in tasks_data.get("tasks", []):
            if task.get("documents"):
                task_id = task["id"]
                document_id = task["documents"][0]["id"]
                return task_id, document_id
                
    except Exception as e:
        print(f"❌ 读取任务失败: {e}")
    
    return None, None

def main():
    """主函数"""
    print("🐛 调试标注保存功能问题")
    print("=" * 60)
    
    # 1. 检查现有标注文件
    latest_task = check_existing_annotations()
    
    # 2. 获取任务和文档ID
    task_id, document_id = get_available_task()
    
    if not task_id or not document_id:
        print("\n❌ 未找到可用的任务，请先运行: python create_test_save_task.py")
        return
    
    print(f"\n🎯 使用任务进行测试:")
    print(f"   任务ID: {task_id}")
    print(f"   文档ID: {document_id}")
    
    # 3. 检查任务状态
    task_info = check_task_status(task_id)
    
    # 4. 直接测试保存API
    save_success = test_save_api_directly(task_id, document_id)
    
    # 5. 如果保存成功，测试提交API
    if save_success:
        test_submit_api_directly(task_id, document_id)
    
    # 6. 再次检查标注文件
    print(f"\n🔍 再次检查标注文件...")
    check_existing_annotations()
    
    # 7. 再次检查任务状态
    print(f"\n📊 再次检查任务状态...")
    check_task_status(task_id)
    
    # 8. 分析可能的问题
    analyze_frontend_backend_mismatch()
    
    print(f"\n" + "=" * 60)
    print(f"🔧 下一步建议:")
    print(f"   1. 检查后端日志是否有错误信息")
    print(f"   2. 检查前端浏览器控制台的网络请求")
    print(f"   3. 确认数据格式是否正确")
    print(f"   4. 检查权限和验证逻辑")

if __name__ == "__main__":
    main() 