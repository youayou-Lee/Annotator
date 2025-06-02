# Document Annotation System
**版本**: 1.0.0
**生成时间**: 2025-06-02 15:55:41

## 描述
Document Annotation System based on FastAPI

## API 统计
- 总端点数: 45
- 方法分布:
  - DELETE: 4
  - GET: 23
  - POST: 14
  - PUT: 4

## API 端点详情
## Annotation

### POST /api/annotations/validate
**摘要**: 验证标注数据
**描述**: 验证标注数据是否符合模板定义
**标签**: Annotation

**请求体**:
- Content-Type: `application/json`
  Schema: `AnnotationValidationRequest`

**响应**:
- `200`: Successful Response
  返回类型: `AnnotationValidationResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### POST /api/annotations/validate-partial
**摘要**: 验证部分标注数据
**描述**: 验证部分标注数据（用于实时验证）
**标签**: Annotation

**请求体**:
- Content-Type: `application/json`
  Schema: `PartialValidationRequest`

**响应**:
- `200`: Successful Response
  返回类型: `PartialValidationResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/annotations/{task_id}/documents
**摘要**: 获取任务文档列表
**描述**: 获取任务包含的所有文档列表
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `status_filter` (query) -  - 可选
  按状态过滤

**响应**:
- `200`: Successful Response
  返回类型: `DocumentListResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/annotations/{task_id}/documents/{document_id}/annotation
**摘要**: 获取标注数据
**描述**: 获取标注数据
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
  返回类型: `Annotation` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### POST /api/annotations/{task_id}/documents/{document_id}/annotation
**摘要**: 保存标注数据
**描述**: 保存标注数据（支持自动保存和手动保存）
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**请求体**:
- Content-Type: `application/json`
  Schema: `AnnotationUpdate`

**响应**:
- `200`: Successful Response
  返回类型: `Annotation` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/annotations/{task_id}/documents/{document_id}/content
**摘要**: 获取文档内容
**描述**: 获取原始JSON文档内容
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
  返回类型: `DocumentContentResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/annotations/{task_id}/documents/{document_id}/form-config
**摘要**: 获取标注表单配置
**描述**: 根据模板动态生成表单字段配置
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
  返回类型: `FormConfigResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/annotations/{task_id}/documents/{document_id}/review
**摘要**: 获取复审数据
**描述**: 获取复审数据
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
  返回类型: `Annotation` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### POST /api/annotations/{task_id}/documents/{document_id}/review
**摘要**: 提交复审
**描述**: 提交复审
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**请求体**:
- Content-Type: `application/json`
  Schema: `AnnotationReview`

**响应**:
- `200`: Successful Response
  返回类型: `Annotation` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### POST /api/annotations/{task_id}/documents/{document_id}/submit
**摘要**: 提交文档标注
**描述**: 提交标注（标记文档为已完成状态）
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**请求体**:
- Content-Type: `application/json`
  Schema: `AnnotationSubmit`

**响应**:
- `200`: Successful Response
  返回类型: `Annotation` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/annotations/{task_id}/progress
**摘要**: 获取任务进度统计
**描述**: 获取整体任务进度和当前文档进度
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `current_document_id` (query) -  - 可选
  当前文档ID

**响应**:
- `200`: Successful Response
  返回类型: `TaskProgressResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### DELETE /api/annotations/{task_id}/{document_id}
**摘要**: 删除标注数据
**描述**: 删除标注数据
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/annotations/{task_id}/{document_id}
**摘要**: 获取标注数据
**描述**: 获取指定任务和文档的标注数据
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
  返回类型: `Annotation` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### POST /api/annotations/{task_id}/{document_id}
**摘要**: 保存标注数据
**描述**: 保存标注数据
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**请求体**:
- Content-Type: `application/json`

**响应**:
- `200`: Successful Response
  返回类型: `Annotation` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### PUT /api/annotations/{task_id}/{document_id}
**摘要**: 更新标注数据
**描述**: 更新标注数据
**标签**: Annotation

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需

**请求体**:
- Content-Type: `application/json`

**响应**:
- `200`: Successful Response
  返回类型: `Annotation` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

## Authentication

