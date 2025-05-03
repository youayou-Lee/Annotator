import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.task import Task, TaskConfig, Document, TaskStatus, TaskType
from sqlalchemy.orm import Session

class TaskService:
    """任务服务"""
    
    def __init__(self, upload_dir: str = "data/raw/upload", task_templates_dir: str = "data/task_templates"):
        self.upload_dir = upload_dir
        self.task_templates_dir = os.path.abspath(task_templates_dir)
        self.tasks_dir = os.path.join("data", "tasks")  # tasks 文件夹用于存储任务配置
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.task_templates_dir, exist_ok=True)
        os.makedirs(self.tasks_dir, exist_ok=True)
    
    def load_documents_from_jsonl(self, file_path: str) -> List[Document]:
        """从JSONL文件加载文档
        
        Args:
            file_path: JSONL文件路径
            
        Returns:
            List[Document]: 文档列表
        """
        documents = []
        # try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # try:
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
                # except json.JSONDecodeError:
                #     print(f"警告: 无效的JSON行: {line}")
                #     continue
        # except Exception as e:
        #     raise Exception(f"读取JSONL文件失败: {str(e)}")
            
        return documents
    
    def create_task(self, task_data: Dict[str, Any]) -> Task:
        """创建新任务
        
        Args:
            task_data: 任务数据，包含：
                - name: 任务名称
                - description: 任务描述 
                - data_file: 数据文件
                - template: 任务模板名称
                - config: 可标注字段配置列表，每个字段包含path和type
        """
        try:
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 从模板创建任务配置
            template_path = os.path.join(self.task_templates_dir, task_data['template'])
            task_config = TaskConfig.from_template(
                template_path=template_path,
                selected_fields=task_data.get('config', [])
            )

            # 创建任务对象
            task = Task(
                id=task_id,
                name=task_data['name'],
                description=task_data['description'],
                files_path=[task_data['data_file']],
                config=task_config.get_beMarked(),  # 将TaskConfig转换为字段配置列表
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            # 保存任务配置
            self.save_task(task)
            return task

        except Exception as e:
            raise Exception(f"创建任务失败: {str(e)}")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        # try:
        task_file_path = os.path.join(self.tasks_dir, f"{task_id}.json")
        if not os.path.exists(task_file_path):
            return None
            
        with open(task_file_path, 'r', encoding='utf-8') as f:
            task_data = json.load(f)
            return Task(**task_data)
                
        # except Exception as e:
        #     raise Exception(f"获取任务失败: {str(e)}")

    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        tasks = []
        # try:
        for filename in os.listdir(self.tasks_dir):
            if filename.endswith('.json'):
                task_file_path = os.path.join(self.tasks_dir, filename)
                with open(task_file_path, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                    print(f"加载任务: {task_data['id']}")
                    tasks.append(Task(**task_data))
        return tasks
        # except Exception as e:
        #     raise Exception(f"获取任务列表失败: {str(e)}")
    
    def get_task_documents(self, task_id: str) -> List[Dict[str, Any]]:
        """获取任务的文档列表"""
        # try:
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        
        documents = []
        # 从上传目录加载文档
        for file_path in task.files_path:
            full_path = os.path.join(self.upload_dir, file_path)
            if not os.path.exists(full_path):
                print(f"警告: 数据文件不存在: {full_path}")
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_content = json.load(f)
                    # 如果文件内容是列表，直接使用
                    if isinstance(file_content, list):
                        documents.extend(file_content)
                    # 如果是单个文档，包装成列表
                    elif isinstance(file_content, dict):
                        documents.append(file_content)
            except Exception as e:
                print(f"读取文件 {full_path} 失败: {str(e)}")
                continue
        
        return documents
            
        # except Exception as e:
        #     raise Exception(f"获取任务文档失败: {str(e)}")
            
    def get_task_document(self, task_id: str, document_id: str) -> Optional[Dict[str, Any]]:
        """获取任务中的单个文档"""
        try:
            documents = self.get_task_documents(task_id)
            for doc in documents:
                if doc.get('id') == document_id:
                    return doc
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
        """删除任务"""
        try:
            task_file_path = os.path.join(self.tasks_dir, f"{task_id}.json")
            if not os.path.exists(task_file_path):
                return False
                
            os.remove(task_file_path)
            return True
            
        except Exception as e:
            raise Exception(f"删除任务失败: {str(e)}")

    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Optional[Task]:
        """更新任务"""
        try:
            task = self.get_task(task_id)
            if not task:
                return None
                
            # 更新任务数据
            for key, value in task_data.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            # 保存更新后的任务
            task_file_path = os.path.join(self.tasks_dir, f"{task_id}.json")
            with open(task_file_path, 'w', encoding='utf-8') as f:
                json.dump(task.dict(), f, ensure_ascii=False, indent=2, default=str)
            
            return task
            
        except Exception as e:
            raise Exception(f"更新任务失败: {str(e)}")

    def save_task(self, task: Task) -> str:
        """保存任务"""
        try:
            task_file_path = os.path.join(self.tasks_dir, f"{task.id}.json")
            with open(task_file_path, 'w', encoding='utf-8') as f:
                json.dump(task.dict(), f, ensure_ascii=False, indent=2, default=str)
            return task_file_path
        except Exception as e:
            raise Exception(f"保存任务失败: {str(e)}")

    def get_available_templates(self) -> List[str]:
        """获取可用的任务模板列表"""
        try:
            templates = []
            for filename in os.listdir(self.task_templates_dir):
                if filename.endswith('.json'):
                    templates.append(filename)
            return templates
        except Exception as e:
            raise Exception(f"获取模板列表失败: {str(e)}")

    def merge_annotations(self, task_id: str) -> str:
        """合并标注结果到最终文档
        
        将一个任务中的多个文档的标注结果合并成一个文件
        """
        try:
            # 获取任务信息和原始文档
            task = self.get_task(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            documents = self.get_task_documents(task_id)
            if not documents:
                raise ValueError(f"任务没有文档: {task_id}")
            
            # 加载标注结果
            annotations_dir = os.path.join("data", "annotations", task_id)
            if not os.path.exists(annotations_dir):
                raise ValueError(f"标注目录不存在: {annotations_dir}")
                
            # 存储合并后的文档
            merged_documents = []
            
            # 检查每个文档是否都有标注结果并合并
            all_annotated = True
            for doc in documents:
                doc_id = doc.get('id')
                if not doc_id:
                    continue
                    
                annotation_path = os.path.join(annotations_dir, f"{doc_id}_annotation.json")
                if not os.path.exists(annotation_path):
                    all_annotated = False
                    print(f"文档 {doc_id} 未完成标注")
                    continue
                
                # 读取标注结果
                with open(annotation_path, 'r', encoding='utf-8') as f:
                    annotated_doc = json.load(f)
                    # 添加原始文档ID作为参考
                    annotated_doc['original_doc_id'] = doc_id
                    merged_documents.append(annotated_doc)
            
            if not merged_documents:
                raise ValueError("没有找到任何已标注的文档")
                
            # 如果所有文档都已标注，更新任务状态
            if all_annotated:
                task.status = "completed"
                self.save_task(task)
            
            # 创建merged_data目录（如果不存在）
            merged_dir = os.path.join("data", "merged_data")
            os.makedirs(merged_dir, exist_ok=True)
            
            # 保存合并后的文档，包含时间戳以避免覆盖
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(merged_dir, f"{task_id}_{timestamp}_merged.json")
            
            # 创建合并文档的元数据
            merged_data = {
                "task_id": task_id,
                "merge_time": timestamp,
                "total_documents": len(documents),
                "merged_documents": len(merged_documents),
                "all_completed": all_annotated,
                "documents": merged_documents
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            
            return output_path
            
        except Exception as e:
            print(f"合并标注结果失败: {str(e)}")
            raise e

    def check_task_completion(self, task_id: str) -> bool:
        """检查任务是否已完成"""
        try:
            # 获取任务信息
            task = self.get_task(task_id)
            if not task:
                return False
            
            # 获取任务的文档列表
            documents = self.get_task_documents(task_id)
            
            # 检查每个文档是否都有标注结果
            annotations_dir = os.path.join("data", "annotations", task_id)
            if not os.path.exists(annotations_dir):
                return False
                
            for doc in documents:
                doc_id = doc.get('id')
                if not doc_id:
                    continue
                    
                annotation_path = os.path.join(annotations_dir, f"{doc_id}_annotation.json")
                if not os.path.exists(annotation_path):
                    return False
            
            return True
            
        except Exception as e:
            print(f"检查任务完成状态失败: {str(e)}")
            return False


