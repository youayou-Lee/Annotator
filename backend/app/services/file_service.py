import json
import os
from typing import List, Dict, Any
from fastapi import UploadFile
from ..models.document import Document

class FileService:
    """文件处理服务"""
    
    def __init__(self, upload_dir: str = "data/raw/upload"):
        # 使用绝对路径
        self.upload_dir = os.path.abspath(upload_dir)
        print(f"文件上传目录: {self.upload_dir}")  # 添加调试信息
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_upload_file(self, file: UploadFile, content: bytes) -> str:
        """保存上传的文件"""
        try:
            # 确保上传目录存在
            os.makedirs(self.upload_dir, exist_ok=True)
            print(f"上传目录: {self.upload_dir}")  # 添加日志
            
            # 保存文件
            file_path = os.path.join(self.upload_dir, file.filename)
            print(f"保存文件到: {file_path}")  # 添加日志
            
            # 检查文件内容
            print(f"文件大小: {len(content)} 字节")  # 添加日志
            
            if not content:
                raise Exception("上传的文件内容为空")
            
            # 保存文件
            try:
                with open(file_path, 'wb') as f:
                    f.write(content)
            except Exception as e:
                print(f"文件写入失败: {str(e)}")  # 添加日志
                raise Exception(f"文件写入失败: {str(e)}")
            
            # 验证文件是否成功保存
            if not os.path.exists(file_path):
                raise Exception(f"文件保存失败: {file_path}")
            
            # 验证文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        raise Exception("文件内容为空")
                    json.loads(content)  # 验证JSON格式
            except json.JSONDecodeError as e:
                print(f"JSON格式验证失败: {str(e)}")  # 添加日志
                raise Exception(f"文件不是有效的JSON格式: {str(e)}")
            except Exception as e:
                print(f"文件内容验证失败: {str(e)}")  # 添加日志
                raise Exception(f"文件内容验证失败: {str(e)}")
            
            print(f"文件保存成功: {file_path}")  # 添加日志
            return file.filename
        except Exception as e:
            print(f"保存文件失败: {str(e)}")  # 添加日志
            raise Exception(f"保存文件失败: {str(e)}")
    
    def read_jsonl_file(self, file_path: str) -> List[Dict[str, Any]]:
        """读取JSONL文件"""
        documents = []
        try:
            print(f"开始读取文件: {file_path}")  # 添加调试信息
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    raise ValueError("文件内容为空")
                
                print(f"文件内容: {content[:200]}...")  # 打印文件内容的前200个字符
                
                # 尝试解析为JSON
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        documents = data
                    elif isinstance(data, dict) and 'documents' in data:
                        documents = data['documents']
                    else:
                        raise ValueError("文件格式不正确，应为JSON数组或包含documents字段的对象")
                except json.JSONDecodeError as e:
                    raise ValueError(f"JSON解析错误: {str(e)}")
                
                print(f"成功解析 {len(documents)} 个文档")  # 添加调试信息
                return documents
        except Exception as e:
            raise Exception(f"读取文件失败: {str(e)}")
    
    def save_jsonl_file(self, documents: List[Dict[str, Any]], file_path: str):
        """保存为JSONL文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for doc in documents:
                    f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}")
    
    def convert_to_documents(self, data: List[Dict[str, Any]]) -> List[Document]:
        """将数据转换为Document对象"""
        try:
            return [
                Document(
                    id=doc.get('s5', ''),  # 使用s5作为文档ID
                    content=doc,
                    metadata={
                        'province': doc.get('s2', '').split('省')[0] + '省' if '省' in doc.get('s2', '') else '',
                        'case_type': doc.get('s8', ''),
                        'level': doc.get('s9', ''),
                        'date': doc.get('s31', ''),
                        'case_reason': doc.get('s11', [])
                    }
                )
                for doc in data
            ]
        except Exception as e:
            raise Exception(f"转换文档失败: {str(e)}")
    
    def process_uploaded_file(self, file_path: str) -> List[Document]:
        """处理上传的文件"""
        try:
            # 确保使用完整的文件路径
            full_path = os.path.join(self.upload_dir, file_path)
            print(f"处理文件: {full_path}")  # 添加调试信息
            
            if not os.path.exists(full_path):
                raise Exception(f"文件不存在: {full_path}")
            
            # 读取JSONL文件
            documents = self.read_jsonl_file(full_path)
            
            # 转换为Document对象
            return self.convert_to_documents(documents)
        except Exception as e:
            raise Exception(f"处理文件失败: {str(e)}") 