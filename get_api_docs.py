#!/usr/bin/env python3
"""
API 文档获取脚本
从 SwaggerUI 的 OpenAPI JSON 端点获取完整的 API 接口文档
"""

import requests
import json
import sys
from typing import Dict, Any, List
from datetime import datetime


class APIDocumentationExtractor:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.openapi_url = f"{self.base_url}/openapi.json"
        
    def fetch_openapi_spec(self) -> Dict[str, Any]:
        """获取 OpenAPI 规范"""
        try:
            print(f"正在从 {self.openapi_url} 获取 API 文档...")
            response = requests.get(self.openapi_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取 API 文档失败: {e}")
            print(f"请确保后端服务正在运行: {self.base_url}")
            sys.exit(1)
    
    def extract_api_info(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """提取 API 信息"""
        info = {
            "title": spec.get("info", {}).get("title", "Unknown API"),
            "version": spec.get("info", {}).get("version", "Unknown"),
            "description": spec.get("info", {}).get("description", ""),
            "servers": spec.get("servers", []),
            "paths": spec.get("paths", {}),
            "components": spec.get("components", {}),
            "tags": spec.get("tags", [])
        }
        return info
    
    def format_endpoint(self, path: str, method: str, details: Dict[str, Any]) -> str:
        """格式化单个端点信息"""
        lines = []
        
        # 基本信息
        summary = details.get("summary", "")
        description = details.get("description", "")
        tags = details.get("tags", [])
        
        lines.append(f"### {method.upper()} {path}")
        if summary:
            lines.append(f"**摘要**: {summary}")
        if description:
            lines.append(f"**描述**: {description}")
        if tags:
            lines.append(f"**标签**: {', '.join(tags)}")
        
        # 请求参数
        parameters = details.get("parameters", [])
        if parameters:
            lines.append("\n**请求参数**:")
            for param in parameters:
                param_name = param.get("name", "")
                param_type = param.get("schema", {}).get("type", "")
                param_desc = param.get("description", "")
                param_required = "必需" if param.get("required", False) else "可选"
                param_location = param.get("in", "")
                
                lines.append(f"- `{param_name}` ({param_location}) - {param_type} - {param_required}")
                if param_desc:
                    lines.append(f"  {param_desc}")
        
        # 请求体
        request_body = details.get("requestBody", {})
        if request_body:
            lines.append("\n**请求体**:")
            content = request_body.get("content", {})
            for content_type, schema_info in content.items():
                lines.append(f"- Content-Type: `{content_type}`")
                schema_ref = schema_info.get("schema", {}).get("$ref", "")
                if schema_ref:
                    schema_name = schema_ref.split("/")[-1]
                    lines.append(f"  Schema: `{schema_name}`")
        
        # 响应
        responses = details.get("responses", {})
        if responses:
            lines.append("\n**响应**:")
            for status_code, response_info in responses.items():
                desc = response_info.get("description", "")
                lines.append(f"- `{status_code}`: {desc}")
                
                content = response_info.get("content", {})
                for content_type, schema_info in content.items():
                    schema_ref = schema_info.get("schema", {}).get("$ref", "")
                    if schema_ref:
                        schema_name = schema_ref.split("/")[-1]
                        lines.append(f"  返回类型: `{schema_name}` ({content_type})")
        
        lines.append("\n" + "-" * 80 + "\n")
        return "\n".join(lines)
    
    def generate_markdown_doc(self, api_info: Dict[str, Any]) -> str:
        """生成 Markdown 格式的文档"""
        lines = []
        
        # 标题和基本信息
        lines.append(f"# {api_info['title']}")
        lines.append(f"**版本**: {api_info['version']}")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        if api_info['description']:
            lines.append("## 描述")
            lines.append(api_info['description'])
            lines.append("")
        
        # 服务器信息
        if api_info['servers']:
            lines.append("## 服务器")
            for server in api_info['servers']:
                url = server.get('url', '')
                desc = server.get('description', '')
                lines.append(f"- {url} - {desc}")
            lines.append("")
        
        # 标签分组
        tags_dict = {}
        for tag in api_info.get('tags', []):
            tags_dict[tag['name']] = tag.get('description', '')
        
        if tags_dict:
            lines.append("## API 模块")
            for tag_name, tag_desc in tags_dict.items():
                lines.append(f"- **{tag_name}**: {tag_desc}")
            lines.append("")
        
        # API 端点统计
        total_endpoints = 0
        methods_count = {}
        
        for path, methods in api_info['paths'].items():
            for method in methods.keys():
                if method not in ['parameters']:
                    total_endpoints += 1
                    methods_count[method.upper()] = methods_count.get(method.upper(), 0) + 1
        
        lines.append("## API 统计")
        lines.append(f"- 总端点数: {total_endpoints}")
        lines.append("- 方法分布:")
        for method, count in sorted(methods_count.items()):
            lines.append(f"  - {method}: {count}")
        lines.append("")
        
        # 按标签分组显示 API
        lines.append("## API 端点详情")
        
        # 收集所有端点并按标签分组
        endpoints_by_tag = {}
        
        for path, methods in api_info['paths'].items():
            for method, details in methods.items():
                if method == 'parameters':
                    continue
                    
                tags = details.get('tags', ['未分类'])
                for tag in tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append((path, method, details))
        
        # 按标签输出
        for tag, endpoints in sorted(endpoints_by_tag.items()):
            lines.append(f"## {tag}")
            lines.append("")
            
            for path, method, details in sorted(endpoints):
                lines.append(self.format_endpoint(path, method, details))
        
        return "\n".join(lines)
    
    def generate_json_doc(self, api_info: Dict[str, Any]) -> str:
        """生成 JSON 格式的简化文档"""
        simplified_doc = {
            "api_info": {
                "title": api_info['title'],
                "version": api_info['version'],
                "description": api_info['description'],
                "generated_at": datetime.now().isoformat()
            },
            "endpoints": []
        }
        
        for path, methods in api_info['paths'].items():
            for method, details in methods.items():
                if method == 'parameters':
                    continue
                    
                endpoint = {
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get('summary', ''),
                    "description": details.get('description', ''),
                    "tags": details.get('tags', []),
                    "parameters": [],
                    "responses": {}
                }
                
                # 提取参数
                for param in details.get('parameters', []):
                    endpoint['parameters'].append({
                        "name": param.get('name', ''),
                        "in": param.get('in', ''),
                        "type": param.get('schema', {}).get('type', ''),
                        "required": param.get('required', False),
                        "description": param.get('description', '')
                    })
                
                # 提取响应
                for status, response in details.get('responses', {}).items():
                    endpoint['responses'][status] = response.get('description', '')
                
                simplified_doc['endpoints'].append(endpoint)
        
        return json.dumps(simplified_doc, ensure_ascii=False, indent=2)
    
    def save_documentation(self, content: str, filename: str):
        """保存文档到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 文档已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
    
    def run(self):
        """运行文档提取"""
        print("🚀 开始获取 API 文档...")
        
        # 获取 OpenAPI 规范
        spec = self.fetch_openapi_spec()
        api_info = self.extract_api_info(spec)
        
        print(f"📋 API 标题: {api_info['title']}")
        print(f"📋 API 版本: {api_info['version']}")
        print(f"📋 端点总数: {len(api_info['paths'])}")
        
        # 生成不同格式的文档
        print("\n📝 生成文档...")
        
        # Markdown 格式
        markdown_doc = self.generate_markdown_doc(api_info)
        self.save_documentation(markdown_doc, "api_documentation.md")
        
        # JSON 格式
        json_doc = self.generate_json_doc(api_info)
        self.save_documentation(json_doc, "api_documentation.json")
        
        # 原始 OpenAPI 规范
        original_spec = json.dumps(spec, ensure_ascii=False, indent=2)
        self.save_documentation(original_spec, "openapi_spec.json")
        
        print("\n🎉 文档生成完成!")
        print("生成的文件:")
        print("- api_documentation.md (Markdown 格式的详细文档)")
        print("- api_documentation.json (JSON 格式的简化文档)")
        print("- openapi_spec.json (原始 OpenAPI 规范)")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="从 SwaggerUI 获取 API 文档")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="API 服务器地址 (默认: http://localhost:8000)"
    )
    parser.add_argument(
        "--format",
        choices=["all", "markdown", "json", "openapi"],
        default="all",
        help="输出格式 (默认: all)"
    )
    
    args = parser.parse_args()
    
    extractor = APIDocumentationExtractor(args.url)
    
    try:
        if args.format == "all":
            extractor.run()
        else:
            # 获取基本信息
            spec = extractor.fetch_openapi_spec()
            api_info = extractor.extract_api_info(spec)
            
            if args.format == "markdown":
                doc = extractor.generate_markdown_doc(api_info)
                extractor.save_documentation(doc, "api_documentation.md")
            elif args.format == "json":
                doc = extractor.generate_json_doc(api_info)
                extractor.save_documentation(doc, "api_documentation.json")
            elif args.format == "openapi":
                doc = json.dumps(spec, ensure_ascii=False, indent=2)
                extractor.save_documentation(doc, "openapi_spec.json")
                
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        sys.exit(1)


if __name__ == "__main__":
    main() 