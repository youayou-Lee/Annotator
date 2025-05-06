from typing import Dict, Any, List, Optional
from ..models.document import Document
import json
import os, glob
from datetime import datetime
import jsonlines
from fastapi import UploadFile, HTTPException
from ..schemas import JsonChecker
from pathlib import Path
class FormatService:
    """格式化存储服务"""
    def __init__(self, output_dir: str = "data/formatted"):
        self.output_dir = output_dir
        # 确保目录存在
        os.makedirs(output_dir, exist_ok=True)
        # 确保默认模板目录存在
        os.makedirs("data/task_templates", exist_ok=True)

        self.templates_dir = os.path.join("data", "format_templates")

    async def process_file(self, jsonl_file: UploadFile, template_file: Optional[UploadFile] = None) -> Dict[str, Any]:
        """处理上传的JSONL文件和Python模板文件"""
        # 验证输入文件
        if not jsonl_file.filename.endswith('.jsonl'):
            raise HTTPException(status_code=400, detail="只接受 JSONL 格式的文件")

        if template_file and not template_file.filename.endswith('.py'):
            raise HTTPException(status_code=400, detail="模板文件必须是 Python (.py) 格式")

        # 创建临时目录
        temp_dir = os.path.join(self.output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:
            # 保存上传的文件到临时目录
            temp_jsonl = os.path.join(temp_dir, f"temp_{timestamp}.jsonl")
            with open(temp_jsonl, 'wb') as f:
                content = await jsonl_file.read()
                if not content:
                    raise HTTPException(status_code=400, detail="JSONL 文件内容为空")
                f.write(content)
                await jsonl_file.seek(0)

            # 初始化校验器
            if template_file:
                temp_py = os.path.join(temp_dir, f"temp_{timestamp}.py")
                with open(temp_py, 'wb') as f:
                    content = await template_file.read()
                    if not content:
                        raise HTTPException(status_code=400, detail="模板文件内容为空")
                    f.write(content)
                checker = JsonChecker(model_file=Path(temp_py))
            else:
                checker = JsonChecker(default_model=Document)

            # 处理JSONL文件
            documents = []
            success_count = 0
            error_count = 0
            error_details = []

            with open(temp_jsonl, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    try:
                        item = json.loads(line)
                        validated_doc = checker.validate(item)[0]  # 取第一个（因为validate返回列表）
                        formatted_doc = checker.fill_template([validated_doc])[0]
                        documents.append(formatted_doc)
                        success_count += 1
                    except json.JSONDecodeError as e:
                        error_count += 1
                        error_details.append({"line": line_num, "error": f"JSON解析错误: {str(e)}"})
                    except Exception as e:
                        error_count += 1
                        error_details.append({"line": line_num, "error": str(e)})

            if not documents:
                raise HTTPException(status_code=400, detail="没有成功处理任何文档")

            # 保存结果
            output_filename = f"formatted_{timestamp}.jsonl"
            output_path = os.path.join(self.output_dir, output_filename)
            with jsonlines.open(output_path, mode='w') as writer:
                writer.write_all(documents)

            return {
                "success": True,
                "message": f"文件处理完成 ({success_count}成功, {error_count}错误)" if error_count else "文件处理完成",
                "document_count": len(documents),
                "success_count": success_count,
                "error_count": error_count,
                "output_path": output_path,
                "error_details": error_details if error_details else None
            }

        finally:
            # 清理临时文件
            for f in glob.glob(os.path.join(temp_dir, f"temp_{timestamp}.*")):
                try:
                    os.remove(f)
                except Exception:
                    pass
            try:
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception:
                pass
    def get_default_template(self) -> List[str]:
        """获取默认模板文件列表"""
        try:
            templates = []
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.py'):
                    templates.append(filename)
            return templates
        except Exception as e:
            raise Exception(f"获取模板列表失败: {str(e)}")