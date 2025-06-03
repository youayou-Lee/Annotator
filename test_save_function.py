#!/usr/bin/env python3
"""
测试标注保存功能
检查保存机制是否正常工作
"""

import requests
import json
import os
from pathlib import Path

def test_annotation_save():
    """测试标注数据保存功能"""
    
    print("🔍 测试标注保存功能...")
    
    # 1. 检查后端服务是否运行
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正在运行")
        else:
            print("❌ 后端服务无响应")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接后端服务: {e}")
        print("💡 请确保后端已启动: uvicorn app.main:app --reload")
        return False
    
    # 2. 检查数据目录结构
    data_dir = Path("data")
    if not data_dir.exists():
        print(f"❌ 数据目录不存在: {data_dir}")
        return False
    
    tasks_dir = data_dir / "tasks"
    if not tasks_dir.exists():
        print(f"❌ 任务目录不存在: {tasks_dir}")
        return False
    
    print(f"✅ 数据目录结构正常: {data_dir}")
    
    # 3. 检查是否有任务数据
    task_dirs = [d for d in tasks_dir.iterdir() if d.is_dir()]
    if not task_dirs:
        print("⚠️  未找到任务目录，可能需要先创建任务")
        return False
    
    print(f"✅ 找到 {len(task_dirs)} 个任务目录")
    
    # 4. 检查最新任务的标注目录
    latest_task = task_dirs[0]  # 使用第一个任务
    annotations_dir = latest_task / "annotations"
    
    print(f"📁 检查任务目录: {latest_task.name}")
    print(f"📁 标注目录: {annotations_dir}")
    
    if annotations_dir.exists():
        annotation_files = list(annotations_dir.glob("*.json"))
        print(f"✅ 找到 {len(annotation_files)} 个标注文件")
        
        if annotation_files:
            # 显示最新的标注文件内容
            latest_annotation = annotation_files[0]
            print(f"📄 最新标注文件: {latest_annotation.name}")
            
            try:
                with open(latest_annotation, 'r', encoding='utf-8') as f:
                    annotation_data = json.load(f)
                    print(f"✅ 标注数据结构:")
                    print(f"   - 文档ID: {annotation_data.get('document_id', 'N/A')}")
                    print(f"   - 任务ID: {annotation_data.get('task_id', 'N/A')}")
                    print(f"   - 状态: {annotation_data.get('status', 'N/A')}")
                    print(f"   - 更新时间: {annotation_data.get('updated_at', 'N/A')}")
                    print(f"   - 有标注数据: {'是' if annotation_data.get('annotation_data') else '否'}")
                    
            except Exception as e:
                print(f"❌ 读取标注文件失败: {e}")
    else:
        print("⚠️  标注目录不存在，可能尚未进行标注")
    
    # 5. 检查前端构建状态
    frontend_dist = Path("frontend/dist")
    if frontend_dist.exists():
        print("✅ 前端已构建")
    else:
        print("⚠️  前端未构建，可能需要运行: npm run build")
    
    return True

def check_save_api_endpoints():
    """检查保存相关的API端点"""
    
    print("\n🔍 检查保存相关API端点...")
    
    api_endpoints = [
        "/api/annotations/{task_id}/documents/{document_id}/annotation",
        "/api/annotations/{task_id}/documents/{document_id}/submit"
    ]
    
    try:
        # 获取API文档
        response = requests.get("http://localhost:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            print("✅ 发现的保存相关API端点:")
            for path in paths:
                if "annotation" in path and ("POST" in paths[path] or "PUT" in paths[path]):
                    methods = list(paths[path].keys())
                    print(f"   - {path} [{', '.join(methods)}]")
                    
        else:
            print("❌ 无法获取API文档")
            
    except Exception as e:
        print(f"❌ 检查API端点失败: {e}")

def main():
    """主函数"""
    print("🧪 标注保存功能测试")
    print("=" * 50)
    
    # 测试保存功能
    if test_annotation_save():
        print("\n✅ 基础检查通过")
    else:
        print("\n❌ 基础检查失败")
        return
    
    # 检查API端点
    check_save_api_endpoints()
    
    print("\n" + "=" * 50)
    print("💡 保存功能说明:")
    print("   1. 点击 '保存更改' 按钮保存到后端")
    print("   2. 原始文件不会被修改")
    print("   3. 标注结果保存在 data/tasks/{task_id}/annotations/ 目录")
    print("   4. 支持自动保存和手动保存")
    print("   5. 可以点击 '导出' 按钮下载JSON文件")
    
    print("\n🔧 如果保存不工作，请检查:")
    print("   1. 后端服务是否启动")
    print("   2. 用户是否有任务权限")
    print("   3. 浏览器控制台是否有错误")
    print("   4. 网络连接是否正常")

if __name__ == "__main__":
    main() 