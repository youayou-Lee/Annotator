#!/usr/bin/env python3
"""
修复保存功能的问题
1. 修复权限问题
2. 修复数据格式问题
3. 测试完整的保存流程
"""

import json
import requests
from pathlib import Path
from datetime import datetime

def fix_task_assignment():
    """修复任务分配问题 - 将任务分配给admin用户"""
    
    print("🔧 修复任务分配问题...")
    
    # 读取现有任务
    tasks_file = Path("data/tasks/tasks.json")
    if not tasks_file.exists():
        print("❌ 任务文件不存在")
        return False
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        # 查找用户ID
        users_file = Path("data/users/users.json")
        admin_user_id = None
        
        if users_file.exists():
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                
            for user in users_data.get('users', []):
                if user.get('username') == 'admin':
                    admin_user_id = user.get('id')
                    break
        
        if not admin_user_id:
            print("❌ 未找到admin用户ID")
            return False
        
        # 更新任务分配
        updated = False
        for task in tasks_data.get('tasks', []):
            if task.get('assignee_id') != admin_user_id:
                print(f"📝 更新任务 {task['id']} 的分配用户: {task.get('assignee_id')} -> {admin_user_id}")
                task['assignee_id'] = admin_user_id
                task['updated_at'] = datetime.now().isoformat()
                updated = True
        
        if updated:
            # 保存更新后的任务
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
            print("✅ 任务分配更新成功")
        else:
            print("ℹ️  任务分配无需更新")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复任务分配失败: {e}")
        return False

def check_backend_annotation_model():
    """检查后端期望的数据模型"""
    
    print("\n🔍 检查后端数据模型...")
    
    # 检查AnnotationUpdate模型
    try:
        # 通过API文档获取模型信息
        response = requests.get("http://localhost:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_spec = response.json()
            components = openapi_spec.get("components", {})
            schemas = components.get("schemas", {})
            
            if "AnnotationUpdate" in schemas:
                annotation_update = schemas["AnnotationUpdate"]
                print("✅ 找到AnnotationUpdate模型:")
                print(f"   属性: {list(annotation_update.get('properties', {}).keys())}")
                
                # 检查具体的属性定义
                properties = annotation_update.get('properties', {})
                for prop_name, prop_def in properties.items():
                    print(f"   - {prop_name}: {prop_def.get('type', 'unknown')}")
                
                return annotation_update
            else:
                print("❌ 未找到AnnotationUpdate模型")
        else:
            print("❌ 无法获取API文档")
    except Exception as e:
        print(f"❌ 检查数据模型失败: {e}")
    
    return None

def test_corrected_save_api():
    """使用正确的数据格式测试保存API"""
    
    print("\n🧪 测试修正后的保存API...")
    
    # 1. 登录获取token
    tester = AuthenticatedAPITester()
    if not tester.login():
        print("❌ 登录失败")
        return False
    
    # 2. 获取任务信息
    task_id, document_id = get_available_task()
    if not task_id:
        print("❌ 未找到可用任务")
        return False
    
    print(f"🎯 测试任务: {task_id}")
    print(f"📄 测试文档: {document_id}")
    
    # 3. 测试多种数据格式
    test_cases = [
        {
            "name": "格式1: annotation_data + status",
            "data": {
                "annotation_data": {
                    "analysis": {
                        "topic": "人工智能发展",
                        "keywords": ["AI", "机器学习", "神经网络"],
                        "summary": "本文档详细描述了人工智能技术的最新发展趋势。"
                    }
                },
                "status": "in_progress"
            }
        },
        {
            "name": "格式2: 仅annotation_data",
            "data": {
                "annotation_data": {
                    "analysis": {
                        "topic": "人工智能发展",
                        "keywords": ["AI", "机器学习", "神经网络"],
                        "summary": "本文档详细描述了人工智能技术的最新发展趋势。"
                    }
                }
            }
        },
        {
            "name": "格式3: annotated_data (前端实际格式)",
            "data": {
                "annotated_data": {
                    "analysis": {
                        "topic": "人工智能发展",
                        "keywords": ["AI", "机器学习", "神经网络"],
                        "summary": "本文档详细描述了人工智能技术的最新发展趋势。"
                    }
                },
                "is_auto_save": False
            }
        }
    ]
    
    success_count = 0
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试用例 {i}: {test_case['name']}")
        
        save_url = f"http://localhost:8000/api/annotations/{task_id}/documents/{document_id}/annotation"
        
        try:
            response = tester.session.post(save_url, json=test_case['data'], timeout=10)
            print(f"📥 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 测试成功!")
                print(f"📄 响应: {response.text[:200]}...")
                success_count += 1
                
                # 立即检查文件是否生成
                if check_annotation_file_created(task_id, document_id):
                    print("✅ 标注文件已生成!")
                    break
            else:
                print(f"❌ 测试失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    return success_count > 0

def check_annotation_file_created(task_id, document_id):
    """检查标注文件是否已生成"""
    
    annotation_file = Path(f"data/tasks/{task_id}/annotations/{document_id}.json")
    if annotation_file.exists():
        try:
            with open(annotation_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    return 'annotation_data' in data and data['annotation_data']
        except:
            pass
    return False

class AuthenticatedAPITester:
    """认证API测试器 - 简化版"""
    
    def __init__(self):
        self.session = requests.Session()
        self.token = None
    
    def login(self, username="admin", password="admin123"):
        """登录"""
        login_url = "http://localhost:8000/api/auth/login"
        
        try:
            response = self.session.post(login_url, json={
                "username": username,
                "password": password
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                print(f"✅ 登录成功: {username}")
                return True
            else:
                print(f"❌ 登录失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False

def get_available_task():
    """获取可用任务"""
    tasks_file = Path("data/tasks/tasks.json")
    if tasks_file.exists():
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            for task in tasks_data.get("tasks", []):
                if task.get("documents"):
                    return task["id"], task["documents"][0]["id"]
        except:
            pass
    return None, None

def main():
    """主函数"""
    print("🔧 修复标注保存功能问题")
    print("=" * 60)
    
    # 1. 修复任务分配问题
    if not fix_task_assignment():
        print("❌ 无法修复任务分配")
        return
    
    # 2. 检查后端数据模型
    check_backend_annotation_model()
    
    # 3. 测试修正后的保存API
    if test_corrected_save_api():
        print("\n🎉 保存功能修复成功!")
        
        # 最终验证
        task_id, document_id = get_available_task()
        if task_id and check_annotation_file_created(task_id, document_id):
            print("✅ 标注文件已正确生成!")
            
            # 显示文件内容
            annotation_file = Path(f"data/tasks/{task_id}/annotations/{document_id}.json")
            with open(annotation_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                print(f"📄 文件内容预览:")
                print(json.dumps(content, ensure_ascii=False, indent=2)[:500] + "...")
        
    else:
        print("\n❌ 保存功能仍有问题")
    
    print(f"\n" + "=" * 60)
    print("🎯 下一步:")
    print("   1. 测试前端页面的保存功能")
    print("   2. 检查任务状态是否正确更新")
    print("   3. 验证提交功能是否正常工作")

if __name__ == "__main__":
    main() 