### POST /api/auth/change-password
**摘要**: 修改密码
**描述**: 修改当前用户密码

- **old_password**: 当前密码
- **new_password**: 新密码
**标签**: Authentication

**请求体**:
- Content-Type: `application/json`
  Schema: `ChangePasswordRequest`

**响应**:
- `200`: Successful Response
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### POST /api/auth/login
**摘要**: 用户登录
**描述**: 用户登录接口

- **username**: 用户名
- **password**: 密码

返回JWT访问令牌
**标签**: Authentication

**请求体**:
- Content-Type: `application/json`
  Schema: `LoginRequest`

**响应**:
- `200`: Successful Response
  返回类型: `Token` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/auth/me
**摘要**: 获取当前用户信息
**描述**: 获取当前登录用户的信息

需要有效的JWT令牌
**标签**: Authentication

**响应**:
- `200`: Successful Response
  返回类型: `User` (application/json)

--------------------------------------------------------------------------------

### POST /api/auth/refresh
**摘要**: 刷新访问令牌
**描述**: 刷新访问令牌

使用当前有效的令牌获取新的令牌
**标签**: Authentication

**响应**:
- `200`: Successful Response
  返回类型: `Token` (application/json)

--------------------------------------------------------------------------------

### POST /api/auth/register
**摘要**: 用户注册
**描述**: 用户注册接口

- **username**: 用户名（3-20个字符）
- **password**: 密码（至少6个字符）
- **role**: 用户角色（默认为annotator）

注意：只有管理员可以注册admin和super_admin角色的用户
**标签**: Authentication

**请求体**:
- Content-Type: `application/json`
  Schema: `RegisterRequest`

**响应**:
- `200`: Successful Response
  返回类型: `User` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

## File Management

### GET /api/files/
**摘要**: 获取文件列表
**描述**: 获取文件列表，支持按类型筛选
**标签**: File Management

**请求参数**:
- `file_type` (query) -  - 可选
  文件类型筛选

**响应**:
- `200`: Successful Response
  返回类型: `FileListResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/files/download/batch
**摘要**: 批量下载文件
**描述**: 批量下载文件（返回ZIP压缩包）
**标签**: File Management

**请求参数**:
- `file_ids` (query) - string - 必需
  文件ID列表，逗号分隔

**响应**:
- `200`: Successful Response
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/files/my-files
**摘要**: 获取我的文件
**描述**: 获取当前用户上传的文件
**标签**: File Management

**请求参数**:
- `file_type` (query) -  - 可选
  文件类型筛选

**响应**:
- `200`: Successful Response
  返回类型: `FileListResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### POST /api/files/upload
**摘要**: 上传文件
**描述**: 上传单个文件
**标签**: File Management

**请求体**:
- Content-Type: `multipart/form-data`
  Schema: `Body_upload_file_api_files_upload_post`

**响应**:
- `200`: Successful Response
  返回类型: `FileUpload` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### POST /api/files/upload/batch
**摘要**: 批量上传文件
**描述**: 批量上传文件
**标签**: File Management

**请求体**:
- Content-Type: `multipart/form-data`
  Schema: `Body_upload_files_batch_api_files_upload_batch_post`

**响应**:
- `200`: Successful Response
  返回类型: `BatchFileUpload` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### DELETE /api/files/{file_id}
**摘要**: 删除文件
**描述**: 删除文件
**标签**: File Management

**请求参数**:
- `file_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
  返回类型: `FileDeleteResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/files/{file_id}/download
**摘要**: 下载文件
**描述**: 下载文件
**标签**: File Management

