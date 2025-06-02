import unittest
import json
import os
from enhanced_validator import EnhancedDocumentValidator

class TestEnhancedDocumentValidator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.validator = EnhancedDocumentValidator("complex_template.py")
        
        # 创建测试数据
        cls.test_data = {
            "id": "test_doc_001",
            "text1": "这是一个测试文档的主要内容，用于验证复杂嵌套结构的标注字段提取功能。",
            "end": 1500,
            "document_info": {
                "title": "测试文档标题",
                "category": "技术文档",
                "metadata": {
                    "author": "测试作者",
                    "publish_date": "2024-01-15",
                    "classification": "内部"
                }
            },
            "content_sections": [
                {
                    "section_id": "intro",
                    "text": "这是介绍章节的内容",
                    "annotations": {
                        "sentiment_score": 0.7,
                        "key_entities": ["测试", "文档"],
                        "importance_level": 4
                    },
                    "subsections": [
                        {
                            "subsection_id": "background",
                            "content": "背景信息内容",
                            "analysis": {
                                "topic": "背景介绍",
                                "confidence": 0.85
                            }
                        }
                    ]
                },
                {
                    "section_id": "main",
                    "text": "这是主要章节的内容",
                    "annotations": {
                        "sentiment_score": 0.9,
                        "key_entities": ["主要内容", "核心"],
                        "importance_level": 5
                    }
                }
            ],
            "statistics": {
                "word_count": 1200,
                "paragraph_count": 6,
                "reading_time": 5
            }
        }

    def test_main_model_loading(self):
        """测试主模型加载"""
        self.assertEqual(self.validator.model.__name__, "ComplexDocumentModel")
        
        # 验证主模型标记
        model_config = getattr(self.validator.model, "model_config", {})
        json_schema_extra = model_config.get("json_schema_extra", {})
        self.assertTrue(json_schema_extra.get("is_main_model", False))

    def test_annotation_fields_extraction(self):
        """测试复杂嵌套结构的标注字段提取"""
        fields = self.validator.annotation_fields
        field_paths = {f.path for f in fields}
        
        print("提取到的标注字段路径:")
        for path in sorted(field_paths):
            print(f"  - {path}")
        
        # 验证基础字段
        self.assertIn("text1", field_paths)
        self.assertIn("end", field_paths)
        
        # 验证一级嵌套字段
        self.assertIn("document_info.title", field_paths)
        self.assertIn("document_info.category", field_paths)
        
        # 验证二级嵌套字段
        self.assertIn("document_info.metadata.author", field_paths)
        self.assertIn("document_info.metadata.publish_date", field_paths)
        self.assertIn("document_info.metadata.classification", field_paths)
        
        # 验证列表嵌套字段
        self.assertIn("content_sections[].text", field_paths)
        self.assertIn("content_sections[].annotations.sentiment_score", field_paths)
        self.assertIn("content_sections[].annotations.key_entities", field_paths)
        self.assertIn("content_sections[].annotations.importance_level", field_paths)
        
        # 验证深层嵌套字段
        self.assertIn("content_sections[].subsections[].content", field_paths)
        self.assertIn("content_sections[].subsections[].analysis.topic", field_paths)
        self.assertIn("content_sections[].subsections[].analysis.confidence", field_paths)
        
        # 验证非标注字段不被提取
        self.assertNotIn("id", field_paths)
        self.assertNotIn("statistics.word_count", field_paths)

    def test_field_types_and_constraints(self):
        """测试字段类型和约束提取"""
        fields = {f.path: f for f in self.validator.annotation_fields}
        
        # 测试基础类型
        text1_field = fields["text1"]
        self.assertEqual(text1_field.type_.__name__, "str")
        self.assertTrue(text1_field.is_required)
        
        # 测试数值类型和约束
        end_field = fields["end"]
        self.assertEqual(end_field.type_.__name__, "int")
        self.assertEqual(end_field.constraints.get("ge"), 0)
        
        # 测试浮点数约束
        sentiment_field = fields["content_sections[].annotations.sentiment_score"]
        self.assertEqual(sentiment_field.type_.__name__, "float")
        self.assertEqual(sentiment_field.constraints.get("ge"), -1.0)
        self.assertEqual(sentiment_field.constraints.get("le"), 1.0)

    def test_document_validation(self):
        """测试文档验证"""
        result = self.validator.validate_document(self.test_data)
        self.assertTrue(result["valid"])
        self.assertIn("instance", result)

    def test_annotation_extraction(self):
        """测试标注字段值提取"""
        annotations = self.validator.extract_annotations(self.test_data)
        
        print("提取到的标注字段值:")
        for key, value in annotations.items():
            print(f"  {key}: {value}")
        
        # 验证基础字段
        self.assertEqual(annotations["text1"], "这是一个测试文档的主要内容，用于验证复杂嵌套结构的标注字段提取功能。")
        self.assertEqual(annotations["end"], 1500)
        
        # 验证嵌套字段
        self.assertEqual(annotations["document_info.title"], "测试文档标题")
        self.assertEqual(annotations["document_info.category"], "技术文档")
        self.assertEqual(annotations["document_info.metadata.author"], "测试作者")
        
        # 验证列表字段
        self.assertEqual(annotations["content_sections[].text"], 
                        ["这是介绍章节的内容", "这是主要章节的内容"])
        self.assertEqual(annotations["content_sections[].annotations.sentiment_score"], 
                        [0.7, 0.9])
        self.assertEqual(annotations["content_sections[].annotations.key_entities"], 
                        [["测试", "文档"], ["主要内容", "核心"]])
        
        # 验证深层嵌套字段
        self.assertEqual(annotations["content_sections[].subsections[].content"], 
                        [["背景信息内容"]])  # 只有第一个section有subsections
        self.assertEqual(annotations["content_sections[].subsections[].analysis.topic"], 
                        [["背景介绍"]])  # 只有第一个section有subsections

    def test_schema_generation(self):
        """测试模式信息生成"""
        schema = self.validator.get_annotation_schema()
        
        print("标注字段模式信息:")
        for field_info in schema:
            print(f"  路径: {field_info['path']}")
            print(f"    类型: {field_info['type']}")
            print(f"    必需: {field_info['required']}")
            print(f"    描述: {field_info['description']}")
            print(f"    约束: {field_info['constraints']}")
            print()
        
        # 验证模式信息完整性
        self.assertGreater(len(schema), 10)  # 应该有多个标注字段
        
        # 验证特定字段的模式信息
        text1_schema = next(f for f in schema if f['path'] == 'text1')
        self.assertEqual(text1_schema['type'], 'str')
        self.assertTrue(text1_schema['required'])
        self.assertEqual(text1_schema['description'], '主要文本内容')

    def test_file_validation(self):
        """测试文件验证功能"""
        # 创建测试文件
        test_file_data = [self.test_data]
        
        with open("test_complex.json", "w", encoding="utf-8") as f:
            json.dump(test_file_data, f, ensure_ascii=False, indent=2)
        
        # 测试文件验证
        result = self.validator.validate_file("test_complex.json")
        
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["valid_count"], 1)
        self.assertEqual(result["invalid_count"], 0)
        
        # 清理测试文件
        os.remove("test_complex.json")

    def test_invalid_document(self):
        """测试无效文档处理"""
        invalid_data = {
            "id": "invalid_doc",
            "text1": "",  # 空字符串可能无效
            "end": -1,  # 负数无效
            "document_info": {
                "title": "短",  # 太短
                "category": "测试",
                "metadata": {
                    "author": "作者",
                    # 缺少必需字段
                }
            },
            "content_sections": []  # 空列表
        }
        
        result = self.validator.validate_document(invalid_data)
        self.assertFalse(result["valid"])
        self.assertIn("errors", result)

if __name__ == "__main__":
    # 设置详细输出
    unittest.main(verbosity=2)