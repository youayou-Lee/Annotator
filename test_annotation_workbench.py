#!/usr/bin/env python3
"""
标注工作台功能测试脚本

测试标注工作台的各项功能，包括：
1. 文档列表获取
2. 文档内容获取
3. 表单配置获取
4. 标注数据的保存和获取
5. 实时验证功能
6. 任务进度统计
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class AnnotationWorkbenchTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        """登录获取token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print(f"✅ 登录成功: {username}")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def test_get_documents(self, task_id: str) -> Optional[Dict[str, Any]]:
        """测试获取文档列表"""
        print(f"\n📋 测试获取任务 {task_id} 的文档列表...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/annotations/{task_id}/documents")
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get("documents", [])
                print(f"✅ 获取文档列表成功，共 {len(documents)} 个文档")
                
                for i, doc in enumerate(documents[:3]):  # 只显示前3个
                    print(f"   {i+1}. {doc.get('filename')} - {doc.get('status')}")
                
                return data
            else:
                print(f"❌ 获取文档列表失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取文档列表异常: {e}")
            return None
    
    def test_get_document_content(self, task_id: str, document_id: str) -> Optional[Dict[str, Any]]:
        """测试获取文档内容"""
        print(f"\n📄 测试获取文档内容...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/annotations/{task_id}/documents/{document_id}/content"
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", {})
                print(f"✅ 获取文档内容成功")
                print(f"   内容字段数: {len(content) if isinstance(content, dict) else 'N/A'}")
                
                # 显示部分内容
                if isinstance(content, dict):
                    for key in list(content.keys())[:3]:
                        value = content[key]
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"   {key}: {value}")
                
                return data
            else:
                print(f"❌ 获取文档内容失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取文档内容异常: {e}")
            return None
    
    def test_get_form_config(self, task_id: str, document_id: str) -> Optional[Dict[str, Any]]:
        """测试获取表单配置"""
        print(f"\n📝 测试获取表单配置...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/annotations/{task_id}/documents/{document_id}/form-config"
            )
            
            if response.status_code == 200:
                data = response.json()
                fields = data.get("fields", [])
                print(f"✅ 获取表单配置成功，共 {len(fields)} 个字段")
                
                for field in fields[:5]:  # 只显示前5个字段
                    field_type = field.get("type", "unknown")
                    required = "必填" if field.get("required") else "可选"
                    print(f"   - {field.get('label', field.get('name'))}: {field_type} ({required})")
                
                return data
            else:
                print(f"❌ 获取表单配置失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取表单配置异常: {e}")
            return None
    
    def test_get_annotation(self, task_id: str, document_id: str) -> Optional[Dict[str, Any]]:
        """测试获取标注数据"""
        print(f"\n🏷️ 测试获取标注数据...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/annotations/{task_id}/documents/{document_id}/annotation"
            )
            
            if response.status_code == 200:
                data = response.json()
                annotated_data = data.get("annotated_data", {})
                status = data.get("status", "unknown")
                print(f"✅ 获取标注数据成功")
                print(f"   状态: {status}")
                print(f"   已标注字段数: {len(annotated_data) if isinstance(annotated_data, dict) else 0}")
                
                return data
            else:
                print(f"❌ 获取标注数据失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取标注数据异常: {e}")
            return None
    
    def test_save_annotation(self, task_id: str, document_id: str, annotation_data: Dict[str, Any]) -> bool:
        """测试保存标注数据"""
        print(f"\n💾 测试保存标注数据...")
        
        try:
            payload = {
                "annotated_data": annotation_data,
                "is_auto_save": False
            }
            
            response = self.session.post(
                f"{self.base_url}/api/annotations/{task_id}/documents/{document_id}/annotation",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 保存标注数据成功")
                print(f"   更新时间: {data.get('updated_at', 'N/A')}")
                return True
            else:
                print(f"❌ 保存标注数据失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 保存标注数据异常: {e}")
            return False
    
    def test_validate_partial(self, task_id: str, document_id: str, partial_data: Dict[str, Any]) -> bool:
        """测试部分数据验证"""
        print(f"\n🔍 测试实时验证...")
        
        try:
            payload = {
                "task_id": task_id,
                "document_id": document_id,
                "partial_data": partial_data,
                "fields": list(partial_data.keys())
            }
            
            response = self.session.post(
                f"{self.base_url}/api/annotations/validate-partial",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                errors = data.get("errors", {})
                is_valid = data.get("is_valid", False)
                
                print(f"✅ 实时验证完成")
                print(f"   验证结果: {'通过' if is_valid else '有错误'}")
                
                if errors:
                    print(f"   错误信息:")
                    for field, error in errors.items():
                        print(f"     {field}: {error}")
                
                return True
            else:
                print(f"❌ 实时验证失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 实时验证异常: {e}")
            return False
    
    def test_get_task_progress(self, task_id: str, current_document_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """测试获取任务进度"""
        print(f"\n📊 测试获取任务进度...")
        
        try:
            params = {}
            if current_document_id:
                params["current_document_id"] = current_document_id
            
            response = self.session.get(
                f"{self.base_url}/api/annotations/{task_id}/progress",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total_documents", 0)
                completed = data.get("completed_documents", 0)
                progress = data.get("progress_percentage", 0)
                
                print(f"✅ 获取任务进度成功")
                print(f"   总文档数: {total}")
                print(f"   已完成: {completed}")
                print(f"   进度: {progress:.1f}%")
                
                return data
            else:
                print(f"❌ 获取任务进度失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取任务进度异常: {e}")
            return None
    
    def test_submit_annotation(self, task_id: str, document_id: str) -> bool:
        """测试提交标注"""
        print(f"\n✅ 测试提交标注...")
        
        try:
            payload = {
                "submit_comment": "测试提交"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/annotations/{task_id}/documents/{document_id}/submit",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 提交标注成功")
                print(f"   状态: {data.get('status', 'N/A')}")
                return True
            else:
                print(f"❌ 提交标注失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 提交标注异常: {e}")
            return False
    
    def run_full_test(self, task_id: str) -> None:
        """运行完整测试流程"""
        print("🚀 开始标注工作台功能测试")
        print("=" * 50)
        
        # 1. 登录
        if not self.login():
            print("❌ 登录失败，终止测试")
            return
        
        # 2. 获取文档列表
        documents_data = self.test_get_documents(task_id)
        if not documents_data:
            print("❌ 无法获取文档列表，终止测试")
            return
        
        documents = documents_data.get("documents", [])
        if not documents:
            print("❌ 文档列表为空，终止测试")
            return
        
        # 选择第一个文档进行测试
        test_document = documents[0]
        document_id = test_document["id"]
        
        print(f"\n🎯 使用文档进行测试: {test_document['filename']}")
        
        # 3. 获取文档内容
        self.test_get_document_content(task_id, document_id)
        
        # 4. 获取表单配置
        form_config = self.test_get_form_config(task_id, document_id)
        
        # 5. 获取现有标注数据
        annotation_data = self.test_get_annotation(task_id, document_id)
        
        # 6. 测试保存标注数据
        if form_config:
            fields = form_config.get("fields", [])
            test_annotation = {}
            
            # 生成测试数据
            for field in fields[:3]:  # 只测试前3个字段
                field_name = field["name"]
                field_type = field["type"]
                
                if field_type == "string":
                    test_annotation[field_name] = f"测试文本_{int(time.time())}"
                elif field_type == "number":
                    test_annotation[field_name] = 42
                elif field_type == "boolean":
                    test_annotation[field_name] = True
                elif field_type == "select" and field.get("options"):
                    test_annotation[field_name] = field["options"][0]["value"]
            
            if test_annotation:
                # 7. 测试实时验证
                self.test_validate_partial(task_id, document_id, test_annotation)
                
                # 8. 测试保存
                self.test_save_annotation(task_id, document_id, test_annotation)
        
        # 9. 获取任务进度
        self.test_get_task_progress(task_id, document_id)
        
        # 注意：不测试提交功能，避免改变文档状态
        # self.test_submit_annotation(task_id, document_id)
        
        print("\n" + "=" * 50)
        print("🎉 标注工作台功能测试完成")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python test_annotation_workbench.py <task_id>")
        print("示例: python test_annotation_workbench.py task_123")
        return
    
    task_id = sys.argv[1]
    
    # 创建测试器并运行测试
    tester = AnnotationWorkbenchTester()
    tester.run_full_test(task_id)

if __name__ == "__main__":
    main() 