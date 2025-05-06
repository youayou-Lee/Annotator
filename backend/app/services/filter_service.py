from typing import List, Dict, Any, Optional, Callable
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FilterService:
    """数据过滤服务"""
    
    def __init__(self, raw_data_dir=os.path.join("backend", "data", "oringinal_data")):
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(raw_data_dir):
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 回到项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            self.raw_data_dir = os.path.join(project_root, raw_data_dir)
        else:
            self.raw_data_dir = raw_data_dir
        
        self.filters = {}
        self._register_default_filters()
    
    def _register_default_filters(self):
        """注册默认的过滤器"""
        self.filters = {
            'court': lambda doc, value: doc.get('court') == value,
            'case_type': lambda doc, value: doc.get('case_type') == value,
            'content_filters': lambda doc, filters: self._check_content_filters(doc, filters)
        }
    


    def _check_content_filters(self, doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """检查文档内容是否匹配所有过滤条件"""
        for field, value in filters.items():
            if doc.get(field) != value:
                return False
        return True

    def get_available_files(self) -> List[str]:
        """获取可用的原始文书文件列表"""
        files = []
        try:
            for file in os.listdir(self.raw_data_dir):
                if file.endswith('.jsonl') or file.endswith('.json'):
                    files.append(file)
        except Exception as e:
            logger.error(f"获取文件列表失败: {str(e)}")
        return files

    def load_and_filter_documents(self, file_names: List[str], filter_conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从文件加载并过滤文档"""
        filtered_docs = []
        
        for file_name in file_names:
            file_path = os.path.join(self.raw_data_dir, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        doc = json.loads(line.strip())
                        if self._matches_all_conditions(doc, filter_conditions):
                            filtered_docs.append(doc)
            except Exception as e:
                logger.error(f"处理文件 {file_name} 时发生错误: {str(e)}")
                continue
        
        return filtered_docs


# 这个地方逻辑有问题，应该是在所有的json对象里进行筛选，而非是对jsonl文件进行筛选
    def _matches_all_conditions(self, doc: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """检查文档是否匹配所有过滤条件"""
        for field, value in conditions.items():
            if field == 'date_range' and value:
                if not self.filters['date_range'](doc, value.get('start'), value.get('end')):
                    return False
            elif field == 'content_filters' and value:
                if not self.filters['content_filters'](doc, value):
                    return False
            elif field in self.filters and value is not None:
                if not self.filters[field](doc, value):
                    return False
        return True

    def save_filtered_documents(self, documents: List[Dict[str, Any]], output_file: str) -> str:
        """保存过滤后的文档到新的 jsonl 文件"""
        output_dir = os.path.join(self.raw_data_dir, 'filtered')
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, output_file)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for doc in documents:
                    f.write(json.dumps(doc, ensure_ascii=False) + '\n')
            return output_path
        except Exception as e:
            logger.error(f"保存过滤结果失败: {str(e)}")
            raise