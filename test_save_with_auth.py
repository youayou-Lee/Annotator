#!/usr/bin/env python3
"""
包含认证的标注保存功能测试
模拟完整的登录->标注->保存流程
"""

import requests
import json
import os
from pathlib import Path

class AuthenticatedAPITester:
    """带认证的API测试器"""
    
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.user_info = None
    
    def login(self, username="admin", password="admin123"):
        """登录并获取token"""
        
        print(f"🔐 尝试登录用户: {username}")
        
        login_url = f"{self.base_url}/auth/login"
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(login_url, json=login_data, timeout=10)
            print(f"📡 登录请求状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_info = data.get('user')
                
                # 设置Authorization header
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                
                print(f"✅ 登录成功!")
                print(f"👤 用户信息: {self.user_info}")
                print(f"🎫 Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ 登录失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def test_save_annotation(self, task_id, document_id):
        """测试保存标注"""
        
        if not self.token:
            print("❌ 未登录，无法测试保存")
            return False
        
        print(f"\n💾 测试保存标注...")
        print(f"任务ID: {task_id}")
        print(f"文档ID: {document_id}")
        
        # 构造测试数据
        annotation_data = {
            "annotation_data": {
                "analysis": {
                    "topic": "机器学习与人工智能",
                    "keywords": ["机器学习", "神经网络", "深度学习"],
                    "summary": "这是一个关于机器学习技术的综合性文档，详细介绍了神经网络和深度学习的基本概念。"
                }
            },
            "is_auto_save": False
        }
        
        save_url = f"{self.base_url}/annotations/{task_id}/documents/{document_id}/annotation"
        
        try:
            print(f"📡 调用保存API: {save_url}")
            print(f"📤 发送数据: {json.dumps(annotation_data, ensure_ascii=False, indent=2)}")
            
            response = self.session.post(save_url, json=annotation_data, timeout=10)
            
            print(f"📥 响应状态: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 保存API调用成功!")
                return True
            else:
                print(f"❌ 保存API调用失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 保存API调用异常: {e}")
            return False
    
    def test_submit_annotation(self, task_id, document_id):
        """测试提交标注"""
        
        if not self.token:
            print("❌ 未登录，无法测试提交")
            return False
        
        print(f"\n🚀 测试提交标注...")
        
        # 构造提交数据
        submit_data = {
            "annotation_data": {
                "analysis": {
                    "topic": "机器学习与人工智能",
                    "keywords": ["机器学习", "神经网络", "深度学习"],
                    "summary": "这是一个关于机器学习技术的综合性文档，详细介绍了神经网络和深度学习的基本概念。"
                }
            }
        }
        
        submit_url = f"{self.base_url}/annotations/{task_id}/documents/{document_id}/submit"
        
        try:
            print(f"📡 调用提交API: {submit_url}")
            print(f"📤 发送数据: {json.dumps(submit_data, ensure_ascii=False, indent=2)}")
            
            response = self.session.post(submit_url, json=submit_data, timeout=10)
            
            print(f"📥 响应状态: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 提交API调用成功!")
                return True
            else:
                print(f"❌ 提交API调用失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 提交API调用异常: {e}")
            return False

def create_test_user():
    """创建测试用户"""
    
    print("👤 创建测试用户...")
    
    # 检查是否已有用户
    users_file = Path("data/users/users.json")
    if users_file.exists():
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                
            if users_data.get('users'):
                print("✅ 已存在用户数据")
                for user in users_data['users']:
                    print(f"   👤 用户: {user.get('username')} ({user.get('role')})")
                return True
        except Exception as e:
            print(f"❌ 读取用户文件失败: {e}")
    
    # 创建默认用户
    from datetime import datetime
    import bcrypt
    
    # 确保用户目录存在
    users_dir = Path("data/users")
    users_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建默认管理员用户
    password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin_user = {
        "id": "admin_001",
        "username": "admin",
        "password_hash": password_hash,
        "role": "admin",
        "created_at": datetime.now().isoformat()
    }
    
    users_data = {
        "users": [admin_user]
    }
    
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 创建默认用户: admin / admin123")
    return True

def check_annotation_files(task_id):
    """检查标注文件是否生成"""
    
    print(f"\n🔍 检查标注文件...")
    
    annotations_dir = Path(f"data/tasks/{task_id}/annotations")
    if not annotations_dir.exists():
        print(f"❌ 标注目录不存在: {annotations_dir}")
        return False
    
    annotation_files = list(annotations_dir.glob("*.json"))
    print(f"📄 找到 {len(annotation_files)} 个标注文件")
    
    for ann_file in annotation_files:
        print(f"📋 文件: {ann_file.name}")
        try:
            with open(ann_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    print(f"   ✅ 文件大小: {len(content)} 字符")
                    print(f"   📊 数据键: {list(data.keys())}")
                    
                    if 'annotation_data' in data and data['annotation_data']:
                        print(f"   ✅ 包含标注数据!")
                        if isinstance(data['annotation_data'], dict):
                            print(f"   📝 标注字段: {list(data['annotation_data'].keys())}")
                        return True
                    else:
                        print(f"   ❌ 标注数据为空")
                else:
                    print(f"   ❌ 文件为空")
        except Exception as e:
            print(f"   ❌ 读取失败: {e}")
    
    return False

def check_task_status_update(task_id):
    """检查任务状态是否更新"""
    
    print(f"\n📊 检查任务状态更新...")
    
    tasks_file = Path("data/tasks/tasks.json")
    if not tasks_file.exists():
        print("❌ 任务文件不存在")
        return False
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        for task in tasks_data.get("tasks", []):
            if task["id"] == task_id:
                print(f"✅ 找到任务: {task['name']}")
                print(f"📋 任务状态: {task.get('status')}")
                
                for doc in task.get("documents", []):
                    print(f"📄 文档: {doc.get('filename')}")
                    print(f"📊 文档状态: {doc.get('status')}")
                    
                    if doc.get('status') == 'completed':
                        print("✅ 文档状态已更新为completed!")
                        return True
                
                print("⚠️  文档状态未更新")
                return False
        
        print(f"❌ 未找到任务: {task_id}")
        return False
        
    except Exception as e:
        print(f"❌ 读取任务文件失败: {e}")
        return False

def get_available_task():
    """获取可用的任务"""
    
    tasks_file = Path("data/tasks/tasks.json")
    if not tasks_file.exists():
        return None, None
    
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        for task in tasks_data.get("tasks", []):
            if task.get("documents"):
                return task["id"], task["documents"][0]["id"]
    except Exception as e:
        print(f"❌ 读取任务失败: {e}")
    
    return None, None

def main():
    """主函数"""
    print("🔐 带认证的标注保存功能测试")
    print("=" * 60)
    
    # 1. 创建测试用户
    create_test_user()
    
    # 2. 获取测试任务
    task_id, document_id = get_available_task()
    if not task_id:
        print("\n❌ 未找到可用任务，请先运行: python create_test_save_task.py")
        return
    
    print(f"\n🎯 使用任务进行测试:")
    print(f"   任务ID: {task_id}")
    print(f"   文档ID: {document_id}")
    
    # 3. 创建认证测试器
    tester = AuthenticatedAPITester()
    
    # 4. 登录
    if not tester.login():
        print("\n❌ 登录失败，无法继续测试")
        return
    
    # 5. 测试保存
    save_success = tester.test_save_annotation(task_id, document_id)
    
    # 6. 测试提交
    if save_success:
        submit_success = tester.test_submit_annotation(task_id, document_id)
    
    # 7. 检查结果
    print(f"\n" + "=" * 60)
    print(f"🔍 检查测试结果:")
    
    # 检查标注文件
    file_created = check_annotation_files(task_id)
    
    # 检查任务状态
    status_updated = check_task_status_update(task_id)
    
    # 8. 总结
    print(f"\n" + "=" * 60)
    print(f"📋 测试结果总结:")
    print(f"   🔐 登录: {'✅ 成功' if tester.token else '❌ 失败'}")
    print(f"   💾 保存: {'✅ 成功' if save_success else '❌ 失败'}")
    print(f"   📄 文件: {'✅ 生成' if file_created else '❌ 未生成'}")
    print(f"   📊 状态: {'✅ 更新' if status_updated else '❌ 未更新'}")
    
    if file_created and status_updated:
        print(f"\n🎉 保存功能测试成功！")
    else:
        print(f"\n❌ 保存功能存在问题，需要进一步调试")

if __name__ == "__main__":
    main() 