from typing import Dict, Any, List, Optional
from ..models.task import Task
import json
import os
from datetime import datetime

class AnnotatorService:
    """标注器服务"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _find_field_in_document(self, doc: Dict[str, Any], field_name: str) -> tuple[Dict[str, Any], str, bool]:
        """递归搜索文档中的字段
        
        Args:
            doc: 要搜索的文档或文档的一部分
            field_name: 要查找的字段名
            
        Returns:
            tuple: (包含该字段的字典, 字段名, 是否找到)
        """
        # 如果当前层级直接包含该字段，返回当前字典
        if field_name in doc:
            return doc, field_name, True
            
        # 递归搜索所有字典和列表
        for key, value in doc.items():
            if isinstance(value, dict):
                container, name, found = self._find_field_in_document(value, field_name)
                if found:
                    return container, name, True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        container, name, found = self._find_field_in_document(item, field_name)
                        if found:
                            return container, name, True
                            
        return doc, field_name, False

    def create_annotation_task(self, task: Task) -> str:
        """创建标注任务"""
        task_dir = os.path.join(self.output_dir, task.id)
        os.makedirs(task_dir, exist_ok=True)
        
        # 创建任务配置文件
        task_config = {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "document_ids": task.document_ids,
            "config": task.config,
            "created_at": datetime.now().isoformat()
        }
        
        config_path = os.path.join(task_dir, "task_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(task_config, f, ensure_ascii=False, indent=2)
        
        return task_dir
    
    def save_annotation(self, task_id: str, document_id: str, annotation: Dict[str, Any]) -> Optional[str]:
        """保存标注结果"""
        try:
            # 创建标注目录
            doc_dir = os.path.join(self.output_dir, task_id)
            os.makedirs(doc_dir, exist_ok=True)
            
            # 获取原始文档数据
            task_file = os.path.join("data", "tasks", f"{task_id}.json")
            if not os.path.exists(task_file):
                print(f"Warning: Task file {task_file} not found during save_annotation for task {task_id}.")
                annotation_data = annotation
            else:
                # 构建完整的标注数据
                annotation_data = annotation
            
            annotation_path = os.path.join(doc_dir, f"{document_id}_annotation.json")
            
            # 检查是否已有标注文件，如果有，合并而不是覆盖
            if os.path.exists(annotation_path):
                try:
                    with open(annotation_path, 'r', encoding='utf-8') as f:
                        existing_annotation = json.load(f)
                        # 深度合并现有标注和新标注
                        for field_name, value in annotation.items():
                            existing_annotation[field_name] = value
                    annotation_data = existing_annotation
                except Exception as e:
                    print(f"读取已有标注失败: {str(e)}，将使用新标注")
            
            with open(annotation_path, 'w', encoding='utf-8') as f:
                json.dump(annotation_data, f, ensure_ascii=False, indent=2)
            
            # 打印保存成功信息和保存的数据，以便调试
            print(f"标注保存成功：{annotation_path}")
            print(f"保存的数据：{json.dumps(annotation_data, ensure_ascii=False)[:200]}...")
            
            return annotation_path
            
        except Exception as e:
            print(f"保存标注失败: {str(e)}")
            return None

    def _get_path_to_field(self, doc: Dict[str, Any], field_name: str, current_path: List[str] = None) -> List[str]:
        """获取文档中字段的路径
        
        Args:
            doc: 文档或文档的一部分
            field_name: 要查找的字段名
            current_path: 当前路径
            
        Returns:
            List[str]: 从根到字段的路径列表
        """
        if current_path is None:
            current_path = []
            
        if field_name in doc:
            return current_path + [field_name]
            
        for key, value in doc.items():
            if isinstance(value, dict):
                result = self._get_path_to_field(value, field_name, current_path + [key])
                if result:
                    return result
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        result = self._get_path_to_field(item, field_name, current_path + [key, str(i)])
                        if result:
                            return result
        return None

    def load_annotation(self, task_id: str, document_id: str, original_document_content: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]: 
        """加载标注结果，并将标注内容合并到原始文档中 (如果提供)."""
        try:
            # 使用原始文档的深拷贝，如果提供了原始文档
            doc_to_merge_into = None
            if original_document_content:
                doc_to_merge_into = json.loads(json.dumps(original_document_content))

            annotation_file_path = os.path.join(self.output_dir, task_id, f"{document_id}_annotation.json")
            
            if not os.path.exists(annotation_file_path):
                return doc_to_merge_into 
            
            with open(annotation_file_path, 'r', encoding='utf-8') as f:
                annotation_data = json.load(f)
                
            if doc_to_merge_into is None:
                return annotation_data

            # 合并标注数据到原始文档
            for field_name, value in annotation_data.items():
                # 直接将标注字段添加到原始文档中
                # 这样标注数据会优先替换原始数据
                doc_to_merge_into[field_name] = value

                # 递归处理复杂字段结构的情况
                if isinstance(value, dict) and field_name in doc_to_merge_into:
                    self._merge_nested_fields(doc_to_merge_into[field_name], value)
                
            return doc_to_merge_into
                
        except Exception as e:
            print(f"加载标注或合并失败: {str(e)}")
            return None 
    
    def _merge_nested_fields(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """递归合并嵌套字段
        
        Args:
            target: 目标字典（原始文档的字段）
            source: 源字典（标注数据的字段）
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                # 递归合并嵌套字典
                self._merge_nested_fields(target[key], value)
            elif isinstance(value, list) and key in target and isinstance(target[key], list):
                # 合并列表，优先保留标注的值
                if len(value) <= len(target[key]):
                    for i, item in enumerate(value):
                        if isinstance(item, dict) and isinstance(target[key][i], dict):
                            self._merge_nested_fields(target[key][i], item)
                        else:
                            target[key][i] = item
                else:
                    # 如果标注列表更长，直接替换
                    target[key] = value
            else:
                # 直接替换其他类型的值
                target[key] = value

    def validate_annotation(self, annotation: Dict[str, Any], template: Dict[str, Any]) -> bool:
        """验证标注结果"""
        for key, value_type in template.items():
            if key not in annotation:
                return False
            
            # 验证类型
            if value_type == "string" and not isinstance(annotation[key], str):
                return False
            elif value_type == "number" and not isinstance(annotation[key], (int, float)):
                return False
            elif value_type == "boolean" and not isinstance(annotation[key], bool):
                return False
            elif value_type == "array" and not isinstance(annotation[key], list):
                return False
            elif value_type == "object" and not isinstance(annotation[key], dict):
                return False
        
        return True