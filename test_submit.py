#!/usr/bin/env python3
import requests
import json

def test_submit():
    # 登录
    login_response = requests.post('http://localhost:8000/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 提交标注
    task_id = 'task_d09fdf6d'
    document_id = 'doc_c88a6864'
    submit_url = f'http://localhost:8000/api/annotations/{task_id}/documents/{document_id}/submit'
    submit_data = {
        'annotation_data': {
            'analysis': {
                'topic': '人工智能技术发展趋势分析',
                'keywords': ['人工智能', '机器学习', '深度学习', '神经网络', '数据挖掘'],
                'summary': '本文档深入探讨了人工智能技术的最新发展趋势，重点分析了机器学习、深度学习等核心技术的应用前景，以及神经网络在数据挖掘领域的创新应用。'
            }
        }
    }

    submit_response = requests.post(submit_url, json=submit_data, headers=headers)
    print(f'提交状态码: {submit_response.status_code}')
    if submit_response.status_code == 200:
        result = submit_response.json()
        print(f'提交成功! 状态: {result.get("status")}')
        
        # 检查文件更新
        import pathlib
        annotation_file = pathlib.Path('backend/data/tasks/task_d09fdf6d/annotations/doc_c88a6864.json')
        if annotation_file.exists():
            with open(annotation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f'文件状态: {data.get("status")}')
            print('✅ 提交功能正常工作!')
    else:
        print(f'提交失败: {submit_response.text}')

if __name__ == "__main__":
    test_submit() 