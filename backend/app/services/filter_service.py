from typing import List, Dict, Any, Optional, Callable
from sqlalchemy.orm import Session
from app.models.document import Document
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class FilterService:
    """数据过滤服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.filters = {}
        self._register_default_filters()
    
    def _register_default_filters(self):
        """注册默认的过滤器"""
        # 按省份筛选
        self.register_filter('province', self.create_province_filter)
        
        # 按案件类型筛选
        self.register_filter('case_type', self.create_case_type_filter)
        
        # 按审级筛选
        self.register_filter('level', self.create_level_filter)
        
        # 按日期范围筛选
        self.register_filter('date_range', self.create_date_range_filter)
        
        # 按案由筛选
        self.register_filter('case_reason', self.create_case_reason_filter)
    
    def get_available_files(self) -> List[str]:
        """获取可用的原始文书文件列表"""
        files = []
        for file in os.listdir(self.raw_data_dir):
            if file.endswith('.jsonl'):
                files.append(file)
        return files
    
    def load_documents_from_files(self, file_names: List[str]) -> List[Document]:
        """从指定文件中加载文档"""
        all_documents = []
        for file_name in file_names:
            file_path = os.path.join(self.raw_data_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            doc = json.loads(line.strip())
                            all_documents.append(Document(
                                id=doc.get('s5', ''),
                                content=doc,
                                metadata={
                                    'province': doc.get('s2', '').split('省')[0] + '省' if '省' in doc.get('s2', '') else '',
                                    'case_type': doc.get('s8', ''),
                                    'level': doc.get('s9', ''),
                                    'date': doc.get('s31', ''),
                                    'case_reason': doc.get('s11', [])
                                }
                            ))
                        except json.JSONDecodeError:
                            continue
        return all_documents
    
    def register_filter(self, name: str, filter_func: Callable[[Dict[str, Any]], bool]):
        """注册过滤器"""
        self.filters[name] = filter_func
    
    def apply_filters(self, documents: List[Document], filter_conditions: Dict[str, Any]) -> List[Document]:
        """应用过滤器
        
        Args:
            documents: 文档列表
            filter_conditions: 过滤条件字典，格式如：
                {
                    'province': '广东',
                    'case_type': '刑事案件',
                    'level': '一审',
                    'date_range': {'start': '2022-01-01', 'end': '2022-12-31'},
                    'case_reason': '交通事故'
                }
        """
        filtered_docs = documents
        for filter_name, filter_value in filter_conditions.items():
            if filter_name in self.filters:
                if filter_name == 'date_range':
                    filtered_docs = [
                        doc for doc in filtered_docs 
                        if self.filters[filter_name](doc.content, filter_value['start'], filter_value['end'])
                    ]
                else:
                    filtered_docs = [
                        doc for doc in filtered_docs 
                        if self.filters[filter_name](doc.content, filter_value)
                    ]
        return filtered_docs
    
    def create_province_filter(self, doc: Dict[str, Any], province: str) -> bool:
        """创建省份过滤器"""
        return province in doc.get('s2', '')
    
    def create_case_type_filter(self, doc: Dict[str, Any], case_type: str) -> bool:
        """创建案件类型过滤器"""
        return doc.get('s8', '') == case_type
    
    def create_level_filter(self, doc: Dict[str, Any], level: str) -> bool:
        """创建审级过滤器"""
        return doc.get('s9', '') == level
    
    def create_date_range_filter(self, doc: Dict[str, Any], start_date: str, end_date: str) -> bool:
        """创建日期范围过滤器"""
        case_date = doc.get('s31', '')
        return start_date <= case_date <= end_date
    
    def create_case_reason_filter(self, doc: Dict[str, Any], case_reason: str) -> bool:
        """创建案由过滤器"""
        case_reasons = doc.get('s11', [])
        return case_reason in case_reasons
    
    def save_filtered_documents(self, documents: List[Document], output_file: str):
        """保存过滤后的文档"""
        output_path = os.path.join(self.raw_data_dir, output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            for doc in documents:
                f.write(json.dumps(doc.content, ensure_ascii=False) + '\n')
        return output_path
    
    def create_custom_filter(self, field: str, value: Any, operator: str = 'eq') -> Callable[[Dict[str, Any]], bool]:
        """创建自定义过滤器
        
        Args:
            field: 字段名
            value: 过滤值
            operator: 操作符，支持 eq(等于), ne(不等于), gt(大于), lt(小于), 
                     ge(大于等于), le(小于等于), in(包含), nin(不包含)
        """
        def filter_func(doc: Dict[str, Any]) -> bool:
            field_value = doc.get(field)
            if operator == 'eq':
                return field_value == value
            elif operator == 'ne':
                return field_value != value
            elif operator == 'gt':
                return field_value > value
            elif operator == 'lt':
                return field_value < value
            elif operator == 'ge':
                return field_value >= value
            elif operator == 'le':
                return field_value <= value
            elif operator == 'in':
                return value in field_value
            elif operator == 'nin':
                return value not in field_value
            return False
        return filter_func
    
    def create_combined_filter(self, conditions: List[Dict[str, Any]]) -> Callable[[Dict[str, Any]], bool]:
        """创建组合过滤器
        
        Args:
            conditions: 条件列表，每个条件是一个字典，包含：
                       - field: 字段名
                       - value: 过滤值
                       - operator: 操作符
                       - logic: 逻辑关系(and/or)
        """
        def filter_func(doc: Dict[str, Any]) -> bool:
            result = True
            for condition in conditions:
                field = condition.get('field')
                value = condition.get('value')
                operator = condition.get('operator', 'eq')
                logic = condition.get('logic', 'and')
                
                # 创建单个条件的过滤器
                single_filter = self.create_custom_filter(field, value, operator)
                
                # 应用逻辑关系
                if logic == 'and':
                    result = result and single_filter(doc)
                elif logic == 'or':
                    result = result or single_filter(doc)
            
            return result
        return filter_func

    def filter_documents(self, filter_criteria: Dict[str, Any]) -> List[Document]:
        """
        根据过滤条件筛选文书
        
        Args:
            filter_criteria: 过滤条件字典，例如：
            {
                "court": "北京市第一中级人民法院",
                "case_type": "刑事案件",
                "date_range": {
                    "start": "2022-01-01",
                    "end": "2022-12-31"
                }
            }
        """
        try:
            query = self.db.query(Document)
            
            # 处理法院过滤
            if "court" in filter_criteria:
                query = query.filter(Document.court == filter_criteria["court"])
            
            # 处理案件类型过滤
            if "case_type" in filter_criteria:
                query = query.filter(Document.case_type == filter_criteria["case_type"])
            
            # 处理日期范围过滤
            if "date_range" in filter_criteria:
                date_range = filter_criteria["date_range"]
                if "start" in date_range:
                    query = query.filter(Document.judgment_date >= date_range["start"])
                if "end" in date_range:
                    query = query.filter(Document.judgment_date <= date_range["end"])
            
            # 处理内容过滤
            if "content_filters" in filter_criteria:
                for field, value in filter_criteria["content_filters"].items():
                    # 使用JSON字段查询
                    query = query.filter(Document.content[field].astext == value)
            
            # 处理状态过滤
            if "status" in filter_criteria:
                query = query.filter(Document.status == filter_criteria["status"])
            
            # 处理标注状态过滤
            if "is_annotated" in filter_criteria:
                query = query.filter(Document.is_annotated == filter_criteria["is_annotated"])
            if "is_ai_reviewed" in filter_criteria:
                query = query.filter(Document.is_ai_reviewed == filter_criteria["is_ai_reviewed"])
            
            return query.all()
            
        except Exception as e:
            logger.error(f"过滤文书时发生错误: {str(e)}")
            raise

    def get_filter_options(self) -> Dict[str, List[str]]:
        """
        获取可用的过滤选项
        """
        try:
            # 获取所有法院
            courts = [court[0] for court in self.db.query(Document.court).distinct().all()]
            
            # 获取所有案件类型
            case_types = [case_type[0] for case_type in self.db.query(Document.case_type).distinct().all()]
            
            return {
                "courts": courts,
                "case_types": case_types,
                "statuses": ["raw", "processed", "annotated"],
                "date_ranges": {
                    "min_date": self.db.query(Document.judgment_date).order_by(Document.judgment_date).first()[0],
                    "max_date": self.db.query(Document.judgment_date).order_by(Document.judgment_date.desc()).first()[0]
                }
            }
        except Exception as e:
            logger.error(f"获取过滤选项时发生错误: {str(e)}")
            raise 