import json
import os
import uuid
import math
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from ..config import settings
from ..models.user import UserInDB, UserCreate
from ..models.task import (
    Task, TaskCreate, TaskDocument, TaskTemplate, TaskProgress, 
    TaskQuery, TaskListResponse, TaskStatistics, TaskStatus, DocumentStatus
)
from ..models.annotation import Annotation
from ..models.file import FileInfo, FileType
from .template_validator import TemplateValidator


class StorageManager:
    """文件系统存储管理器"""
    
    def __init__(self):
        self.data_dir = Path(settings.data_dir)
        self.template_validator = TemplateValidator()
        self._ensure_directories()
        self._init_default_data()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.data_dir,
            self.data_dir / "users",
            self.data_dir / "public_files",
            self.data_dir / "public_files" / "documents",
            self.data_dir / "public_files" / "templates", 
            self.data_dir / "public_files" / "exports",
            self.data_dir / "tasks",
            self.data_dir / "uploads"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _init_default_data(self):
        """初始化默认数据"""
        # 初始化用户文件
        users_file = self.data_dir / "users" / "users.json"
        if not users_file.exists():
            default_users = {"users": []}
            self._write_json(users_file, default_users)
        
        # 初始化任务文件
        tasks_file = self.data_dir / "tasks" / "tasks.json"
        if not tasks_file.exists():
            default_tasks = {"tasks": []}
            self._write_json(tasks_file, default_tasks)
    
    def _read_json(self, file_path: Path) -> Dict[str, Any]:
        """读取JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _write_json(self, file_path: Path, data: Dict[str, Any]):
        """写入JSON文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def _calculate_task_progress(self, task: Task) -> TaskProgress:
        """计算任务进度"""
        total_documents = len(task.documents)
        if total_documents == 0:
            return TaskProgress(
                total_documents=0,
                completed_documents=0,
                in_progress_documents=0,
                pending_documents=0,
                completion_percentage=0.0
            )
        
        completed_documents = sum(1 for doc in task.documents if doc.status == DocumentStatus.COMPLETED)
        in_progress_documents = sum(1 for doc in task.documents if doc.status == DocumentStatus.IN_PROGRESS)
        pending_documents = sum(1 for doc in task.documents if doc.status == DocumentStatus.PENDING)
        
        completion_percentage = (completed_documents / total_documents) * 100
        
        return TaskProgress(
            total_documents=total_documents,
            completed_documents=completed_documents,
            in_progress_documents=in_progress_documents,
            pending_documents=pending_documents,
            completion_percentage=round(completion_percentage, 2)
        )
    
    def _update_task_status(self, task: Task) -> TaskStatus:
        """根据文档状态自动更新任务状态"""
        if not task.documents:
            return TaskStatus.PENDING
        
        all_completed = all(doc.status == DocumentStatus.COMPLETED for doc in task.documents)
        any_in_progress = any(doc.status == DocumentStatus.IN_PROGRESS for doc in task.documents)
        
        if all_completed:
            return TaskStatus.COMPLETED
        elif any_in_progress or any(doc.status == DocumentStatus.COMPLETED for doc in task.documents):
            return TaskStatus.IN_PROGRESS
        else:
            return TaskStatus.PENDING
    
    def _parse_template_file(self, template_path: str) -> Dict[str, Any]:
        """解析模板文件，提取字段信息"""
        try:
            validation_result = self.validate_python_template(template_path)
            if validation_result.get("valid"):
                return {
                    "fields": validation_result.get("schema", {}),
                    "validation_result": validation_result
                }
            else:
                return {
                    "fields": {},
                    "validation_result": validation_result
                }
        except Exception as e:
            return {
                "fields": {},
                "validation_result": {"valid": False, "error": str(e)}
            }

    # 用户管理
    def get_all_users(self) -> List[UserInDB]:
        """获取所有用户"""
        users_file = self.data_dir / "users" / "users.json"
        data = self._read_json(users_file)
        users = []
        for user_data in data.get("users", []):
            users.append(UserInDB(**user_data))
        return users
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """根据ID获取用户"""
        users = self.get_all_users()
        for user in users:
            if user.id == user_id:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """根据用户名获取用户"""
        users = self.get_all_users()
        for user in users:
            if user.username == username:
                return user
        return None
    
    def create_user(self, user_create: UserCreate, password_hash: str) -> UserInDB:
        """创建用户"""
        users_file = self.data_dir / "users" / "users.json"
        data = self._read_json(users_file)
        
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        new_user = UserInDB(
            id=user_id,
            username=user_create.username,
            password_hash=password_hash,
            role=user_create.role,
            created_at=datetime.now()
        )
        
        data["users"].append(new_user.dict())
        self._write_json(users_file, data)
        return new_user
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[UserInDB]:
        """更新用户"""
        users_file = self.data_dir / "users" / "users.json"
        data = self._read_json(users_file)
        
        for i, user_data in enumerate(data.get("users", [])):
            if user_data["id"] == user_id:
                user_data.update(update_data)
                data["users"][i] = user_data
                self._write_json(users_file, data)
                return UserInDB(**user_data)
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        users_file = self.data_dir / "users" / "users.json"
        data = self._read_json(users_file)
        
        for i, user_data in enumerate(data.get("users", [])):
            if user_data["id"] == user_id:
                del data["users"][i]
                self._write_json(users_file, data)
                return True
        return False

    # 任务管理 - 增强版本
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        tasks_file = self.data_dir / "tasks" / "tasks.json"
        data = self._read_json(tasks_file)
        tasks = []
        for task_data in data.get("tasks", []):
            task = Task(**task_data)
            # 计算进度
            task.progress = self._calculate_task_progress(task)
            tasks.append(task)
        return tasks
    
    def get_tasks_with_query(self, query: TaskQuery) -> TaskListResponse:
        """根据查询条件获取任务列表"""
        all_tasks = self.get_all_tasks()
        
        # 应用筛选条件
        filtered_tasks = []
        for task in all_tasks:
            # 状态筛选
            if query.status and task.status != query.status:
                continue
            
            # 分配人筛选
            if query.assignee_id and task.assignee_id != query.assignee_id:
                continue
            
            # 创建人筛选
            if query.creator_id and task.creator_id != query.creator_id:
                continue
            
            # 搜索筛选
            if query.search:
                search_text = query.search.lower()
                if (search_text not in task.name.lower() and 
                    (not task.description or search_text not in task.description.lower())):
                    continue
            
            filtered_tasks.append(task)
        
        # 计算分页
        total = len(filtered_tasks)
        total_pages = math.ceil(total / query.page_size) if total > 0 else 1
        start_index = (query.page - 1) * query.page_size
        end_index = start_index + query.page_size
        
        paginated_tasks = filtered_tasks[start_index:end_index]
        
        return TaskListResponse(
            tasks=paginated_tasks,
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages
        )
    
    def get_task_statistics(self, user_id: Optional[str] = None) -> TaskStatistics:
        """获取任务统计信息"""
        all_tasks = self.get_all_tasks()
        
        total_tasks = len(all_tasks)
        pending_tasks = sum(1 for task in all_tasks if task.status == TaskStatus.PENDING)
        in_progress_tasks = sum(1 for task in all_tasks if task.status == TaskStatus.IN_PROGRESS)
        completed_tasks = sum(1 for task in all_tasks if task.status == TaskStatus.COMPLETED)
        
        my_tasks = 0
        if user_id:
            my_tasks = sum(1 for task in all_tasks if task.assignee_id == user_id)
        
        return TaskStatistics(
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            in_progress_tasks=in_progress_tasks,
            completed_tasks=completed_tasks,
            my_tasks=my_tasks
        )
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        tasks = self.get_all_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None
    
    def create_task(self, task_create: TaskCreate, creator_id: str) -> Task:
        """创建任务"""
        tasks_file = self.data_dir / "tasks" / "tasks.json"
        data = self._read_json(tasks_file)
        
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # 处理文档列表
        documents = []
        for doc_path in task_create.documents:
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
            filename = os.path.basename(doc_path)
            
            # 获取文件大小
            file_size = self.get_file_size(doc_path)
            
            documents.append(TaskDocument(
                id=doc_id,
                filename=filename,
                file_path=doc_path,
                status=DocumentStatus.PENDING,
                file_size=file_size,
                created_at=datetime.now()
            ))
        
        # 处理模板
        template = None
        if task_create.template_path:
            template_info = self._parse_template_file(task_create.template_path)
            template = TaskTemplate(
                filename=os.path.basename(task_create.template_path),
                file_path=task_create.template_path,
                fields=template_info.get("fields"),
                validation_result=template_info.get("validation_result")
            )
        
        new_task = Task(
            id=task_id,
            name=task_create.name,
            description=task_create.description,
            creator_id=creator_id,
            assignee_id=task_create.assignee_id,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            documents=documents,
            template=template
        )
        
        # 计算进度
        new_task.progress = self._calculate_task_progress(new_task)
        
        # 使用model_dump()替代dict()以兼容Pydantic v2
        try:
            task_dict = new_task.model_dump()
        except AttributeError:
            # 兼容Pydantic v1
            task_dict = new_task.dict()
        
        data["tasks"].append(task_dict)
        self._write_json(tasks_file, data)
        
        # 创建任务目录
        task_dir = self.data_dir / "tasks" / task_id
        task_dir.mkdir(exist_ok=True)
        (task_dir / "annotations").mkdir(exist_ok=True)
        
        return new_task
    
    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Optional[Task]:
        """更新任务"""
        tasks_file = self.data_dir / "tasks" / "tasks.json"
        data = self._read_json(tasks_file)
        
        for i, task_data in enumerate(data.get("tasks", [])):
            if task_data["id"] == task_id:
                # 添加更新时间
                update_data["updated_at"] = datetime.now().isoformat()
                task_data.update(update_data)
                
                # 重新构建任务对象以计算进度
                updated_task = Task(**task_data)
                updated_task.progress = self._calculate_task_progress(updated_task)
                
                # 自动更新任务状态
                auto_status = self._update_task_status(updated_task)
                if updated_task.status != auto_status:
                    updated_task.status = auto_status
                    task_data["status"] = auto_status.value
                
                # 使用model_dump()替代dict()以兼容Pydantic v2
                try:
                    task_dict = updated_task.model_dump()
                except AttributeError:
                    # 兼容Pydantic v1
                    task_dict = updated_task.dict()
                
                data["tasks"][i] = task_dict
                self._write_json(tasks_file, data)
                return updated_task
        return None
    
    def update_document_status(self, task_id: str, document_id: str, status: DocumentStatus) -> Optional[Task]:
        """更新文档状态并重新计算任务进度"""
        tasks_file = self.data_dir / "tasks" / "tasks.json"
        data = self._read_json(tasks_file)
        
        for i, task_data in enumerate(data.get("tasks", [])):
            if task_data["id"] == task_id:
                # 更新文档状态
                for doc in task_data.get("documents", []):
                    if doc["id"] == document_id:
                        doc["status"] = status.value
                        break
                
                # 重新构建任务对象
                updated_task = Task(**task_data)
                updated_task.progress = self._calculate_task_progress(updated_task)
                
                # 自动更新任务状态
                auto_status = self._update_task_status(updated_task)
                updated_task.status = auto_status
                task_data["status"] = auto_status.value
                task_data["updated_at"] = datetime.now().isoformat()
                
                data["tasks"][i] = updated_task.dict()
                self._write_json(tasks_file, data)
                return updated_task
        return None
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        tasks_file = self.data_dir / "tasks" / "tasks.json"
        data = self._read_json(tasks_file)
        
        for i, task_data in enumerate(data.get("tasks", [])):
            if task_data["id"] == task_id:
                del data["tasks"][i]
                self._write_json(tasks_file, data)
                
                # 删除任务目录
                task_dir = self.data_dir / "tasks" / task_id
                if task_dir.exists():
                    import shutil
                    shutil.rmtree(task_dir)
                
                return True
        return False

    # 标注管理
    def get_annotation(self, task_id: str, document_id: str) -> Optional[Annotation]:
        """获取标注数据"""
        annotation_file = self.data_dir / "tasks" / task_id / "annotations" / f"{document_id}.json"
        if annotation_file.exists():
            data = self._read_json(annotation_file)
            return Annotation(**data)
        return None
    
    def save_annotation(self, annotation: Annotation) -> Annotation:
        """保存标注数据"""
        annotation_file = self.data_dir / "tasks" / annotation.task_id / "annotations" / f"{annotation.document_id}.json"
        annotation.updated_at = datetime.now()
        self._write_json(annotation_file, annotation.dict())
        
        # 更新文档状态
        if annotation.status == "completed":
            self.update_document_status(annotation.task_id, annotation.document_id, DocumentStatus.COMPLETED)
        elif annotation.status == "in_progress":
            self.update_document_status(annotation.task_id, annotation.document_id, DocumentStatus.IN_PROGRESS)
        
        return annotation

    # 文件管理
    def save_file_info(self, file_info: FileInfo):
        """保存文件信息到元数据"""
        files_file = self.data_dir / "public_files" / "files_metadata.json"
        data = self._read_json(files_file)
        
        if "files" not in data:
            data["files"] = []
        
        # 检查是否已存在，如果存在则更新
        for i, existing_file in enumerate(data["files"]):
            if existing_file["id"] == file_info.id:
                data["files"][i] = file_info.dict()
                self._write_json(files_file, data)
                return
        
        # 如果不存在则添加
        data["files"].append(file_info.dict())
        self._write_json(files_file, data)

    def get_file_content(self, file_path: str) -> Optional[str]:
        """获取文件内容"""
        try:
            full_path = self.data_dir / file_path
            if not full_path.exists():
                return None
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    # 文件管理功能
    def get_all_files(self, file_type: Optional[FileType] = None) -> List[FileInfo]:
        """获取所有文件信息"""
        files_file = self.data_dir / "public_files" / "files_metadata.json"
        data = self._read_json(files_file)
        
        files = []
        for file_data in data.get("files", []):
            file_info = FileInfo(**file_data)
            if file_type is None or file_info.file_type == file_type:
                files.append(file_info)
        
        return files
    
    def get_file_by_id(self, file_id: str) -> Optional[FileInfo]:
        """根据ID获取文件信息"""
        files = self.get_all_files()
        for file_info in files:
            if file_info.id == file_id:
                return file_info
        return None
    
    def delete_file_info(self, file_id: str) -> bool:
        """删除文件元数据"""
        files_file = self.data_dir / "public_files" / "files_metadata.json"
        data = self._read_json(files_file)
        
        for i, file_data in enumerate(data.get("files", [])):
            if file_data["id"] == file_id:
                del data["files"][i]
                self._write_json(files_file, data)
                return True
        return False
    
    def delete_physical_file(self, file_path: str) -> bool:
        """删除物理文件"""
        try:
            full_path = self.data_dir / file_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def validate_python_template(self, file_path: str) -> Dict[str, Any]:
        """验证Python模板文件 - 使用新的AnnotationSchema格式"""
        try:
            full_path = self.data_dir / file_path
            return self.template_validator.validate_template_file(str(full_path))
        except Exception as e:
            return {"valid": False, "error": f"验证失败: {str(e)}"}
    
    def get_file_size(self, file_path: str) -> int:
        """获取文件大小"""
        try:
            full_path = self.data_dir / file_path
            if full_path.exists():
                return full_path.stat().st_size
            return 0
        except Exception:
            return 0
    
    def get_files_by_uploader(self, uploader_id: str) -> List[FileInfo]:
        """获取指定用户上传的文件"""
        files = self.get_all_files()
        return [f for f in files if f.uploader_id == uploader_id] 