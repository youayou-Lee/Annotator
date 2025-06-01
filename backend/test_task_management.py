#!/usr/bin/env python3
"""
任务管理功能测试脚本
测试第五阶段的任务管理功能实现
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.storage import StorageManager
from app.models.user import UserCreate, UserRole
from app.models.task import TaskCreate, TaskQuery, TaskStatus, DocumentStatus
from app.models.file import FileInfo, FileType
from app.core.security import get_password_hash


class TaskManagementTester:
    """任务管理功能测试器"""
    
    def __init__(self):
        self.storage = StorageManager()
        self.test_users = {}
        self.test_files = {}
        self.test_tasks = {}
    
    def setup_test_data(self):
        """设置测试数据"""
        print("🔧 设置测试数据...")
        
        # 创建测试用户
        users_data = [
            ("super_admin", "super123", UserRole.SUPER_ADMIN),
            ("admin_user", "admin123", UserRole.ADMIN),
            ("annotator1", "anno123", UserRole.ANNOTATOR),
            ("annotator2", "anno456", UserRole.ANNOTATOR),
        ]
        
        for username, password, role in users_data:
            try:
                # 先检查用户是否已存在
                existing_user = self.storage.get_user_by_username(username)
                if existing_user:
                    self.test_users[username] = existing_user
                    print(f"📝 用户已存在: {username} ({role.value})")
                    continue
                
                # 创建新用户
                user_create = UserCreate(username=username, password=password, role=role)
                password_hash = get_password_hash(password)
                user = self.storage.create_user(user_create, password_hash)
                self.test_users[username] = user
                print(f"✅ 创建用户: {username} ({role.value})")
            except Exception as e:
                print(f"❌ 处理用户失败: {username} - {e}")
                # 如果创建失败，尝试获取现有用户
                existing_user = self.storage.get_user_by_username(username)
                if existing_user:
                    self.test_users[username] = existing_user
                    print(f"📝 使用现有用户: {username}")
        
        # 确保至少有一个管理员用户用于创建文件
        if not self.test_users:
            print("❌ 没有可用的测试用户，无法继续测试")
            return
        
        # 创建测试文件
        self.create_test_files()
    
    def create_test_files(self):
        """创建测试文件"""
        print("\n📁 创建测试文件...")
        
        # 获取一个可用的用户作为文件上传者
        uploader_user = None
        for username, user in self.test_users.items():
            if user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
                uploader_user = user
                break
        
        if not uploader_user:
            # 如果没有管理员，使用第一个可用用户
            uploader_user = list(self.test_users.values())[0]
        
        print(f"📤 使用用户 {uploader_user.username} 作为文件上传者")
        
        # 创建测试文档文件
        doc_files = [
            ("test_doc1.json", {"data": "test document 1", "content": "sample content"}),
            ("test_doc2.jsonl", {"line1": "data1", "line2": "data2"}),
            ("test_doc3.json", {"title": "Document 3", "body": "Content of document 3"}),
        ]
        
        for filename, content in doc_files:
            file_path = f"public_files/documents/{filename}"
            full_path = self.storage.data_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            file_info = FileInfo(
                id=f"doc_{len(self.test_files)}",
                filename=filename,
                file_path=file_path,
                file_type=FileType.DOCUMENT,
                file_size=full_path.stat().st_size,
                uploader_id=uploader_user.id,
                uploaded_at=datetime.now()
            )
            self.storage.save_file_info(file_info)
            self.test_files[filename] = file_info
            print(f"✅ 创建文档文件: {filename}")
        
        # 创建测试模板文件
        template_content = '''
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class AnnotationSchema(BaseModel):
    """标注数据模式"""
    
    # 基本信息字段
    title: str = Field(..., description="文档标题")
    category: str = Field(..., description="文档类别")
    
    # 内容字段
    summary: str = Field("", description="文档摘要")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    
    # 评分字段
    quality_score: int = Field(1, ge=1, le=5, description="质量评分(1-5)")
    importance: str = Field("medium", description="重要性等级")
    
    # 标注状态
    is_reviewed: bool = Field(False, description="是否已复审")
    notes: str = Field("", description="标注备注")

def get_annotation_schema() -> Dict[str, Any]:
    """获取标注模式"""
    return AnnotationSchema.model_json_schema()
'''
        
        template_path = "public_files/templates/test_template.py"
        full_template_path = self.storage.data_dir / template_path
        full_template_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        template_info = FileInfo(
            id="template_1",
            filename="test_template.py",
            file_path=template_path,
            file_type=FileType.TEMPLATE,
            file_size=full_template_path.stat().st_size,
            uploader_id=uploader_user.id,
            uploaded_at=datetime.now()
        )
        self.storage.save_file_info(template_info)
        self.test_files["test_template.py"] = template_info
        print(f"✅ 创建模板文件: test_template.py")
    
    def test_task_creation(self):
        """测试任务创建"""
        print("\n🎯 测试任务创建...")
        
        # 确保有足够的用户进行测试
        if len(self.test_users) < 2:
            print("⚠️ 用户数量不足，跳过部分任务创建测试")
            return
        
        # 获取用户
        admin_user = None
        annotator_user = None
        
        for username, user in self.test_users.items():
            if user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN] and not admin_user:
                admin_user = user
            elif user.role == UserRole.ANNOTATOR and not annotator_user:
                annotator_user = user
        
        if not admin_user:
            admin_user = list(self.test_users.values())[0]
        if not annotator_user:
            annotator_user = list(self.test_users.values())[-1]
        
        # 测试1: 管理员创建完整任务
        if len(self.test_files) >= 3:
            doc_files = list(self.test_files.values())[:2]  # 取前两个文档文件
            template_file = self.test_files.get("test_template.py")
            
            task_create = TaskCreate(
                name="测试任务1",
                description="这是一个测试任务，包含多个文档和模板",
                assignee_id=annotator_user.id,
                documents=[f.file_path for f in doc_files if f.file_type == FileType.DOCUMENT],
                template_path=template_file.file_path if template_file else None
            )
            
            task1 = self.storage.create_task(task_create, admin_user.id)
            self.test_tasks["task1"] = task1
            print(f"✅ 创建任务1: {task1.name} (ID: {task1.id})")
            print(f"   - 文档数量: {len(task1.documents)}")
            print(f"   - 模板: {task1.template.filename if task1.template else '无'}")
            print(f"   - 进度: {task1.progress.completion_percentage}%")
        
        # 测试2: 标注员创建自己的任务
        doc_files = [f for f in self.test_files.values() if f.file_type == FileType.DOCUMENT]
        if doc_files:
            task_create2 = TaskCreate(
                name="标注员任务",
                description="标注员自己创建的任务",
                documents=[doc_files[-1].file_path]  # 使用最后一个文档
            )
            
            task2 = self.storage.create_task(task_create2, annotator_user.id)
            self.test_tasks["task2"] = task2
            print(f"✅ 创建任务2: {task2.name} (ID: {task2.id})")
        
        # 测试3: 创建无模板任务
        if doc_files:
            task_create3 = TaskCreate(
                name="无模板任务",
                description="测试无模板的任务创建",
                assignee_id=annotator_user.id,
                documents=[doc_files[0].file_path]
            )
            
            task3 = self.storage.create_task(task_create3, admin_user.id)
            self.test_tasks["task3"] = task3
            print(f"✅ 创建任务3: {task3.name} (ID: {task3.id})")
    
    def test_task_query(self):
        """测试任务查询"""
        print("\n🔍 测试任务查询...")
        
        # 测试1: 获取所有任务
        query1 = TaskQuery(page=1, page_size=10)
        result1 = self.storage.get_tasks_with_query(query1)
        print(f"✅ 查询所有任务: 总数 {result1.total}, 当前页 {len(result1.tasks)} 个")
        
        # 测试2: 按状态筛选
        query2 = TaskQuery(status=TaskStatus.PENDING, page=1, page_size=10)
        result2 = self.storage.get_tasks_with_query(query2)
        print(f"✅ 查询待处理任务: {len(result2.tasks)} 个")
        
        # 测试3: 按分配人筛选
        if self.test_users:
            annotator_user = None
            for user in self.test_users.values():
                if user.role == UserRole.ANNOTATOR:
                    annotator_user = user
                    break
            
            if annotator_user:
                query3 = TaskQuery(assignee_id=annotator_user.id, page=1, page_size=10)
                result3 = self.storage.get_tasks_with_query(query3)
                print(f"✅ 查询{annotator_user.username}的任务: {len(result3.tasks)} 个")
        
        # 测试4: 搜索任务
        query4 = TaskQuery(search="测试", page=1, page_size=10)
        result4 = self.storage.get_tasks_with_query(query4)
        print(f"✅ 搜索包含'测试'的任务: {len(result4.tasks)} 个")
        
        # 测试5: 分页测试
        query5 = TaskQuery(page=1, page_size=2)
        result5 = self.storage.get_tasks_with_query(query5)
        print(f"✅ 分页测试: 总页数 {result5.total_pages}, 当前页 {result5.page}")
    
    def test_task_statistics(self):
        """测试任务统计"""
        print("\n📊 测试任务统计...")
        
        # 测试1: 全局统计
        stats = self.storage.get_task_statistics()
        print(f"✅ 全局统计:")
        print(f"   - 总任务数: {stats.total_tasks}")
        print(f"   - 待处理: {stats.pending_tasks}")
        print(f"   - 进行中: {stats.in_progress_tasks}")
        print(f"   - 已完成: {stats.completed_tasks}")
        
        # 测试2: 用户统计
        if self.test_users:
            annotator_user = None
            for user in self.test_users.values():
                if user.role == UserRole.ANNOTATOR:
                    annotator_user = user
                    break
            
            if annotator_user:
                user_stats = self.storage.get_task_statistics(annotator_user.id)
                print(f"✅ {annotator_user.username}统计:")
                print(f"   - 我的任务: {user_stats.my_tasks}")
    
    def test_document_status_update(self):
        """测试文档状态更新"""
        print("\n📝 测试文档状态更新...")
        
        if not self.test_tasks:
            print("⚠️ 没有可用的测试任务，跳过文档状态更新测试")
            return
        
        task = list(self.test_tasks.values())[0]  # 使用第一个任务
        if task.documents:
            doc = task.documents[0]
            
            # 更新文档状态为进行中
            updated_task = self.storage.update_document_status(
                task.id, doc.id, DocumentStatus.IN_PROGRESS
            )
            print(f"✅ 更新文档状态为进行中")
            print(f"   - 任务状态: {updated_task.status}")
            print(f"   - 完成进度: {updated_task.progress.completion_percentage}%")
            
            # 更新文档状态为已完成
            updated_task = self.storage.update_document_status(
                task.id, doc.id, DocumentStatus.COMPLETED
            )
            print(f"✅ 更新文档状态为已完成")
            print(f"   - 任务状态: {updated_task.status}")
            print(f"   - 完成进度: {updated_task.progress.completion_percentage}%")
            
            # 如果有第二个文档，也完成它
            if len(task.documents) > 1:
                doc2 = task.documents[1]
                updated_task = self.storage.update_document_status(
                    task.id, doc2.id, DocumentStatus.COMPLETED
                )
                print(f"✅ 完成第二个文档")
                print(f"   - 任务状态: {updated_task.status}")
                print(f"   - 完成进度: {updated_task.progress.completion_percentage}%")
    
    def test_task_update(self):
        """测试任务更新"""
        print("\n✏️ 测试任务更新...")
        
        if not self.test_tasks:
            print("⚠️ 没有可用的测试任务，跳过任务更新测试")
            return
        
        task = list(self.test_tasks.values())[0]  # 使用第一个任务
        
        # 获取一个标注员用户
        annotator_user = None
        for user in self.test_users.values():
            if user.role == UserRole.ANNOTATOR:
                annotator_user = user
                break
        
        if not annotator_user:
            annotator_user = list(self.test_users.values())[0]
        
        # 更新任务信息
        update_data = {
            "name": "更新后的任务",
            "description": "任务描述已更新",
            "assignee_id": annotator_user.id
        }
        
        updated_task = self.storage.update_task(task.id, update_data)
        print(f"✅ 更新任务信息")
        print(f"   - 新名称: {updated_task.name}")
        print(f"   - 新分配人: {updated_task.assignee_id}")
        print(f"   - 更新时间: {updated_task.updated_at}")
    
    def test_template_validation(self):
        """测试模板验证"""
        print("\n🔍 测试模板验证...")
        
        template_file = self.test_files.get("test_template.py")
        if not template_file:
            print("⚠️ 没有可用的模板文件，跳过模板验证测试")
            return
        
        template_path = template_file.file_path
        validation_result = self.storage.validate_python_template(template_path)
        
        print(f"✅ 模板验证结果:")
        print(f"   - 有效性: {validation_result.get('valid')}")
        if validation_result.get('valid'):
            schema = validation_result.get('schema', {})
            print(f"   - 字段数量: {len(schema.get('properties', {}))}")
            print(f"   - 必填字段: {schema.get('required', [])}")
        else:
            print(f"   - 错误信息: {validation_result.get('error')}")
    
    def test_task_deletion(self):
        """测试任务删除"""
        print("\n🗑️ 测试任务删除...")
        
        if not self.test_users or not self.test_files:
            print("⚠️ 没有可用的用户或文件，跳过任务删除测试")
            return
        
        # 获取管理员用户
        admin_user = None
        for user in self.test_users.values():
            if user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
                admin_user = user
                break
        
        if not admin_user:
            admin_user = list(self.test_users.values())[0]
        
        # 获取文档文件
        doc_files = [f for f in self.test_files.values() if f.file_type == FileType.DOCUMENT]
        if not doc_files:
            print("⚠️ 没有可用的文档文件，跳过任务删除测试")
            return
        
        # 创建一个临时任务用于删除测试
        temp_task_create = TaskCreate(
            name="临时任务",
            description="用于删除测试的临时任务",
            documents=[doc_files[0].file_path]
        )
        
        temp_task = self.storage.create_task(temp_task_create, admin_user.id)
        print(f"✅ 创建临时任务: {temp_task.id}")
        
        # 删除任务
        success = self.storage.delete_task(temp_task.id)
        print(f"✅ 删除任务结果: {success}")
        
        # 验证任务已删除
        deleted_task = self.storage.get_task_by_id(temp_task.id)
        print(f"✅ 验证删除: 任务是否存在 {deleted_task is not None}")
    
    def display_final_status(self):
        """显示最终状态"""
        print("\n📋 最终状态总览...")
        
        all_tasks = self.storage.get_all_tasks()
        print(f"📊 任务总数: {len(all_tasks)}")
        
        for task in all_tasks:
            print(f"\n🎯 任务: {task.name}")
            print(f"   - ID: {task.id}")
            print(f"   - 状态: {task.status}")
            print(f"   - 创建者: {task.creator_id}")
            print(f"   - 分配给: {task.assignee_id or '未分配'}")
            print(f"   - 文档数: {len(task.documents)}")
            print(f"   - 进度: {task.progress.completion_percentage}%")
            if task.template:
                print(f"   - 模板: {task.template.filename}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始任务管理功能测试\n")
        
        try:
            self.setup_test_data()
            self.test_task_creation()
            self.test_task_query()
            self.test_task_statistics()
            self.test_document_status_update()
            self.test_task_update()
            self.test_template_validation()
            self.test_task_deletion()
            self.display_final_status()
            
            print("\n🎉 所有测试完成！")
            
        except Exception as e:
            print(f"\n❌ 测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    print("=" * 60)
    print("🎯 任务管理功能测试 - 第五阶段")
    print("=" * 60)
    
    tester = TaskManagementTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main() 