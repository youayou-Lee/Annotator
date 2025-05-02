from typing import Dict, Any, List, Optional
from ..models.document import Document
from ..models.task import Task
import json
import os
from datetime import datetime

class AnnotatorService:
    """标注器服务"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

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
    
    def save_annotation(self, task_id: str, document_id: str, annotation: Dict[str, Any]) -> bool:
        """保存标注结果"""
        try:
            # 获取文档保存路径
            doc_dir = os.path.join(self.output_dir, task_id)
            os.makedirs(doc_dir, exist_ok=True)
            
            # 获取原始文档
            task_docs = self._get_task_documents(task_id)
            if not task_docs:
                return False
                
            doc = next((d for d in task_docs if d.get('id') == document_id), None)
            if not doc:
                return False
                
            # 加载已有的标注（如果存在）
            annotation_path = os.path.join(doc_dir, f"{document_id}_annotation.json")
            if os.path.exists(annotation_path):
                with open(annotation_path, 'r', encoding='utf-8') as f:
                    existing_doc = json.load(f)
                    doc = existing_doc  # 使用已有的标注文档作为基础

            # 更新文档中的字段
            for field_name, value in annotation.items():
                # 递归查找并更新字段
                container, name, found = self._find_field_in_document(doc, field_name)
                if found:
                    # 如果找到了字段，直接更新其值
                    container[name] = value
                else:
                    # 如果没有找到，作为顶层字段添加
                    doc[field_name] = value

            # 保存更新后的文档
            with open(annotation_path, 'w', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"保存标注失败: {str(e)}")
            return False

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

    def _get_task_documents(self, task_id: str) -> List[Dict[str, Any]]:
        """从任务文件中获取所有文档"""
        try:
            task_file = os.path.join("data", "tasks", f"{task_id}.json")
            if not os.path.exists(task_file):
                return None
            
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
                return task_data.get('documents', [])
        except Exception as e:
            print(f"获取任务文档失败: {str(e)}")
            return None
    
    def load_annotation(self, task_id: str, document_id: str) -> Optional[Dict[str, Any]]: 
        """加载标注结果，并将标注内容合并到原始文档中"""
        try:
            # 获取原始文档
            doc_path = os.path.join("data", "raw", "upload", f"{document_id}.json")
            if not os.path.exists(doc_path):
                # 如果单独的文档文件不存在，尝试从任务文件中获取
                task_docs = self._get_task_documents(task_id)
                if not task_docs:
                    return None
                doc = next((d for d in task_docs if d.get('id') == document_id), None)
                if not doc:
                    return None
            else:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    doc = json.load(f)

            # 加载标注文件
            task_dir = os.path.join(self.output_dir, task_id)
            annotation_path = os.path.join(task_dir, f"{document_id}_annotation.json")
            
            if not os.path.exists(annotation_path):
                return doc
            
            # 读取标注内容
            with open(annotation_path, 'r', encoding='utf-8') as f:
                annotation = json.load(f)
                
            # 将标注内容合并到原始文档中
            for field_path, value in annotation.items():
                # 对于没有明确路径的字段，在文档中搜索已存在的位置
                if '.' not in field_path:
                    container, name, found = self._find_field_in_document(doc, field_path)
                    if found:
                        container[name] = value
                else:
                    # 处理带路径的字段
                    parts = field_path.split('.')
                    current = doc
                    
                    # 遍历路径
                    for i, part in enumerate(parts[:-1]):
                        if part.isdigit():
                            idx = int(part)
                            if not isinstance(current, list):
                                current = []
                            while len(current) <= idx:
                                current.append({})
                            current = current[idx]
                        else:
                            if part not in current:
                                current[part] = {}
                            current = current[part]
                    
                    # 设置最终值
                    last_part = parts[-1]
                    if last_part.isdigit():
                        idx = int(last_part)
                        if not isinstance(current, list):
                            current = []
                        while len(current) <= idx:
                            current.append(None)
                        current[idx] = value
                    else:
                        current[last_part] = value
                        
            return doc
                
        except Exception as e:
            print(f"加载标注失败: {str(e)}")
            return None
    
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