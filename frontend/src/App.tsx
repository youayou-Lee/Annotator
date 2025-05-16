import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import BasicLayout from './layouts/BasicLayout';
import Login from './pages/Login';
import TaskManagement from './pages/TaskManagement';
import Dashboard from './pages/Dashboard';
import TaskDetail from './pages/TaskDetail';
import PublicFiles from './pages/PublicFiles';

// 路由守卫
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token');
  return token ? <>{children}</> : <Navigate to="/login" />;
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
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
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
            </Route>
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </BrowserRouter>
      </AntdApp>
    </ConfigProvider>
  );
};

export default App;