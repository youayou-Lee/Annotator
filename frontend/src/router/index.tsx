import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import Layout from '../components/Layout'
import Login from '../pages/Login'
import Register from '../pages/Login/Register'
import FileLibrary from '../pages/FileLibrary'
import TaskList from '../pages/TaskList'
import TaskDetail from '../pages/TaskDetail'
import Annotation from '../pages/Annotation'
import Review from '../pages/Review'
import UserManagement from '../pages/UserManagement'

// 路由守卫组件
const ProtectedRoute = ({ 
  children, 
  requiredPermissions = [],
  requiredRoles = []
}: { 
  children: React.ReactNode
  requiredPermissions?: string[]
  requiredRoles?: string[]
}) => {
  const { isAuthenticated, hasPermission, hasRole } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // 检查权限
  if (requiredPermissions.length > 0) {
    const hasRequiredPermission = requiredPermissions.some(permission => hasPermission(permission))
    if (!hasRequiredPermission) {
      return <Navigate to="/tasks" replace />
    }
  }

  // 检查角色
  if (requiredRoles.length > 0) {
    const hasRequiredRole = hasRole(requiredRoles)
    if (!hasRequiredRole) {
      return <Navigate to="/tasks" replace />
    }
  }
  
  return <>{children}</>
}

// 公共路由组件（已登录用户不能访问）
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (isAuthenticated) {
    return <Navigate to="/tasks" replace />
  }
  
  return <>{children}</>
}

const AppRouter = () => {
  return (
    <Routes>
      {/* 公共路由 */}
      <Route 
        path="/login" 
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        } 
      />
      
      <Route 
        path="/register" 
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        } 
      />
      
      {/* 受保护的路由 */}
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* 默认重定向到任务列表 */}
        <Route index element={<Navigate to="/tasks" replace />} />
        
        {/* 文件库 - 所有登录用户都可以访问 */}
        <Route path="files" element={<FileLibrary />} />
        
        {/* 任务管理 - 所有登录用户都可以访问 */}
        <Route path="tasks" element={<TaskList />} />
        <Route path="tasks/:taskId" element={<TaskDetail />} />
        
        {/* 用户管理 - 需要用户管理权限 */}
        <Route 
          path="users" 
          element={
            <ProtectedRoute requiredPermissions={['user.manage']}>
              <UserManagement />
            </ProtectedRoute>
          } 
        />
      </Route>
      
      {/* 标注页面 - 需要标注权限 */}
      <Route 
        path="/tasks/:taskId/documents/:documentId/annotation" 
        element={
          <ProtectedRoute requiredPermissions={['task.annotate']}>
            <Annotation />
          </ProtectedRoute>
        } 
      />
      
      {/* 复审页面 - 需要复审权限 */}
      <Route 
        path="/tasks/:taskId/documents/:documentId/review" 
        element={
          <ProtectedRoute requiredPermissions={['task.review']}>
            <Review />
          </ProtectedRoute>
        } 
      />
      
      {/* 404页面 */}
      <Route path="*" element={<Navigate to="/tasks" replace />} />
    </Routes>
  )
}

export default AppRouter 