#!/usr/bin/env python3
"""
测试 API 连接的简单脚本
"""

import requests
import sys

def test_api_connection(base_url="http://localhost:8000"):
    """测试 API 连接"""
    
    print(f"🔍 测试 API 连接: {base_url}")
    
    # 测试基本连接
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ 基本连接成功 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 基本连接失败: {e}")
        return False
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ 健康检查通过")
        else:
            print(f"⚠️ 健康检查异常 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 测试 OpenAPI 端点
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            spec = response.json()
            title = spec.get("info", {}).get("title", "Unknown")
            version = spec.get("info", {}).get("version", "Unknown")
            paths_count = len(spec.get("paths", {}))
            print(f"✅ OpenAPI 文档可访问")
            print(f"   API 名称: {title}")
            print(f"   版本: {version}")
            print(f"   端点数量: {paths_count}")
            return True
        else:
            print(f"❌ OpenAPI 文档不可访问 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ OpenAPI 文档访问失败: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试 API 连接")
    parser.add_argument("--url", default="http://localhost:8000", help="API 服务器地址")
    
    args = parser.parse_args()
    
    success = test_api_connection(args.url)
    
    if success:
        print(f"\n🎉 API 服务正常运行！")
        print(f"你可以使用以下命令获取 API 文档:")
        print(f"  python quick_api_list.py --url {args.url}")
        print(f"  python get_api_docs.py --url {args.url}")
        print(f"\n或者直接访问:")
        print(f"  SwaggerUI: {args.url}/docs")
        print(f"  ReDoc: {args.url}/redoc")
    else:
        print(f"\n❌ API 服务不可用，请检查:")
        print(f"  1. 后端服务是否正在运行")
        print(f"  2. 服务器地址是否正确: {args.url}")
        print(f"  3. 防火墙或网络设置")
        sys.exit(1) 