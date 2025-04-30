from typing import Dict, Any, List
from ..models.document import Document
import json
import os
from datetime import datetime

class FormatService:
    """格式化存储服务"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def format_document(self, document: Document, template: Dict[str, Any]) -> Dict[str, Any]:
        """格式化文档"""
        formatted_doc = {}
        for key, value_type in template.items():
            if key in document.content:
                formatted_doc[key] = document.content[key]
            else:
                # 根据类型设置默认值
                if value_type == "string":
                    formatted_doc[key] = ""
                elif value_type == "number":
                    formatted_doc[key] = 0
                elif value_type == "boolean":
                    formatted_doc[key] = False
                elif value_type == "array":
                    formatted_doc[key] = []
                elif value_type == "object":
                    formatted_doc[key] = {}
        return formatted_doc
    
    def save_formatted_documents(self, documents: List[Document], template: Dict[str, Any], filename: str):
        """保存格式化后的文档"""
        formatted_docs = [self.format_document(doc, template) for doc in documents]
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_docs, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def load_formatted_documents(self, filename: str) -> List[Dict[str, Any]]:
        """加载格式化后的文档"""
        input_path = os.path.join(self.output_dir, filename)
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f) 