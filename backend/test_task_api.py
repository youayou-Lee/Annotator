#!/usr/bin/env python3
"""
任务管理API测试脚本
测试第五阶段的任务管理HTTP接口
"""

import asyncio
import json
import sys
from pathlib import Path
import httpx

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TaskAPITester:
    """任务管理API测试器"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
        self.auth_token = None
        self.test_users = {}
        self.test_tasks = {}
    
    async def login(self, username: str, password: str):
        """登录获取token"""
        response = await self.client.post("/api/auth/login", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            print(f"✅ 登录成功: {username}")
            return True
        else:
            print(f"❌ 登录失败: {username} - {response.text}")
            return False
    
    def get_headers(self):
        """获取认证头"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def test_task_statistics(self):
        """测试任务统计API"""
        print("\n📊 测试任务统计API...")
        
        response = await self.client.get("/api/tasks/statistics", headers=self.get_headers())
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 获取任务统计成功:")
            print(f"   - 总任务数: {stats.get('total_tasks')}")
            print(f"   - 待处理: {stats.get('pending_tasks')}")
            print(f"   - 进行中: {stats.get('in_progress_tasks')}")
            print(f"   - 已完成: {stats.get('completed_tasks')}")
            print(f"   - 我的任务: {stats.get('my_tasks')}")
        else:
            print(f"❌ 获取任务统计失败: {response.status_code} - {response.text}")
    
    async def test_task_list(self):
        """测试任务列表API"""
        print("\n📋 测试任务列表API...")
        
        # 测试1: 获取所有任务
        response = await self.client.get("/api/tasks/", headers=self.get_headers())
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取任务列表成功:")
            print(f"   - 总数: {data.get('total')}")
            print(f"   - 当前页: {data.get('page')}")
            print(f"   - 每页数量: {data.get('page_size')}")
            print(f"   - 总页数: {data.get('total_pages')}")
            print(f"   - 任务数量: {len(data.get('tasks', []))}")
            
            # 保存任务信息
            for task in data.get('tasks', []):
                self.test_tasks[task['id']] = task
                print(f"     📝 任务: {task['name']} (状态: {task['status']})")
        else:
            print(f"❌ 获取任务列表失败: {response.status_code} - {response.text}")
        
        # 测试2: 带筛选条件的查询
        response = await self.client.get("/api/tasks/?status=pending&page_size=5", headers=self.get_headers())
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 筛选待处理任务成功: {len(data.get('tasks', []))} 个")
        else:
            print(f"❌ 筛选任务失败: {response.status_code} - {response.text}")
    
    async def test_task_detail(self):
        """测试任务详情API"""
        print("\n🔍 测试任务详情API...")
        
        if not self.test_tasks:
            print("⚠️ 没有可用的任务，跳过详情测试")
            return
        
        task_id = list(self.test_tasks.keys())[0]
        response = await self.client.get(f"/api/tasks/{task_id}", headers=self.get_headers())
        
        if response.status_code == 200:
            task = response.json()
            print(f"✅ 获取任务详情成功:")
            print(f"   - 任务名: {task.get('name')}")
            print(f"   - 状态: {task.get('status')}")
            print(f"   - 文档数: {len(task.get('documents', []))}")
            print(f"   - 进度: {task.get('progress', {}).get('completion_percentage', 0)}%")
            if task.get('template'):
                print(f"   - 模板: {task['template']['filename']}")
        else:
            print(f"❌ 获取任务详情失败: {response.status_code} - {response.text}")
    
    async def test_task_progress(self):
        """测试任务进度API"""
        print("\n📈 测试任务进度API...")
        
        if not self.test_tasks:
            print("⚠️ 没有可用的任务，跳过进度测试")
            return
        
        task_id = list(self.test_tasks.keys())[0]
        response = await self.client.get(f"/api/tasks/{task_id}/progress", headers=self.get_headers())
        
        if response.status_code == 200:
            progress = response.json()
            print(f"✅ 获取任务进度成功:")
            print(f"   - 任务ID: {progress.get('task_id')}")
            print(f"   - 任务名: {progress.get('task_name')}")
            print(f"   - 状态: {progress.get('status')}")
            
            progress_info = progress.get('progress', {})
            if progress_info:
                print(f"   - 总文档: {progress_info.get('total_documents')}")
                print(f"   - 已完成: {progress_info.get('completed_documents')}")
                print(f"   - 进行中: {progress_info.get('in_progress_documents')}")
                print(f"   - 待处理: {progress_info.get('pending_documents')}")
                print(f"   - 完成率: {progress_info.get('completion_percentage')}%")
        else:
            print(f"❌ 获取任务进度失败: {response.status_code} - {response.text}")
    
    async def test_template_fields(self):
        """测试模板字段API"""
        print("\n🔧 测试模板字段API...")
        
        if not self.test_tasks:
            print("⚠️ 没有可用的任务，跳过模板字段测试")
            return
        
        # 找一个有模板的任务
        task_with_template = None
        for task in self.test_tasks.values():
            if task.get('template'):
                task_with_template = task
                break
        
        if not task_with_template:
            print("⚠️ 没有包含模板的任务，跳过模板字段测试")
            return
        
        task_id = task_with_template['id']
        response = await self.client.get(f"/api/tasks/{task_id}/template/fields", headers=self.get_headers())
        
        if response.status_code == 200:
            template_info = response.json()
            print(f"✅ 获取模板字段成功:")
            print(f"   - 模板文件: {template_info.get('template_filename')}")
            print(f"   - 验证结果: {template_info.get('validation_result', {}).get('valid')}")
            fields = template_info.get('fields', {})
            if fields:
                print(f"   - 字段数量: {len(fields.get('properties', {}))}")
        else:
            print(f"❌ 获取模板字段失败: {response.status_code} - {response.text}")
    
    async def test_document_status_update(self):
        """测试文档状态更新API"""
        print("\n📝 测试文档状态更新API...")
        
        if not self.test_tasks:
            print("⚠️ 没有可用的任务，跳过文档状态更新测试")
            return
        
        # 找一个有文档的任务
        task_with_docs = None
        for task in self.test_tasks.values():
            if task.get('documents'):
                task_with_docs = task
                break
        
        if not task_with_docs:
            print("⚠️ 没有包含文档的任务，跳过文档状态更新测试")
            return
        
        task_id = task_with_docs['id']
        document_id = task_with_docs['documents'][0]['id']
        
        # 更新文档状态为进行中
        response = await self.client.put(
            f"/api/tasks/{task_id}/documents/{document_id}/status?status=in_progress",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            updated_task = response.json()
            print(f"✅ 更新文档状态成功:")
            print(f"   - 任务状态: {updated_task.get('status')}")
            print(f"   - 完成进度: {updated_task.get('progress', {}).get('completion_percentage')}%")
        else:
            print(f"❌ 更新文档状态失败: {response.status_code} - {response.text}")
    
    async def run_all_tests(self):
        """运行所有API测试"""
        print("🚀 开始任务管理API测试\n")
        
        try:
            # 登录
            success = await self.login("admin_user", "admin123")
            if not success:
                print("❌ 登录失败，无法继续测试")
                return
            
            # 运行各项测试
            await self.test_task_statistics()
            await self.test_task_list()
            await self.test_task_detail()
            await self.test_task_progress()
            await self.test_template_fields()
            await self.test_document_status_update()
            
            print("\n🎉 所有API测试完成！")
            
        except Exception as e:
            print(f"\n❌ 测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.client.aclose()


async def main():
    """主函数"""
    print("=" * 60)
    print("🎯 任务管理API测试 - 第五阶段")
    print("=" * 60)
    
    tester = TaskAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 