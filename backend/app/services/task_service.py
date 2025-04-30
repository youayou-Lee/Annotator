import os
import json
import uuid
from typing import List, Dict, Any
from datetime import datetime
from ..models.task import Task
from ..models.document import Document

class TaskService:
    """任务服务"""
    
    def __init__(self, raw_data_dir: str = "data/raw", task_templates_dir: str = "data/task_templates"):
        # 使用绝对路径
        self.raw_data_dir = os.path.abspath(raw_data_dir)
        self.task_templates_dir = os.path.abspath(task_templates_dir)
        print(f"原始数据目录: {self.raw_data_dir}")  # 添加调试信息
        print(f"任务模板目录: {self.task_templates_dir}")  # 添加调试信息
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.task_templates_dir, exist_ok=True)
    
    def get_available_templates(self) -> List[str]:
        """获取可用的任务模板列表"""
        templates = []
        for file in os.listdir(self.task_templates_dir):
            if file.endswith('.json'):
                templates.append(file)
        return templates
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """加载任务模板"""
        template_path = os.path.join(self.task_templates_dir, template_name)
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def save_template(self, template: Dict[str, Any], template_name: str):
        """保存任务模板"""
        template_path = os.path.join(self.task_templates_dir, template_name)
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
    
    def convert_jsonl_to_json(self, jsonl_file: str) -> str:
        """将JSONL文件转换为JSON文件"""
        json_file = jsonl_file.replace('.jsonl', '.json')
        json_path = os.path.join(self.raw_data_dir, json_file)
        
        # 读取JSONL文件
        documents = []
        with open(os.path.join(self.raw_data_dir, jsonl_file), 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    doc = json.loads(line.strip())
                    documents.append(doc)
                except json.JSONDecodeError:
                    continue
        
        # 保存为JSON文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({'documents': documents}, f, ensure_ascii=False, indent=2)
        
        return json_file
    
    def validate_document_structure(self, document: Dict[str, Any], template: Dict[str, Any]) -> bool:
        """验证文档结构是否符合模板要求"""
        required_fields = template.get('required_fields', [])
        for field in required_fields:
            if field not in document:
                return False
        return True
    
    def create_task(self, task_data: Dict[str, Any]) -> Task:
        """创建任务
        
        Args:
            task_data: 任务数据，包含：
                - name: 任务名称
                - description: 任务描述
                - data_file: 数据文件名
                - template: 任务模板名
                - config: 任务配置
        """
        try:
            # 验证必要字段
            required_fields = ['name', 'description', 'data_file', 'template']
            for field in required_fields:
                if field not in task_data:
                    raise ValueError(f"缺少必要字段: {field}")
            
            # 获取任务模板
            template = self.load_template(task_data.get('template', 'default.json'))
            if not template:
                raise ValueError("任务模板不存在")
            
            # 处理数据文件
            data_file = task_data['data_file']
            data_path = os.path.join(self.raw_data_dir, data_file)
            print(f"尝试读取文件: {data_path}")  # 添加调试信息
            
            if not os.path.exists(data_path):
                raise ValueError(f"数据文件不存在: {data_file}")
            
            # 读取数据文件
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"文件内容: {content[:200]}...")  # 打印文件内容的前200个字符
                    data = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"数据文件格式错误: {str(e)}")
            except Exception as e:
                raise ValueError(f"读取文件失败: {str(e)}")
            
            # 处理文档数据
            documents = []
            if isinstance(data, list):
                documents = data
            elif isinstance(data, dict) and 'documents' in data:
                documents = data['documents']
            else:
                raise ValueError("数据文件格式不正确，应为JSON数组或包含documents字段的对象")
            
            if not documents:
                raise ValueError("数据文件中没有文档")
            
            print(f"找到 {len(documents)} 个文档")  # 添加调试信息
            
            # 验证文档结构
            for doc in documents:
                if not isinstance(doc, dict):
                    raise ValueError(f"文档格式不正确: {doc}")
                if not self.validate_document_structure(doc, template):
                    raise ValueError(f"文档结构不匹配模板: {doc.get('s5', '')}")
            
            # 创建任务
            task = Task(
                id=str(uuid.uuid4()),
                name=task_data['name'],
                description=task_data['description'],
                document_ids=[doc.get('s5', '') for doc in documents],
                status='pending',
                created_at=datetime.now(),
                updated_at=datetime.now(),
                config={
                    'template': template,
                    'data_file': data_file,
                    **task_data.get('config', {})
                }
            )
            
            return task
        except Exception as e:
            raise Exception(f"创建任务失败: {str(e)}")
    
    def save_task(self, task: Task):
        """保存任务"""
        task_dir = os.path.join(self.raw_data_dir, task.id)
        os.makedirs(task_dir, exist_ok=True)
        
        # 保存任务配置
        task_config = {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "document_ids": task.document_ids,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "config": task.config
        }
        
        config_path = os.path.join(task_dir, "task_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(task_config, f, ensure_ascii=False, indent=2)
        
        return task_dir
    
    def get_tasks(self) -> List[Task]:
        """获取所有任务列表"""
        try:
            tasks = []
            # 遍历原始数据目录下的所有子目录
            for task_id in os.listdir(self.raw_data_dir):
                task_dir = os.path.join(self.raw_data_dir, task_id)
                if os.path.isdir(task_dir):
                    config_path = os.path.join(task_dir, "task_config.json")
                    if os.path.exists(config_path):
                        try:
                            with open(config_path, 'r', encoding='utf-8') as f:
                                task_config = json.load(f)
                                task = Task(
                                    id=task_config['id'],
                                    name=task_config['name'],
                                    description=task_config['description'],
                                    document_ids=task_config['document_ids'],
                                    status=task_config['status'],
                                    created_at=datetime.fromisoformat(task_config['created_at']),
                                    updated_at=datetime.fromisoformat(task_config['updated_at']),
                                    config=task_config['config']
                                )
                                tasks.append(task)
                        except Exception as e:
                            print(f"加载任务配置失败 {task_id}: {str(e)}")
                            continue
            return tasks
        except Exception as e:
            raise Exception(f"获取任务列表失败: {str(e)}")
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            task_dir = os.path.join(self.raw_data_dir, task_id)
            if not os.path.exists(task_dir):
                raise ValueError(f"任务不存在: {task_id}")
            
            # 删除任务目录及其所有内容
            import shutil
            shutil.rmtree(task_dir)
            print(f"成功删除任务目录: {task_dir}")
            
            return True
        except Exception as e:
            raise Exception(f"删除任务失败: {str(e)}")
    
    def load_task_documents(self, task_id: str) -> List[Dict[str, Any]]:
        """加载任务的文档列表
        
        Args:
            task_id: 任务ID
            
        Returns:
            List[Dict[str, Any]]: 文档列表
        """
        try:
            # 获取任务配置
            task_dir = os.path.join(self.raw_data_dir, task_id)
            if not os.path.exists(task_dir):
                raise ValueError(f"任务不存在: {task_id}")
            
            config_path = os.path.join(task_dir, "task_config.json")
            if not os.path.exists(config_path):
                raise ValueError(f"任务配置文件不存在: {task_id}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                task_config = json.load(f)
            
            # 获取数据文件路径
            data_file = task_config['config']['data_file']
            data_path = os.path.join(self.raw_data_dir, data_file)
            
            if not os.path.exists(data_path):
                raise ValueError(f"数据文件不存在: {data_file}")
            
            # 读取数据文件
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理文档数据
            documents = []
            if isinstance(data, list):
                documents = data
            elif isinstance(data, dict) and 'documents' in data:
                documents = data['documents']
            else:
                raise ValueError("数据文件格式不正确")
            
            # 过滤出任务中的文档
            task_document_ids = set(task_config['document_ids'])
            task_documents = [
                doc for doc in documents
                if doc.get('s5', '') in task_document_ids
            ]
            
            return task_documents
        except Exception as e:
            raise Exception(f"加载文档失败: {str(e)}")
    
    def get_task_document(self, task_id: str, document_id: str) -> Dict[str, Any]:
        """获取任务的单个文档
        
        Args:
            task_id: 任务ID
            document_id: 文档ID
            
        Returns:
            Dict[str, Any]: 文档内容
        """
        try:
            # 获取任务配置
            task_dir = os.path.join(self.raw_data_dir, task_id)
            if not os.path.exists(task_dir):
                raise ValueError(f"任务不存在: {task_id}")
            
            config_path = os.path.join(task_dir, "task_config.json")
            if not os.path.exists(config_path):
                raise ValueError(f"任务配置文件不存在: {task_id}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                task_config = json.load(f)
            
            # 检查文档ID是否在任务中
            if document_id not in task_config['document_ids']:
                raise ValueError(f"文档不在任务中: {document_id}")
            
            # 获取数据文件路径
            data_file = task_config['config']['data_file']
            data_path = os.path.join(self.raw_data_dir, data_file)
            
            if not os.path.exists(data_path):
                raise ValueError(f"数据文件不存在: {data_file}")
            
            # 读取数据文件
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理文档数据
            documents = []
            if isinstance(data, list):
                documents = data
            elif isinstance(data, dict) and 'documents' in data:
                documents = data['documents']
            else:
                raise ValueError("数据文件格式不正确")
            
            # 查找指定ID的文档
            for doc in documents:
                if doc.get('s5', '') == document_id:
                    return doc
            
            raise ValueError(f"文档不存在: {document_id}")
        except Exception as e:
            raise Exception(f"加载文档失败: {str(e)}") 