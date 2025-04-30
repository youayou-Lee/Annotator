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
        task_dir = os.path.join(self.output_dir, task_id)
        if not os.path.exists(task_dir):
            return False
        
        # 保存标注结果
        annotation_path = os.path.join(task_dir, f"{document_id}_annotation.json")
        with open(annotation_path, 'w', encoding='utf-8') as f:
            json.dump(annotation, f, ensure_ascii=False, indent=2)
        
        return True
    
    def load_annotation(self, task_id: str, document_id: str) -> Optional[Dict[str, Any]]:
        """加载标注结果"""
        task_dir = os.path.join(self.output_dir, task_id)
        annotation_path = os.path.join(task_dir, f"{document_id}_annotation.json")
        
        if not os.path.exists(annotation_path):
            return None
        
        with open(annotation_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
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