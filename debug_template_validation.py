#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试模板验证功能
"""

import sys
from pathlib import Path

def debug_template_validation():
    print("🔍 调试模板验证功能...")
    
    # 添加项目根目录到Python路径
    project_root = Path('.').absolute()
    print(f"项目根目录: {project_root}")
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    try:
        from simple_document_validator import SimpleDocumentValidator
        print("✅ 简化版文档校验模块导入成功")
        
        # 测试模板文件
        template_path = "backend/data/public_files/templates/20250602_151605_complex_template.py"
        full_path = Path(template_path)
        
        print(f"模板文件路径: {template_path}")
        print(f"完整路径: {full_path.absolute()}")
        print(f"文件存在: {full_path.exists()}")
        
        if full_path.exists():
            print("✅ 模板文件存在")
            
            try:
                validator = SimpleDocumentValidator(str(full_path))
                print("✅ 创建验证器成功")
                
                if validator.main_model:
                    print(f"✅ 模板解析成功: {validator.main_model.__name__}")
                    
                    try:
                        schema = validator.get_annotation_schema()
                        print(f"✅ 获取标注字段配置成功，字段数量: {len(schema)}")
                        
                        # 显示前几个字段
                        for i, field in enumerate(schema[:3]):
                            print(f"  字段{i+1}: {field}")
                            
                    except Exception as e:
                        print(f"❌ 获取标注字段配置失败: {e}")
                        import traceback
                        traceback.print_exc()
                        
                else:
                    print("❌ 模板解析失败，main_model为空")
                    
            except Exception as e:
                print(f"❌ 创建验证器失败: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print("❌ 模板文件不存在")
            
            # 列出模板目录中的文件
            template_dir = Path("backend/data/public_files/templates")
            if template_dir.exists():
                print(f"模板目录内容:")
                for file in template_dir.iterdir():
                    print(f"  - {file.name}")
            else:
                print("模板目录不存在")
                
    except Exception as e:
        print(f"❌ 导入简化版文档校验模块失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_template_validation() 