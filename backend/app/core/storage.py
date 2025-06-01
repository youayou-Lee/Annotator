import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..config import settings
from ..models.user import UserInDB, UserCreate
from ..models.task import Task, TaskCreate, TaskDocument, TaskTemplate
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
    
    # 任务管理
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        tasks_file = self.data_dir / "tasks" / "tasks.json"
        data = self._read_json(tasks_file)
        tasks = []
        for task_data in data.get("tasks", []):
            tasks.append(Task(**task_data))
        return tasks
    
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
            documents.append(TaskDocument(
                id=doc_id,
                filename=filename,
                file_path=doc_path,
                status="pending"
            ))
        
        # 处理模板
        template = None
        if task_create.template_path:
            template = TaskTemplate(
                filename=os.path.basename(task_create.template_path),
                file_path=task_create.template_path
            )
        
        new_task = Task(
            id=task_id,
            name=task_create.name,
            description=task_create.description,
            creator_id=creator_id,
            assignee_id=task_create.assignee_id,
            status="pending",
            created_at=datetime.now(),
            documents=documents,
            template=template
        )
        
        data["tasks"].append(new_task.dict())
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
                task_data.update(update_data)
                data["tasks"][i] = task_data
                self._write_json(tasks_file, data)
                return Task(**task_data)
        return None
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        tasks_file = self.data_dir / "tasks" / "tasks.json"
        data = self._read_json(tasks_file)
        
        for i, task_data in enumerate(data.get("tasks", [])):
            if task_data["id"] == task_id:
                del data["tasks"][i]
                self._write_json(tasks_file, data)
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