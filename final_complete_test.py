#!/usr/bin/env python3
"""
最终完整测试
确认保存功能已完全修复
"""

import requests
import json
from pathlib import Path

def complete_test():
    """完整测试保存功能"""
    
    print("🎯 最终完整测试")
    print("=" * 50)
    
    # 步骤1: 登录
    print("🔐 步骤1: 登录")
    try:
        login_response = requests.post(
            "http://localhost:8000/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.text}")
            return False
        
        login_data = login_response.json()
        token = login_data['access_token']
        user_id = login_data['user']['id']
        print(f"✅ 登录成功, 用户ID: {user_id}")
        
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 步骤2: 获取任务列表
    print("\n📋 步骤2: 获取任务列表")
    try:
        tasks_response = requests.get(
            "http://localhost:8000/api/tasks",
            headers=headers,
            timeout=10
        )
        
        if tasks_response.status_code != 200:
            print(f"❌ 获取任务失败: {tasks_response.text}")
            return False
        
        tasks_data = tasks_response.json()
        if not tasks_data.get('tasks'):
            print("❌ 无可用任务")
            return False
        
        task = tasks_data['tasks'][0]
        task_id = task['id']
        document_id = task['documents'][0]['id'] if task.get('documents') else None
        
        if not document_id:
            print("❌ 任务无文档")
            return False
        
        print(f"✅ 找到任务: {task_id}")
        print(f"   文档ID: {document_id}")
        print(f"   分配给: {task.get('assignee_id')}")
        
    except Exception as e:
        print(f"❌ 获取任务异常: {e}")
        return False
    
    # 步骤3: 保存标注
    print("\n💾 步骤3: 保存标注")
    save_url = f"http://localhost:8000/api/annotations/{task_id}/documents/{document_id}/annotation"
    save_data = {
        "annotation_data": {
            "analysis": {
                "topic": "人工智能技术发展趋势分析",
                "keywords": ["人工智能", "机器学习", "深度学习", "神经网络", "数据挖掘"],
                "summary": "本文档深入探讨了人工智能技术的最新发展趋势，重点分析了机器学习、深度学习等核心技术的应用前景，以及神经网络在数据挖掘领域的创新应用。"
            }
        }
    }
    
    try:
        save_response = requests.post(
            save_url,
            json=save_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📡 保存请求: POST {save_url}")
        print(f"📊 状态码: {save_response.status_code}")
        
        if save_response.status_code == 200:
            print("✅ 保存成功!")
            save_result = save_response.json()
            print(f"   标注ID: {save_result.get('document_id')}")
            print(f"   状态: {save_result.get('status')}")
        else:
            print(f"❌ 保存失败: {save_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 保存异常: {e}")
        return False
    
    # 步骤4: 验证文件生成
    print("\n📁 步骤4: 验证文件生成")
    annotation_file = Path(f"data/tasks/{task_id}/annotations/{document_id}.json")
    
    if annotation_file.exists():
        try:
            with open(annotation_file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            print("✅ 标注文件已生成")
            print(f"   文件路径: {annotation_file}")
            print(f"   文件大小: {annotation_file.stat().st_size} 字节")
            
            if file_data.get('annotation_data'):
                ann_data = file_data['annotation_data']
                if ann_data.get('analysis'):
                    analysis = ann_data['analysis']
                    print(f"   主题: {analysis.get('topic', 'N/A')}")
                    print(f"   关键词数: {len(analysis.get('keywords', []))}")
                    print(f"   摘要长度: {len(analysis.get('summary', ''))}")
                    print("✅ 标注数据完整")
                else:
                    print("❌ 缺少analysis数据")
                    return False
            else:
                print("❌ 标注文件无数据")
                return False
                
        except Exception as e:
            print(f"❌ 读取标注文件失败: {e}")
            return False
    else:
        print("❌ 标注文件未生成")
        return False
    
    # 步骤5: 提交标注
    print("\n🚀 步骤5: 提交标注")
    submit_url = f"http://localhost:8000/api/annotations/{task_id}/documents/{document_id}/submit"
    submit_data = {
        "annotation_data": {
            "analysis": {
                "topic": "人工智能技术发展趋势分析",
                "keywords": ["人工智能", "机器学习", "深度学习", "神经网络", "数据挖掘"],
                "summary": "本文档深入探讨了人工智能技术的最新发展趋势，重点分析了机器学习、深度学习等核心技术的应用前景，以及神经网络在数据挖掘领域的创新应用。"
            }
        }
    }
    
    try:
        submit_response = requests.post(
            submit_url,
            json=submit_data,
            headers=headers,
            timeout=10
        )
        
        print(f"📡 提交请求: POST {submit_url}")
        print(f"📊 状态码: {submit_response.status_code}")
        
        if submit_response.status_code == 200:
            print("✅ 提交成功!")
            submit_result = submit_response.json()
            print(f"   最终状态: {submit_result.get('status')}")
            return True
        else:
            print(f"❌ 提交失败: {submit_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 提交异常: {e}")
        return False

def main():
    """主函数"""
    
    if complete_test():
        print("\n🎉 恭喜！保存功能完全正常！")
        print("=" * 50)
        print("✅ 所有测试通过")
        print("✅ 登录功能正常")
        print("✅ 任务访问正常") 
        print("✅ 保存功能正常")
        print("✅ 文件生成正常")
        print("✅ 提交功能正常")
        print("\n💡 现在您可以在前端页面正常使用:")
        print("   - 点击保存按钮保存标注")
        print("   - 点击完成并提交按钮提交标注")
        print("   - 查看任务状态的更新")
        
        print("\n📋 问题解决总结:")
        print("   1. 修复了任务数据格式问题")
        print("   2. 修复了用户ID映射问题") 
        print("   3. 验证了Storage层正常工作")
        print("   4. 验证了API层正常工作")
        print("   5. 验证了完整的保存->提交流程")
    else:
        print("\n❌ 测试失败，仍有问题需要解决")

if __name__ == "__main__":
    main() 