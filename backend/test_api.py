import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_login(username, password):
    """测试登录"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"登录测试 - {username}:")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"登录成功: {result}")
            return result.get('access_token')
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"请求错误: {e}")
        return None

def test_register(username, password, role="annotator"):
    """测试注册"""
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": username,
        "password": password,
        "role": role
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"注册测试 - {username}:")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"注册成功: {result}")
            return True
        else:
            print(f"注册失败: {response.text}")
            return False
    except Exception as e:
        print(f"请求错误: {e}")
        return False

def test_me(token):
    """测试获取当前用户信息"""
    url = f"{BASE_URL}/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"获取用户信息:")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"用户信息: {result}")
            return result
        else:
            print(f"获取失败: {response.text}")
            return None
    except Exception as e:
        print(f"请求错误: {e}")
        return None

def main():
    print("=== 文书标注系统API测试 ===\n")
    
    # 测试服务器是否运行
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ 后端服务正在运行")
        else:
            print("❌ 后端服务状态异常")
            return
    except:
        print("❌ 无法连接到后端服务，请确保服务已启动")
        return
    
    print("\n1. 测试管理员登录 (admin/admin123)")
    admin_token = test_login("admin", "admin123")
    
    if admin_token:
        print("\n2. 获取管理员用户信息")
        test_me(admin_token)
    
    print("\n3. 尝试注册新的标注员用户")
    # 尝试注册一个新的标注员用户
    test_register("annotator", "123456", "annotator")
    
    print("\n4. 测试标注员登录 (annotator/123456)")
    annotator_token = test_login("annotator", "123456")
    
    if annotator_token:
        print("\n5. 获取标注员用户信息")
        test_me(annotator_token)
    
    print("\n6. 测试错误的登录凭据")
    test_login("admin", "wrongpassword")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 