**请求参数**:
- `file_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/files/{file_id}/preview
**摘要**: 预览文件
**描述**: 预览文件内容
**标签**: File Management

**请求参数**:
- `file_id` (path) - string - 必需
- `max_size` (query) - integer - 可选
  最大预览大小（字节）

**响应**:
- `200`: Successful Response
  返回类型: `FilePreview` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/files/{file_id}/validate
**摘要**: 验证模板文件
**描述**: 验证Python模板文件
**标签**: File Management

**请求参数**:
- `file_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
  返回类型: `TemplateValidationResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

## Task Management

### GET /api/tasks/
**摘要**: 获取任务列表
**描述**: 获取任务列表，支持筛选、分页和搜索
**标签**: Task Management

**请求参数**:
- `status` (query) -  - 可选
  任务状态筛选
- `assignee_id` (query) -  - 可选
  分配人ID筛选
- `creator_id` (query) -  - 可选
  创建人ID筛选
- `page` (query) - integer - 可选
  页码
- `page_size` (query) - integer - 可选
  每页数量
- `search` (query) -  - 可选
  搜索关键词

**响应**:
- `200`: Successful Response
  返回类型: `TaskListResponse` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### POST /api/tasks/
**摘要**: 创建任务
**描述**: 创建任务
**标签**: Task Management

**请求体**:
- Content-Type: `application/json`
  Schema: `TaskCreate`

**响应**:
- `200`: Successful Response
  返回类型: `Task` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/tasks/statistics
**摘要**: 获取任务统计
**描述**: 获取任务统计信息
**标签**: Task Management

**响应**:
- `200`: Successful Response
  返回类型: `TaskStatistics` (application/json)

--------------------------------------------------------------------------------

### DELETE /api/tasks/{task_id}
**摘要**: 删除任务
**描述**: 删除任务
**标签**: Task Management

**请求参数**:
- `task_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/tasks/{task_id}
**摘要**: 获取任务详情
**描述**: 获取任务详情
**标签**: Task Management

**请求参数**:
- `task_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
  返回类型: `Task` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### PUT /api/tasks/{task_id}
**摘要**: 更新任务
**描述**: 更新任务
**标签**: Task Management

**请求参数**:
- `task_id` (path) - string - 必需

**请求体**:
- Content-Type: `application/json`
  Schema: `TaskUpdate`

**响应**:
- `200`: Successful Response
  返回类型: `Task` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### PUT /api/tasks/{task_id}/documents/{document_id}/status
**摘要**: 更新文档状态
**描述**: 更新文档状态
**标签**: Task Management

**请求参数**:
- `task_id` (path) - string - 必需
- `document_id` (path) - string - 必需
- `status` (query) -  - 必需

**响应**:
- `200`: Successful Response
  返回类型: `Task` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### POST /api/tasks/{task_id}/export
**摘要**: 导出任务数据
**描述**: 导出任务数据
**标签**: Task Management

**请求参数**:
- `task_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/tasks/{task_id}/progress
**摘要**: 获取任务进度详情
**描述**: 获取任务进度详情
**标签**: Task Management

**请求参数**:
- `task_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/tasks/{task_id}/template/fields
**摘要**: 获取任务模板字段
**描述**: 获取任务模板字段信息
**标签**: Task Management

**请求参数**:
- `task_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

## User Management

### GET /api/users/
**摘要**: 获取用户列表
**描述**: 获取用户列表（需要管理员权限）
**标签**: User Management

**响应**:
- `200`: Successful Response

--------------------------------------------------------------------------------

### DELETE /api/users/{user_id}
**摘要**: 删除用户
**描述**: 删除用户（需要超级管理员权限）
**标签**: User Management

**请求参数**:
- `user_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### GET /api/users/{user_id}
**摘要**: 获取用户详情
**描述**: 获取用户详情
**标签**: User Management

**请求参数**:
- `user_id` (path) - string - 必需

**响应**:
- `200`: Successful Response
  返回类型: `User` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

### PUT /api/users/{user_id}
**摘要**: 更新用户信息
**描述**: 更新用户信息
**标签**: User Management

**请求参数**:
- `user_id` (path) - string - 必需

**请求体**:
- Content-Type: `application/json`
  Schema: `UserUpdate`

**响应**:
- `200`: Successful Response
  返回类型: `User` (application/json)
- `422`: Validation Error
  返回类型: `HTTPValidationError` (application/json)

--------------------------------------------------------------------------------

## 未分类

### GET /
**摘要**: Root Path
**描述**: Root path, returns system information

**响应**:
- `200`: Successful Response

--------------------------------------------------------------------------------

### GET /health
**摘要**: Health Check
**描述**: Health check endpoint

**响应**:
- `200`: Successful Response

--------------------------------------------------------------------------------
