# 文书标注系统前端

## 项目概述

这是文书标注系统的前端部分，基于 React + TypeScript + Ant Design 构建，实现了完整的用户认证和权限控制系统。

## 技术栈

- **React 18** - 前端框架
- **TypeScript** - 类型安全
- **Ant Design 5** - UI组件库
- **React Router 6** - 路由管理
- **Zustand** - 状态管理
- **Axios** - HTTP客户端
- **React Query** - 数据获取和缓存
- **Vite** - 构建工具

## 功能特性

### 🔐 用户认证系统

- **登录/注册** - 支持用户名密码登录和新用户注册
- **自动Token刷新** - 自动处理Token过期和刷新
- **记住登录状态** - 支持持久化登录状态
- **安全登出** - 清除所有认证信息

### 👥 权限控制系统

- **基于角色的权限控制（RBAC）**
  - `super_admin` - 超级管理员
  - `admin` - 管理员  
  - `annotator` - 标注员

- **细粒度权限控制**
  - `user.manage` - 用户管理权限
  - `file.upload` - 文件上传权限
  - `file.delete.all` - 删除所有文件权限
  - `file.delete.own` - 删除自己文件权限
  - `task.create` - 任务创建权限
  - `task.assign` - 任务分配权限
  - `task.annotate` - 任务标注权限
  - `task.review` - 任务复审权限
  - `task.export` - 任务导出权限

### 🛡️ 路由守卫

- **认证守卫** - 未登录用户自动跳转到登录页
- **权限守卫** - 根据用户权限控制页面访问
- **角色守卫** - 基于用户角色的页面访问控制

### 🎨 用户界面

- **响应式设计** - 适配不同屏幕尺寸
- **现代化UI** - 基于Ant Design的美观界面
- **用户友好** - 直观的操作流程和反馈

## 项目结构

```
src/
├── components/          # 公共组件
│   ├── AuthInitializer/ # 认证初始化器
│   └── Layout/         # 布局组件
├── pages/              # 页面组件
│   ├── Login/          # 登录/注册页面
│   ├── TaskList/       # 任务列表页面
│   ├── FileLibrary/    # 文件库页面
│   ├── UserManagement/ # 用户管理页面
│   ├── TaskDetail/     # 任务详情页面
│   ├── Annotation/     # 标注页面
│   └── Review/         # 复审页面
├── router/             # 路由配置
├── services/           # API服务
├── stores/             # 状态管理
├── types/              # TypeScript类型定义
├── App.tsx             # 应用入口
└── main.tsx           # 主入口文件
```

## 快速开始

### 环境要求

- Node.js >= 16
- npm >= 8

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

## 使用说明

### 1. 用户注册和登录

#### 注册新用户
1. 访问注册页面 `/register`
2. 填写用户名、密码、确认密码
3. 选择角色（标注员/管理员）
4. 点击注册按钮

#### 登录系统
1. 访问登录页面 `/login`
2. 输入用户名和密码
3. 可选择"记住登录状态"
4. 点击登录按钮

#### 演示账户
- 管理员：`admin` / `admin123`
- 标注员：`annotator` / `123456`

### 2. 权限系统演示

登录后可以在任务列表页面查看：
- 当前用户信息
- 用户权限检查结果
- 用户角色检查结果

### 3. 页面访问控制

- **所有用户**：任务列表、文件库
- **管理员及以上**：用户管理、任务创建、任务复审
- **所有登录用户**：任务标注

### 4. 用户管理（仅管理员）

1. 访问用户管理页面 `/users`
2. 查看用户列表
3. 编辑用户信息
4. 创建新用户（开发中）
5. 删除用户（开发中）

## 状态管理

### 认证状态 (authStore)

```typescript
interface AuthState {
  user: User | null              // 当前用户信息
  token: string | null           // 认证Token
  isAuthenticated: boolean       // 是否已认证
  isLoading: boolean            // 加载状态
  isInitialized: boolean        // 是否已初始化
}
```

### 主要方法

- `login(user, token)` - 用户登录
- `logout()` - 用户登出
- `initializeAuth()` - 初始化认证状态
- `refreshUserInfo()` - 刷新用户信息
- `hasPermission(permission)` - 检查权限
- `hasRole(role)` - 检查角色

## API集成

### 认证API

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取当前用户信息

### 用户管理API

- `GET /api/users` - 获取用户列表
- `PUT /api/users/:id` - 更新用户信息

### 自动Token处理

- 请求拦截器自动添加Authorization头
- 响应拦截器自动处理401错误
- Token过期自动清除状态并跳转登录页

## 开发指南

### 添加新权限

1. 在 `authStore.ts` 的权限映射中添加新权限
2. 在需要的组件中使用 `hasPermission()` 检查
3. 在路由中使用 `ProtectedRoute` 组件保护

### 添加新角色

1. 在类型定义中添加新角色
2. 更新权限映射
3. 更新UI中的角色显示逻辑

### 添加新页面

1. 创建页面组件
2. 在路由中配置
3. 添加必要的权限检查
4. 更新导航菜单

## 环境配置

### 开发环境

创建 `.env.development` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 生产环境

创建 `.env.production` 文件：

```env
VITE_API_BASE_URL=https://your-api-domain.com/api
```

## 注意事项

1. **安全性**：Token存储在localStorage中，生产环境建议使用httpOnly cookie
2. **权限检查**：前端权限检查仅用于UI控制，后端必须进行权限验证
3. **错误处理**：所有API调用都有错误处理和用户友好的提示
4. **性能优化**：使用React Query进行数据缓存和状态管理

## 后续开发

- [ ] 完善文件库功能
- [ ] 实现任务管理功能
- [ ] 添加标注功能
- [ ] 实现复审功能
- [ ] 添加导出功能
- [ ] 优化移动端体验
- [ ] 添加国际化支持

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 