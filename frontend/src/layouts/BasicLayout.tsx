import React, { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Avatar, Dropdown, Button, theme } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UserOutlined,
  FileTextOutlined,
  TeamOutlined,
  BookOutlined,
  LogoutOutlined,
  FolderOpenOutlined,
  AuditOutlined,
} from '@ant-design/icons';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useUserInfo } from '../App';
import api from '../services/api';

const { Header, Sider, Content, Footer } = Layout;

const BasicLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { userInfo, loading } = useUserInfo();
  
  const { token } = theme.useToken();

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
    },
  ];

  // 基础菜单项
  const baseMenuItems = [
    {
      key: 'dashboard',
      icon: <BookOutlined />,
      label: '仪表盘',
      path: '/',
    },
    {
      key: 'tasks',
      icon: <BookOutlined />,
      label: '任务管理',
      path: '/tasks',
    },
    {
      key: 'public-files',
      icon: <FolderOpenOutlined />,
      label: '公共文件库',
      path: '/public-files',
    },
  ];

  // 管理员菜单项
  const adminMenuItems = [
    {
      key: 'users',
      icon: <TeamOutlined />,
      label: '用户管理',
      path: '/users',
      roles: ['admin', 'superuser'],
    },
  ];

  // 超级管理员菜单项
  const superuserMenuItems = [
    {
      key: 'admin-approval',
      icon: <AuditOutlined />,
      label: '管理员审批',
      path: '/admin-approval',
      roles: ['superuser'],
    },
  ];

  // 根据用户角色获取菜单项
  const getMenuItems = () => {
    let items = [...baseMenuItems];
    
    if (userInfo) {
      if (['admin', 'superuser'].includes(userInfo.role)) {
        items = [...items, ...adminMenuItems];
      }
      
      if (userInfo.role === 'superuser') {
        items = [...items, ...superuserMenuItems];
      }
    }
    
    return items;
  };

  const handleUserMenuClick = (key: string) => {
    if (key === 'profile') {
      navigate('/profile');
    } else if (key === 'logout') {
      // Logout logic
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      navigate('/login');
    }
  };

  if (loading) {
    return <div>加载中...</div>;
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        theme="light"
      >
        <div style={{ 
          height: 32, 
          margin: 16, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center'
        }}>
          <Typography.Title 
            level={4} 
            style={{ 
              margin: 0, 
              color: token.colorPrimary 
            }}
          >
            {collapsed ? '文档' : '文档标注系统'}
          </Typography.Title>
        </div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[location.pathname.split('/')[1] || 'dashboard']}
          items={getMenuItems().map(item => ({
            key: item.key,
            icon: item.icon,
            label: <Link to={item.path}>{item.label}</Link>,
          }))}
        />
      </Sider>
      <Layout>
        <Header style={{ 
          padding: 0, 
          background: 'white',
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between' 
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: 64, height: 64 }}
          />
          <div style={{ display: 'flex', marginRight: 20 }}>
            <Dropdown menu={{ 
              items: userMenuItems.map(item => ({
                key: item.key,
                icon: item.icon,
                label: item.label,
                onClick: () => handleUserMenuClick(item.key),
              }))
            }}>
              <div style={{ 
                cursor: 'pointer', 
                display: 'flex', 
                alignItems: 'center' 
              }}>
                <Avatar icon={<UserOutlined />} />
                <span style={{ marginLeft: 8 }}>
                  {userInfo ? userInfo.username : '用户'} 
                  {userInfo && userInfo.role === 'superuser' && '(超级管理员)'}
                  {userInfo && userInfo.role === 'admin' && '(管理员)'}
                </span>
              </div>
            </Dropdown>
          </div>
        </Header>
        <Content style={{ 
          margin: '24px 16px', 
          padding: 24, 
          minHeight: 280, 
          background: 'white',
          borderRadius: token.borderRadius,
        }}>
          <Outlet />
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          文档标注系统 ©{new Date().getFullYear()}
        </Footer>
      </Layout>
    </Layout>
  );
};

export default BasicLayout;