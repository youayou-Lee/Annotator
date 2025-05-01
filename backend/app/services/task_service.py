import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.task import Task, TaskConfig, DataSource, Document, TaskStatus, TaskType
from ..models.task import TaskInDB
from sqlalchemy.orm import Session

class TaskService:
    """任务服务"""
    
    def __init__(self, db: Session, raw_data_dir: str = "data/raw", task_templates_dir: str = "data/task_templates"):
        self.db = db
        self.raw_data_dir = os.path.abspath(raw_data_dir)
        self.task_templates_dir = os.path.abspath(task_templates_dir)
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.task_templates_dir, exist_ok=True)
    
    def load_documents_from_jsonl(self, file_path: str) -> List[Document]:
        """从JSONL文件加载文档
        
        Args:
            file_path: JSONL文件路径
            
        Returns:
            List[Document]: 文档列表
        """
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        content = json.loads(line.strip())
                        doc_id = content.get('s5', '')
                        if not doc_id:
                            print(f"警告: 文档缺少s5字段: {content}")
                            continue
                            
                        doc = Document(
                            id=doc_id,
                            content=content,
                            source_file=os.path.basename(file_path)
                        )
                        documents.append(doc)
                    except json.JSONDecodeError:
                        print(f"警告: 无效的JSON行: {line}")
                        continue
        except Exception as e:
            raise Exception(f"读取JSONL文件失败: {str(e)}")
            
        return documents
    
    def create_task(self, task_data: Dict[str, Any]) -> Task:
        """创建新任务
        
        Args:
            task_data: 任务数据，包含：
                - name: 任务名称
                - description: 任务描述
                - data_files: 数据文件列表
                - template_name: 任务模板名称
                - type: 任务类型
                
        Returns:
            Task: 创建的任务
        """
        try:
            # 验证必要字段
            required_fields = ['name', 'description', 'data_files', 'template_name']
            for field in required_fields:
                if field not in task_data:
                    raise ValueError(f"缺少必要字段: {field}")
            
            # 处理数据源
            data_sources = []
            all_document_ids = []
            total_documents = 0
            
            for file_name in task_data['data_files']:
                file_path = os.path.join(self.raw_data_dir, file_name)
                if not os.path.exists(file_path):
                    raise ValueError(f"数据文件不存在: {file_name}")
                
                # 加载文档
                documents = self.load_documents_from_jsonl(file_path)
                if not documents:
                    print(f"警告: 文件没有有效文档: {file_name}")
                    continue
                
                # 收集文档ID
                doc_ids = [doc.id for doc in documents]
                
                # 检查ID是否重复
                duplicate_ids = set(doc_ids) & set(all_document_ids)
                if duplicate_ids:
                    raise ValueError(f"发现重复的文档ID: {duplicate_ids}")
                
                all_document_ids.extend(doc_ids)
                total_documents += len(documents)
                
                # 创建数据源配置
                data_source = DataSource(
                    file_path=file_name,
                    total_documents=len(documents),
                    document_ids=doc_ids
                )
                data_sources.append(data_source)
            
            # 创建任务配置
            task_config = TaskConfig(
                data_sources=data_sources,
                template_name=task_data['template_name'],
                annotatable_fields=task_data.get('annotatable_fields', []),
                validation_rules=task_data.get('validation_rules', {})
            )
            
            # 创建任务
            task = Task(
                id=str(uuid.uuid4()),
                name=task_data['name'],
                description=task_data['description'],
                type=task_data.get('type', TaskType.ANNOTATION),
                config=task_config,
                document_ids=all_document_ids,
                total_documents=total_documents
            )
            
            # 保存到数据库
            task_in_db = TaskInDB(
                id=task.id,
                name=task.name,
                description=task.description,
                type=task.type,
                status=task.status,
                config=task_config.dict(),
                document_ids=task.document_ids,
                statistics={
                    "total_documents": total_documents,
                    "completed_documents": 0
                }
            )
            
            self.db.add(task_in_db)
            self.db.commit()
            
            return task
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"创建任务失败: {str(e)}")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        task_in_db = self.db.query(TaskInDB).filter(TaskInDB.id == task_id).first()
        if not task_in_db:
            return None
        return task_in_db.to_task()
    
    def get_task_documents(self, task_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """获取任务的文档列表
        
        Args:
            task_id: 任务ID
            skip: 跳过的文档数
            limit: 返回的最大文档数
            
        Returns:
            List[Document]: 文档列表
        """
        try:
            task = self.get_task(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            # 获取指定范围的文档ID
            doc_ids = task.document_ids[skip:skip + limit]
            if not doc_ids:
                return []
            
            documents = []
            # 从每个数据源加载文档
            for data_source in task.config.data_sources:
                file_path = os.path.join(self.raw_data_dir, data_source.file_path)
                if not os.path.exists(file_path):
                    print(f"警告: 数据文件不存在: {data_source.file_path}")
                    continue
                
                # 读取文件查找文档
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            content = json.loads(line.strip())
                            doc_id = content.get('s5', '')
                            if doc_id in doc_ids:
                                doc = Document(
                                    id=doc_id,
                                    content=content,
                                    source_file=data_source.file_path
                                )
                                documents.append(doc)
                                # 如果找到所有需要的文档就停止
                                if len(documents) == len(doc_ids):
                                    break
                        except json.JSONDecodeError:
                            continue
                            
                if len(documents) == len(doc_ids):
                    break
            
            return documents
            
        except Exception as e:
            raise Exception(f"获取任务文档失败: {str(e)}")
    
    def get_task_document(self, task_id: str, document_id: str) -> Optional[Document]:
        """获取任务中的单个文档
        
        Args:
            task_id: 任务ID
            document_id: 文档ID
            
        Returns:
            Optional[Document]: 文档对象，如果不存在返回None
        """
        try:
            task = self.get_task(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            # 检查文档是否属于任务
            if document_id not in task.document_ids:
                raise ValueError(f"文档不在任务中: {document_id}")
            
            # 查找包含该文档的数据源
            for data_source in task.config.data_sources:
                if document_id in data_source.document_ids:
                    file_path = os.path.join(self.raw_data_dir, data_source.file_path)
                    if not os.path.exists(file_path):
                        raise ValueError(f"数据文件不存在: {data_source.file_path}")
                    
                    # 在文件中查找文档
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                content = json.loads(line.strip())
                                if content.get('s5', '') == document_id:
                                    return Document(
                                        id=document_id,
                                        content=content,
                                        source_file=data_source.file_path
                                    )
                            except json.JSONDecodeError:
                                continue
            
            return None
            
        except Exception as e:
            raise Exception(f"获取文档失败: {str(e)}")
    
    def update_document_status(self, task_id: str, document_id: str, status: str) -> bool:
        """更新文档状态
        
        Args:
            task_id: 任务ID
            document_id: 文档ID
            status: 新状态
            
        Returns:
            bool: 是否更新成功
        """
        try:
            task = self.get_task(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            if document_id not in task.document_ids:
                raise ValueError(f"文档不在任务中: {document_id}")
            
            # 更新任务统计信息
            task_in_db = self.db.query(TaskInDB).filter(TaskInDB.id == task_id).first()
            if not task_in_db:
                return False
                
            statistics = task_in_db.statistics or {}
            if status == "completed" and document_id not in statistics.get("completed_ids", []):
                statistics["completed_documents"] = statistics.get("completed_documents", 0) + 1
                completed_ids = statistics.get("completed_ids", [])
                completed_ids.append(document_id)
                statistics["completed_ids"] = completed_ids
                
                # 检查是否所有文档都完成了
                if statistics["completed_documents"] == task_in_db.statistics.get("total_documents", 0):
                    task_in_db.status = TaskStatus.COMPLETED
                
                task_in_db.statistics = statistics
                self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新文档状态失败: {str(e)}")
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            task_in_db = self.db.query(TaskInDB).filter(TaskInDB.id == task_id).first()
            if not task_in_db:
                return False
            
            self.db.delete(task_in_db)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"删除任务失败: {str(e)}")