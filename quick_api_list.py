#!/usr/bin/env python3
"""
快速获取 API 接口列表脚本
从 SwaggerUI 快速获取所有 API 端点的简要信息
"""

import requests
import json
from typing import Dict, Any


def get_api_list(base_url: str = "http://localhost:8000"):
    """快速获取 API 接口列表"""
    
    openapi_url = f"{base_url.rstrip('/')}/openapi.json"
    
    try:
        print(f"🔍 正在获取 API 文档: {openapi_url}")
        response = requests.get(openapi_url, timeout=10)
        response.raise_for_status()
        spec = response.json()
        
        # 基本信息
        info = spec.get("info", {})
        title = info.get("title", "Unknown API")
        version = info.get("version", "Unknown")
        
        print(f"\n📋 API 名称: {title}")
        print(f"📋 版本: {version}")
        print(f"📋 服务器: {base_url}")
        
        # 统计信息
        paths = spec.get("paths", {})
        total_endpoints = 0
        methods_count = {}
        
        # 收集所有端点
        endpoints = []
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method == 'parameters':
                    continue
                    
                total_endpoints += 1
                method_upper = method.upper()
                methods_count[method_upper] = methods_count.get(method_upper, 0) + 1
                
                endpoints.append({
                    "method": method_upper,
                    "path": path,
                    "summary": details.get("summary", ""),
                    "tags": details.get("tags", [])
                })
        
        print(f"\n📊 统计信息:")
        print(f"   总端点数: {total_endpoints}")
        for method, count in sorted(methods_count.items()):
            print(f"   {method}: {count}")
        
        # 按标签分组显示
        print(f"\n🔗 API 端点列表:")
        print("=" * 80)
        
        # 按标签分组
        endpoints_by_tag = {}
        for endpoint in endpoints:
            tags = endpoint["tags"] if endpoint["tags"] else ["未分类"]
            for tag in tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)
        
        # 显示每个分组
        for tag, tag_endpoints in sorted(endpoints_by_tag.items()):
            print(f"\n📁 {tag}")
            print("-" * 40)
            
            for endpoint in sorted(tag_endpoints, key=lambda x: (x["path"], x["method"])):
                method_color = {
                    "GET": "🟢",
                    "POST": "🟡", 
                    "PUT": "🔵",
                    "DELETE": "🔴",
                    "PATCH": "🟠"
                }.get(endpoint["method"], "⚪")
                
                summary = endpoint["summary"]
                if len(summary) > 50:
                    summary = summary[:47] + "..."
                
                print(f"  {method_color} {endpoint['method']:<6} {endpoint['path']:<30} {summary}")
        
        # 生成简单的测试命令
        print(f"\n🧪 测试示例:")
        print("=" * 80)
        print("# 获取 API 文档")
        print(f"curl {base_url}/docs")
        print(f"curl {base_url}/openapi.json")
        
        # 找一些常见的端点作为示例
        common_endpoints = [ep for ep in endpoints if any(keyword in ep["path"].lower() 
                           for keyword in ["login", "health", "users", "tasks"])]
        
        if common_endpoints:
            print("\n# 常用端点测试:")
            for endpoint in common_endpoints[:3]:  # 只显示前3个
                if endpoint["method"] == "GET":
                    print(f"curl -X {endpoint['method']} {base_url}{endpoint['path']}")
                elif endpoint["method"] == "POST" and "login" in endpoint["path"]:
                    print(f'curl -X POST {base_url}{endpoint["path"]} \\')
                    print('     -H "Content-Type: application/json" \\')
                    print('     -d \'{"username":"admin","password":"admin123"}\'')
        
        return endpoints
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取 API 文档失败: {e}")
        print(f"请确保后端服务正在运行: {base_url}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ 解析 JSON 失败: {e}")
        return []
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return []


def save_simple_list(endpoints, filename="api_list.txt"):
    """保存简单的 API 列表到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("API 接口列表\n")
            f.write("=" * 50 + "\n\n")
            
            for endpoint in sorted(endpoints, key=lambda x: (x["path"], x["method"])):
                f.write(f"{endpoint['method']:<6} {endpoint['path']:<40} {endpoint['summary']}\n")
        
        print(f"\n✅ API 列表已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="快速获取 API 接口列表")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="API 服务器地址 (默认: http://localhost:8000)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="保存 API 列表到文件"
    )
    
    args = parser.parse_args()
    
    endpoints = get_api_list(args.url)
    
    if endpoints and args.save:
        save_simple_list(endpoints)


if __name__ == "__main__":
    main() 