from typing import Dict, Any, List, Optional
import openai
import json
import os
from datetime import datetime

class AIReviewService:
    """AI审查服务"""
    
    def __init__(self, api_key: str, output_dir: str):
        self.api_key = api_key
        self.output_dir = output_dir
        openai.api_key = api_key
        os.makedirs(output_dir, exist_ok=True)
    
    def review_document(self, document: Dict[str, Any], prompt_template: str) -> Dict[str, Any]:
        """审查单个文档"""
        # 构建提示
        prompt = prompt_template.format(**document)
        
        # 调用OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业的法律文书审查助手。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 解析响应
        review_result = response.choices[0].message.content
        
        return {
            "document_id": document.get("id", ""),
            "review_result": review_result,
            "reviewed_at": datetime.now().isoformat()
        }
    
    def batch_review(self, documents: List[Dict[str, Any]], prompt_template: str) -> List[Dict[str, Any]]:
        """批量审查文档"""
        results = []
        for doc in documents:
            result = self.review_document(doc, prompt_template)
            results.append(result)
        
        return results
    
    def save_review_results(self, task_id: str, results: List[Dict[str, Any]]):
        """保存审查结果"""
        task_dir = os.path.join(self.output_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        output_path = os.path.join(task_dir, "ai_review_results.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def compare_with_human_annotation(self, task_id: str) -> Dict[str, Any]:
        """比较AI审查结果与人工标注"""
        task_dir = os.path.join(self.output_dir, task_id)
        
        # 加载AI审查结果
        ai_results_path = os.path.join(task_dir, "ai_review_results.json")
        with open(ai_results_path, 'r', encoding='utf-8') as f:
            ai_results = json.load(f)
        
        # 加载人工标注结果
        human_annotations = {}
        for filename in os.listdir(task_dir):
            if filename.endswith("_annotation.json"):
                with open(os.path.join(task_dir, filename), 'r', encoding='utf-8') as f:
                    doc_id = filename.replace("_annotation.json", "")
                    human_annotations[doc_id] = json.load(f)
        
        # 比较结果
        comparison = {
            "total_documents": len(ai_results),
            "matching_documents": 0,
            "differences": []
        }
        
        for ai_result in ai_results:
            doc_id = ai_result["document_id"]
            if doc_id in human_annotations:
                if self._compare_annotations(ai_result, human_annotations[doc_id]):
                    comparison["matching_documents"] += 1
                else:
                    comparison["differences"].append({
                        "document_id": doc_id,
                        "ai_result": ai_result,
                        "human_annotation": human_annotations[doc_id]
                    })
        
        return comparison
    
    def _compare_annotations(self, ai_result: Dict[str, Any], human_annotation: Dict[str, Any]) -> bool:
        """比较AI结果和人工标注"""
        # 这里可以根据具体需求实现比较逻辑
        return ai_result["review_result"] == human_annotation.get("review_result", "") 