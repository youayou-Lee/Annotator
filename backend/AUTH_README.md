# 文书标注系统 - 用户认证系统

## 概述

本系统实现了完整的基于JWT的用户认证和授权系统，支持三种用户角色：
- **super_admin**: 超级管理员，拥有所有权限
- **admin**: 管理员，可以管理用户和任务
- **annotator**: 标注员，只能进行标注工作

## 功能特性

### 🔐 认证功能
- ✅ 用户注册和登录
- ✅ JWT令牌认证
- ✅ 令牌刷新
- ✅ 密码修改
- ✅ 密码强度验证
- ✅ 用户名格式验证

### 👥 用户管理
- ✅ 用户列表查看（管理员权限）
- ✅ 用户信息更新
- ✅ 用户删除（超级管理员权限）
- ✅ 角色管理

### 🛡️ 权限控制
- ✅ 基于角色的访问控制（RBAC）
- ✅ 权限装饰器
- ✅ 细粒度权限检查
- ✅ 防止权限提升攻击

### 🔒 安全特性
- ✅ 密码哈希存储（bcrypt）
- ✅ JWT令牌签名验证
- ✅ 输入数据验证
- ✅ 错误处理和日志记录

## API接口

### 认证接口

#### 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

响应：
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "user_12345678",
    "username": "admin",
    "role": "super_admin"
  }
}
```

#### 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123",
  "role": "annotator"
}
```

#### 获取当前用户信息
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### 刷新令牌
```http
POST /api/auth/refresh
Authorization: Bearer <access_token>
```

#### 修改密码
```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "oldpass123",
  "new_password": "newpass123"
}
```

### 用户管理接口

#### 获取用户列表（需要管理员权限）
```http
GET /api/users
Authorization: Bearer <admin_token>
```

#### 获取用户详情
```http
GET /api/users/{user_id}
Authorization: Bearer <access_token>
```

#### 更新用户信息
```http
PUT /api/users/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "username": "newusername",
  "password": "newpassword",
  "role": "admin"
}
```

#### 删除用户（需要超级管理员权限）
```http
DELETE /api/users/{user_id}
Authorization: Bearer <super_admin_token>
```

## 权限矩阵

| 功能 | super_admin | admin | annotator |
|------|-------------|-------|-----------|
| 用户管理 | ✅ | ✅ | ❌ |
| 文件上传 | ✅ | ✅ | ✅ |
| 文件删除 | ✅ | ✅ | 仅自己上传 |
| 任务创建 | ✅ | ✅ | 仅分配给自己 |
| 任务分配 | ✅ | ✅ | ❌ |
| 标注工作 | ✅ | ✅ | ✅ |
| 复审功能 | ✅ | ✅ | ❌ |
| 角色管理 | ✅ | ❌ | ❌ |
| 用户删除 | ✅ | ❌ | ❌ |

## 快速开始

### 1. 安装依赖
```bash
cd backend
conda activate annotator
pip install -r requirements.txt
```

### 2. 启动服务器
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 3. 初始管理员账户
系统启动时会自动创建初始管理员账户：
- 用户名: `admin`
- 密码: `admin123`
- 角色: `super_admin`

**⚠️ 请在生产环境中立即修改默认密码！**

### 4. 运行测试
```bash
# 运行认证系统测试
python test_auth.py

# 或者使用自动启动和测试脚本
python start_and_test.py
```

## 使用示例

### Python客户端示例
```python
import requests

# 登录获取令牌
login_response = requests.post("http://localhost:8000/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = login_response.json()["access_token"]

# 使用令牌访问受保护的接口
headers = {"Authorization": f"Bearer {token}"}
users_response = requests.get("http://localhost:8000/api/users", headers=headers)
users = users_response.json()
print(f"用户列表: {users}")
```

### JavaScript客户端示例
```javascript
// 登录
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});
const { access_token } = await loginResponse.json();

// 获取用户列表
const usersResponse = await fetch('http://localhost:8000/api/users', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const users = await usersResponse.json();
console.log('用户列表:', users);
```

## 配置说明

### 环境变量
可以通过`.env`文件配置以下参数：

```env
# 安全配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATA_DIR=data

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### 密码策略
- 最小长度：6个字符
- 支持的字符：所有可打印字符
- 存储方式：bcrypt哈希

### 用户名规则
- 长度：3-20个字符
- 允许字符：字母、数字、下划线
- 不允许重复

## 安全建议

1. **生产环境配置**
   - 修改默认的SECRET_KEY
   - 使用强密码策略
   - 启用HTTPS
   - 设置合适的令牌过期时间

2. **权限管理**
   - 遵循最小权限原则
   - 定期审查用户权限
   - 及时删除不需要的账户

3. **监控和日志**
   - 监控异常登录尝试
   - 记录权限变更日志
   - 设置告警机制

## 故障排除

### 常见问题

1. **无法连接到服务器**
   - 检查服务器是否启动
   - 确认端口8000未被占用
   - 检查防火墙设置

2. **认证失败**
   - 确认用户名和密码正确
   - 检查令牌是否过期
   - 验证令牌格式

3. **权限不足**
   - 确认用户角色
   - 检查接口权限要求
   - 验证令牌有效性

### 调试模式
启用调试模式可以获得更详细的错误信息：
```bash
export DEBUG=true
python -m uvicorn app.main:app --reload --log-level debug
```

## 开发指南

### 添加新的权限检查
```python
from app.core.security import require_roles, UserRole

@require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN])
async def admin_only_function():
    pass
```

### 自定义权限装饰器
```python
def require_custom_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 自定义权限检查逻辑
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## 更新日志

### v1.0.0 (当前版本)
- ✅ 基础认证功能
- ✅ 用户管理
- ✅ 权限控制
- ✅ 安全特性
- ✅ 测试套件

## 支持

如有问题或建议，请联系开发团队或提交Issue。 