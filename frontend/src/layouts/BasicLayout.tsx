import React, { useState } from 'react';
import { Layout, Menu, Typography, Avatar, Dropdown, Button, theme } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UserOutlined,
  FileTextOutlined,
  TeamOutlined,
  BookOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';

const { Header, Sider, Content, Footer } = Layout;

const BasicLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  const { token } = theme.useToken();

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
    },
  ];

  const menuItems = [
    {
      key: 'dashboard',
      icon: <BookOutlined />,
      label: 'Dashboard',
      path: '/',
    },
    {
      key: 'documents',
      icon: <FileTextOutlined />,
      label: 'Documents',
      path: '/documents',
    },
    {
      key: 'tasks',
      icon: <BookOutlined />,
      label: 'Tasks',
      path: '/tasks',
    },
    {
      key: 'users',
      icon: <TeamOutlined />,
      label: 'Users',
      path: '/users',
    },
  ];

  const handleUserMenuClick = (key: string) => {
    if (key === 'profile') {
      navigate('/profile');
    } else if (key === 'logout') {
      // Logout logic
      localStorage.removeItem('token');
      navigate('/login');
    }
  };

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
            {collapsed ? 'DAS' : 'Doc Annotation'}
          </Typography.Title>
        </div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[location.pathname.split('/')[1] || 'dashboard']}
          items={menuItems.map(item => ({
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
                <span style={{ marginLeft: 8 }}>Admin</span>
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
          Document Annotation System ©{new Date().getFullYear()}
        </Footer>
      </Layout>
    </Layout>
  );
};

export default BasicLayout;