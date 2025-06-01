#!/usr/bin/env python3
"""
启动服务器并运行测试的脚本
"""

import subprocess
import time
import sys
import os
import signal
import requests

def check_server_running():
    """检查服务器是否运行"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server():
    """启动服务器"""
    print("🚀 启动服务器...")
    
    # 确保在正确的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 启动服务器
    server_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app.main:app", 
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ])
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    for i in range(30):  # 最多等待30秒
        if check_server_running():
            print("✅ 服务器启动成功！")
            return server_process
        time.sleep(1)
        print(f"   等待中... ({i+1}/30)")
    
    print("❌ 服务器启动失败")
    server_process.terminate()
    return None

def run_tests():
    """运行测试"""
    print("\n🧪 运行认证系统测试...")
    try:
        result = subprocess.run([sys.executable, "test_auth.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("文书标注系统 - 自动启动和测试")
    print("=" * 60)
    
    server_process = None
    
    try:
        # 检查服务器是否已经运行
        if check_server_running():
            print("✅ 服务器已经在运行")
        else:
            # 启动服务器
            server_process = start_server()
            if not server_process:
                sys.exit(1)
        
        # 运行测试
        if run_tests():
            print("\n🎉 所有测试通过！")
        else:
            print("\n❌ 测试失败")
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
    finally:
        # 清理服务器进程
        if server_process:
            print("\n🛑 关闭服务器...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("✅ 服务器已关闭")

if __name__ == "__main__":
    main() 