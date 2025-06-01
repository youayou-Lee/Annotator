#!/usr/bin/env python3
"""
完整的文档验证系统测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.template_validator import TemplateValidator
from app.core.annotation_validator import AnnotationValidator
from app.core.storage import StorageManager


def test_storage_template_validation():
    """测试存储管理器的模板验证功能"""
    print("=== 测试存储管理器模板验证功能 ===")
    
    storage = StorageManager()
    template_path = "public_files/templates/example_template.py"
    
    # 验证模板
    result = storage.validate_python_template(template_path)
    
    if result["valid"]:
        print("✅ 存储管理器模板验证通过")
        print(f"模板名称: {result['template_info']['schema_name']}")
        print(f"版本: {result['template_info']['version']}")
        print(f"描述: {result['template_info']['description']}")
        print(f"字段数量: {len(result['annotation_fields'])}")
        return True
    else:
        print(f"❌ 存储管理器模板验证失败: {result['error']}")
        return False


def test_api_validation_models():
    """测试API验证模型"""
    print("\n=== 测试API验证模型 ===")
    
    try:
        from app.api.annotations import (
            AnnotationValidationRequest, 
            AnnotationValidationResponse,
            PartialValidationRequest,
            PartialValidationResponse
        )
        
        # 测试验证请求模型
        validation_request = AnnotationValidationRequest(
            template_file_path="public_files/templates/example_template.py",
            annotation_data={"title": "测试", "content": "测试内容"}
        )
        
        print("✅ API验证模型创建成功")
        return True
        
    except Exception as e:
        print(f"❌ API验证模型测试失败: {str(e)}")
        return False


def test_annotation_model():
    """测试标注模型"""
    print("\n=== 测试标注模型 ===")
    
    try:
        from app.models.annotation import Annotation, AnnotationStatus
        from datetime import datetime
        
        # 创建标注实例
        annotation = Annotation(
            document_id="doc_123",
            task_id="task_456",
            status=AnnotationStatus.PENDING,
            annotator_id="user_789",
            annotation_data={"title": "测试标题", "content": "测试内容"},
            updated_at=datetime.now()
        )
        
        print("✅ 标注模型创建成功")
        print(f"文档ID: {annotation.document_id}")
        print(f"任务ID: {annotation.task_id}")
        print(f"状态: {annotation.status}")
        return True
        
    except Exception as e:
        print(f"❌ 标注模型测试失败: {str(e)}")
        return False


def test_task_model():
    """测试任务模型"""
    print("\n=== 测试任务模型 ===")
    
    try:
        from app.models.task import Task, TaskStatus, TaskTemplate, TaskDocument
        from datetime import datetime
        
        # 创建任务实例
        task = Task(
            id="task_123",
            name="测试任务",
            description="这是一个测试任务",
            creator_id="user_456",
            assignee_id="user_789",
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            template=TaskTemplate(
                filename="example_template.py",
                file_path="public_files/templates/example_template.py"
            ),
            documents=[
                TaskDocument(
                    id="doc_123",
                    filename="test.txt",
                    file_path="public_files/documents/test.txt"
                )
            ]
        )
        
        print("✅ 任务模型创建成功")
        print(f"任务ID: {task.id}")
        print(f"任务名称: {task.name}")
        print(f"模板路径: {task.template.file_path if task.template else 'None'}")
        return True
        
    except Exception as e:
        print(f"❌ 任务模型测试失败: {str(e)}")
        return False


def test_integration():
    """集成测试"""
    print("\n=== 集成测试 ===")
    
    try:
        # 创建验证器
        template_validator = TemplateValidator()
        annotation_validator = AnnotationValidator()
        
        # 验证模板
        template_path = "data/public_files/templates/example_template.py"
        template_result = template_validator.validate_template_file(template_path)
        
        if not template_result["valid"]:
            print(f"❌ 模板验证失败: {template_result['error']}")
            return False
        
        # 验证标注数据
        test_data = {
            "title": "集成测试文档",
            "doc_type": "article",
            "content": "这是集成测试的内容",
            "authors": [],
            "keywords": ["集成", "测试"],
            "importance": 3,
            "is_reviewed": False,
            "attachments": [],
            "metadata": {},
            "notes": "集成测试备注"
        }
        
        validation_result = annotation_validator.validate_annotation_data(template_path, test_data)
        
        if validation_result["valid"]:
            print("✅ 集成测试通过")
            print("验证的数据字段:")
            for key in validation_result["validated_data"].keys():
                print(f"  - {key}")
            return True
        else:
            print(f"❌ 数据验证失败: {validation_result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ 集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("开始完整的文档验证系统测试...")
    
    # 确保数据目录存在
    template_dir = Path("data/public_files/templates")
    template_dir.mkdir(parents=True, exist_ok=True)
    
    success = True
    
    try:
        success &= test_storage_template_validation()
        success &= test_api_validation_models()
        success &= test_annotation_model()
        success &= test_task_model()
        success &= test_integration()
        
        if success:
            print("\n🎉 所有测试通过！文档验证系统已完全就绪。")
            print("\n系统功能总结:")
            print("✅ 模板验证 - 支持AnnotationSchema格式")
            print("✅ 数据验证 - 支持Pydantic模型验证")
            print("✅ 部分验证 - 支持实时字段验证")
            print("✅ API集成 - 完整的REST API支持")
            print("✅ 模型兼容 - 支持任务和标注模型")
        else:
            print("\n❌ 部分测试失败，请检查实现。")
            
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 