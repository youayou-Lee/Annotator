from typing import Dict, Any, List, Optional
from ..models.document import Document
import json
import os
from datetime import datetime
import jsonlines
from fastapi import UploadFile, HTTPException
import shutil

class FormatService:
    """格式化存储服务"""
    def __init__(self, output_dir: str = "data/formatted"):
        self.output_dir = output_dir
        # 确保目录存在
        os.makedirs(output_dir, exist_ok=True)
        # 确保默认模板目录存在
        os.makedirs("data/task_templates", exist_ok=True)

    async def process_file(self, jsonl_file: UploadFile, template_file: Optional[UploadFile] = None) -> Dict[str, Any]:
        """处理上传的JSONL文件和模板文件"""
        # 创建临时目录用于处理文件
        temp_dir = os.path.join(self.output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # 创建临时文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_jsonl = os.path.join(temp_dir, f"temp_{timestamp}.jsonl")
        temp_template = os.path.join(temp_dir, f"temp_{timestamp}.json")
        
        try:
            # 验证JSONL文件
            if not jsonl_file.filename.endswith('.jsonl'):
                raise HTTPException(status_code=400, detail="只接受 JSONL 格式的文件")
            
            # 保存并验证JSONL文件
            try:
                with open(temp_jsonl, 'wb') as f:
                    content = await jsonl_file.read()
                    if not content:
                        raise HTTPException(status_code=400, detail="JSONL 文件内容为空")
                    f.write(content)
                    await jsonl_file.seek(0)  # 重置文件指针
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"JSONL 文件保存失败: {str(e)}")

            # 获取并验证模板
            try:
                if template_file:
                    if not template_file.filename.endswith('.json'):
                        raise HTTPException(status_code=400, detail="模板文件必须是 JSON 格式")
                    with open(temp_template, 'wb') as f:
                        content = await template_file.read()
                        if not content:
                            raise HTTPException(status_code=400, detail="模板文件内容为空")
                        f.write(content)
                    with open(temp_template, 'r', encoding='utf-8') as f:
                        template = json.load(f)
                else:
                    template_path = "data/task_templates/template_default.json"
                    if not os.path.exists(template_path):
                        raise HTTPException(status_code=404, detail="默认模板文件不存在")
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template = json.load(f)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="模板文件格式错误，不是有效的 JSON")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"模板文件处理失败: {str(e)}")

            # 处理文件
            documents = []
            success_count = 0
            error_count = 0
            error_details = []
            
            try:
                with jsonlines.open(temp_jsonl) as reader:
                    for line_num, item in enumerate(reader, 1):
                        try:
                            # 根据模板格式化文档
                            formatted_doc = self._format_document(item, template)
                            documents.append(formatted_doc)
                            success_count += 1
                        except Exception as e:
                            error_count += 1
                            error_details.append({
                                "line": line_num,
                                "error": str(e)
                            })
                            print(f"处理第 {line_num} 行文档时出错: {str(e)}")
            except jsonlines.jsonlines.InvalidLineError as e:
                raise HTTPException(status_code=400, detail=f"JSONL 文件格式错误: {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

            if not documents:
                raise HTTPException(status_code=400, detail="没有成功处理任何文档")

            # 保存格式化后的文件
            output_filename = f"formatted_{timestamp}.jsonl"
            output_path = os.path.join(self.output_dir, output_filename)
            
            try:
                with jsonlines.open(output_path, mode='w') as writer:
                    for doc in documents:
                        writer.write(doc)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"保存格式化文件失败: {str(e)}")

            result = {
                "success": True,
                "message": "文件处理完成",
                "document_count": len(documents),
                "success_count": success_count,
                "error_count": error_count,
                "output_path": output_path,
                "error_details": error_details if error_details else None
            }

            # 如果有错误但不是全部失败，返回部分成功的结果
            if error_count > 0 and success_count > 0:
                result["message"] = f"部分处理成功 ({success_count}/{success_count + error_count})"

            return result

        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_jsonl):
                    os.remove(temp_jsonl)
                if os.path.exists(temp_template):
                    os.remove(temp_template)
                # 尝试删除临时目录（如果为空）
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"清理临时文件失败: {str(e)}")

    def _format_document(self, doc: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """根据模板格式化单个文档"""
        try:
            formatted = {}
            template_doc = template["task_template"]["config"]["document_format"]
            
            # 遍历模板中的字段
            for key, value in template_doc.items():
                try:
                    if key in doc:
                        if isinstance(value, dict):
                            formatted[key] = self._format_document(doc[key], {"task_template": {"config": {"document_format": value}}})
                        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                            formatted[key] = [
                                self._format_document(item, {"task_template": {"config": {"document_format": value[0]}}})
                                for item in doc.get(key, [])
                            ]
                        else:
                            formatted[key] = doc[key]
                    else:
                        # 使用模板中的默认值
                        formatted[key] = value
                except Exception as e:
                    raise ValueError(f"处理字段 '{key}' 时出错: {str(e)}")

            return formatted
        except KeyError as e:
            raise ValueError(f"模板格式错误，缺少必要的键: {str(e)}")
        except Exception as e:
            raise ValueError(f"格式化文档失败: {str(e)}")

    def save_formatted_documents(self, documents: List[Document], template: Dict[str, Any], filename: str) -> str:
        """保存格式化后的文档"""
        if not filename.endswith('.jsonl'):
            filename += '.jsonl'
            
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            with jsonlines.open(output_path, mode='w') as writer:
                for doc in documents:
                    writer.write(doc.dict())
            return output_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"保存文档失败: {str(e)}")