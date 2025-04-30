from typing import Dict, Any, List
import json
import os
from datetime import datetime

class TrainingService:
    """训练数据转换服务"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def convert_to_jsonl(self, documents: List[Dict[str, Any]], output_file: str) -> str:
        """将JSON数据转换为JSONL格式"""
        output_path = os.path.join(self.output_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for doc in documents:
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        
        return output_path
    
    def split_dataset(self, documents: List[Dict[str, Any]], train_ratio: float = 0.8) -> Dict[str, List[Dict[str, Any]]]:
        """划分训练集和验证集"""
        total_docs = len(documents)
        train_size = int(total_docs * train_ratio)
        
        # 随机打乱数据
        import random
        random.shuffle(documents)
        
        return {
            "train": documents[:train_size],
            "validation": documents[train_size:]
        }
    
    def prepare_training_data(self, task_id: str, train_ratio: float = 0.8) -> Dict[str, str]:
        """准备训练数据"""
        task_dir = os.path.join(self.output_dir, task_id)
        
        # 加载标注结果
        annotations = []
        for filename in os.listdir(task_dir):
            if filename.endswith("_annotation.json"):
                with open(os.path.join(task_dir, filename), 'r', encoding='utf-8') as f:
                    annotations.append(json.load(f))
        
        # 划分数据集
        datasets = self.split_dataset(annotations, train_ratio)
        
        # 转换为JSONL格式
        train_file = self.convert_to_jsonl(datasets["train"], f"{task_id}_train.jsonl")
        validation_file = self.convert_to_jsonl(datasets["validation"], f"{task_id}_validation.jsonl")
        
        return {
            "train_file": train_file,
            "validation_file": validation_file
        }
    
    def upload_to_openai(self, api_key: str, training_file: str, validation_file: str) -> Dict[str, Any]:
        """上传数据到OpenAI"""
        import openai
        openai.api_key = api_key
        
        # 上传训练文件
        train_response = openai.File.create(
            file=open(training_file, "rb"),
            purpose="fine-tune"
        )
        
        # 上传验证文件
        validation_response = openai.File.create(
            file=open(validation_file, "rb"),
            purpose="fine-tune"
        )
        
        return {
            "train_file_id": train_response.id,
            "validation_file_id": validation_response.id
        }
    
    def start_training(self, api_key: str, train_file_id: str, validation_file_id: str) -> Dict[str, Any]:
        """开始训练"""
        import openai
        openai.api_key = api_key
        
        # 创建微调作业
        response = openai.FineTune.create(
            training_file=train_file_id,
            validation_file=validation_file_id,
            model="gpt-3.5-turbo"
        )
        
        return {
            "job_id": response.id,
            "status": response.status
        }
    
    def check_training_status(self, api_key: str, job_id: str) -> Dict[str, Any]:
        """检查训练状态"""
        import openai
        openai.api_key = api_key
        
        response = openai.FineTune.retrieve(job_id)
        
        return {
            "job_id": response.id,
            "status": response.status,
            "model": response.fine_tuned_model if response.fine_tuned_model else None
        } 