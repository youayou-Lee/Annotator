# 文书标注系统测试文档

## 测试架构概述

本项目使用 Vitest 作为测试框架，结合 React Testing Library 进行 React 组件测试。测试涵盖了单元测试和组件测试，未来将添加端到端测试。

## 测试脚本

在 `package.json` 中定义的测试相关脚本：

```json
"scripts": {
  "test": "vitest run",         // 运行所有测试（一次性运行）
  "test:watch": "vitest"        // 运行所有测试（观察模式）
}
```

运行特定测试文件的方法：

```bash
npm test -- <测试文件名>        # 例如: npm test -- FileUpload.test.tsx
```

## 测试配置

位于 `vitest.config.ts` 的测试配置：

```typescript
test: {
  globals: true,                // 全局可用测试函数（无需导入）
  environment: 'jsdom',         // 使用 jsdom 环境模拟浏览器
  setupFiles: ['./src/setupTests.ts'], // 测试前运行的设置文件
  include: ['./src/**/*.test.{ts,tsx}'], // 包含的测试文件
  exclude: ['./src/**/*.e2e.test.{ts,tsx}'], // 排除的测试文件（端到端测试）
  coverage: {
    reporter: ['text', 'html'], // 覆盖率报告格式
    exclude: [
      'node_modules/',
      'src/setupTests.ts',
    ],
  },
}
```

## 测试文件概述

项目中的测试文件及其功能：

### 组件测试

1. **FileUpload.test.tsx**
   - 位置：`src/__tests__/FileUpload.test.tsx`
   - 功能：测试文件上传组件
   - 测试用例：
     - 组件渲染测试
     - 文件格式验证测试
     - 文件上传成功处理测试
     - 上传错误处理测试
     - 验证错误展示测试
   - 状态：✅ 通过

2. **TaskDetail.test.tsx**
   - 位置：`src/__tests__/TaskDetail.test.tsx`
   - 功能：测试任务详情页面组件
   - 测试用例：
     - 渲染任务详情页面
     - 切换到文档列表标签页
     - 切换到历史记录标签页
     - 切换到讨论标签页并添加评论
     - 尝试删除任务
     - 返回任务列表
   - 状态：❌ 失败
   - 失败原因：react-router-dom的useNavigate模拟有问题

3. **TaskManagement.test.tsx**
   - 位置：`src/__tests__/TaskManagement.test.tsx`
   - 功能：测试任务管理页面组件
   - 测试用例：
     - 渲染任务管理页面
     - 通过文本搜索过滤任务
     - 通过状态筛选任务
     - 通过优先级筛选任务
     - 打开创建任务模态框
     - 提交创建任务表单
   - 状态：❌ 失败
   - 失败原因：元素选择器匹配问题和文本重复问题

4. **DocumentUpload.test.tsx**
   - 位置：`src/__tests__/DocumentUpload.test.tsx`
   - 功能：测试文档上传页面
   - 测试用例：
     - 渲染文档上传页面
     - 成功上传后显示成功提示
   - 状态：未确认

5. **Dashboard.test.tsx**
   - 位置：`src/__tests__/Dashboard.test.tsx`
   - 功能：测试仪表盘页面
   - 测试用例：（待补充）
   - 状态：未确认

### 端到端测试

1. **FileUpload.e2e.test.ts**
   - 位置：`src/__tests__/FileUpload.e2e.test.ts`
   - 功能：测试文件上传的端到端流程
   - 测试用例：
     - 上传有效文件并验证成功
     - 上传无效文件并验证失败
     - 尝试上传不支持的文件格式
     - 测试文件格式选择功能
   - 状态：未运行
   - 原因：需要额外配置和运行环境

## 测试工具函数

1. **generateMockFiles.ts**
   - 位置：`src/__tests__/generateMockFiles.ts`
   - 功能：生成各种模拟文件用于测试
   - 生成的文件类型：
     - JSON文件
     - CSV文件
     - XLSX文件
     - 普通文本文件（用于测试不支持的格式）

## 测试设置文件

**setupTests.ts**
- 位置：`src/setupTests.ts`
- 功能：
  - 导入测试库
  - 模拟localStorage
  - 模拟matchMedia
  - 模拟IntersectionObserver

## 测试模式和策略

1. **组件单元测试**
   - 使用React Testing Library进行渲染和交互
   - 使用vitest的vi.mock()模拟依赖
   - 关注组件的行为而不是实现细节

2. **API模拟策略**
   - 使用vi.mock()模拟API服务
   - 针对不同测试场景返回不同的模拟数据

3. **路由测试策略**
   - 使用MemoryRouter包装组件
   - 模拟useNavigate和useParams钩子

## 常见测试问题和解决方案

1. **文本选择器问题**
   - 问题：使用getByText等选择器找不到元素或找到多个匹配元素
   - 解决方案：使用更精确的选择器，如testId，或使用正则表达式匹配

2. **路由钩子模拟问题**
   - 问题：vi.mocked(require('react-router-dom')).useNavigate.mockReturnValue不工作
   - 解决方案：直接在模拟模块中提供函数实现

3. **异步测试问题**
   - 问题：测试中的异步行为导致测试提前完成
   - 解决方案：正确使用waitFor和async/await

## 改进测试的建议

1. 添加更多的测试ID到组件，减少对文本内容的依赖
2. 改进模拟策略，特别是对外部库的模拟
3. 增加测试覆盖率，添加更多边缘情况测试
4. 为端到端测试添加专门的环境配置 