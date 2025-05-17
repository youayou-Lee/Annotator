import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import BasicLayout from './layouts/BasicLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import UserApproval from './pages/UserApproval';
import TaskManagement from './pages/TaskManagement';
import Dashboard from './pages/Dashboard';
import TaskDetail from './pages/TaskDetail';
import PublicFiles from './pages/PublicFiles';
import api from './services/api';

// 用户角色类型
type UserRole = 'superuser' | 'admin' | 'annotator';

// 用户信息接口
interface UserInfo {
  id: number;
  username: string;
  email: string;
  role: UserRole;
}

// 全局用户信息状态
export const useUserInfo = () => {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  // 获取当前登录用户信息
  const fetchUserInfo = async () => {
    setLoading(true);
    try {
      console.log('正在获取用户信息，当前token:', localStorage.getItem('token'));
      const response = await api.get('/auth/me');
      console.log('获取用户信息成功:', response);
      setUserInfo(response);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      setUserInfo(null);
      
      // 清除无效的token
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      console.log('检测到token，开始获取用户信息');
      fetchUserInfo();
    } else {
      console.log('未检测到token，用户未登录状态');
      setLoading(false);
    }
  }, []);

  return { userInfo, loading, fetchUserInfo };
};

// 路由守卫
const PrivateRoute = ({ children, requiredRoles = [] }: { 
  children: React.ReactNode, 
  requiredRoles?: UserRole[] 
}) => {
  const token = localStorage.getItem('token');
  const { userInfo, loading } = useUserInfo();

  if (loading) {
    return <div>加载中...</div>;
  }

  if (!token) {
    console.log('未检测到token，重定向到登录页面');
    return <Navigate to="/login" />;
  }

  if (requiredRoles.length > 0 && userInfo && !requiredRoles.includes(userInfo.role)) {
    console.log('用户角色不符合要求，重定向到首页');
    return <Navigate to="/" />;
  }

  console.log('验证通过，显示受保护的内容');
  return <>{children}</>;
};

const App: React.FC = () => {
  const isDarkMode = false;

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
      }}
    >
      <AntdApp>
        <BrowserRouter
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true
          }}
        >
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <BasicLayout />
                </PrivateRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="documents" element={<Navigate to="/public-files" replace />} />
              <Route path="tasks" element={<TaskManagement />} />
              <Route path="tasks/:id" element={<TaskDetail />} />
              <Route path="public-files" element={<PublicFiles />} />
              <Route path="users" element={<div>User Management</div>} />
              <Route 
                path="admin-approval" 
                element={
                  <PrivateRoute requiredRoles={['superuser']}>
                    <UserApproval />
                  </PrivateRoute>
                } 
              />
            </Route>
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </BrowserRouter>
      </AntdApp>
    </ConfigProvider>
  );
};

export default App;