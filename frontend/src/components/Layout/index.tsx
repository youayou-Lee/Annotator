import React, { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  Layout as AntLayout,
  Menu,
  Avatar,
  Dropdown,
  Button,
  Space,
  Typography,
  theme,
  Tag,
  message,
} from 'antd'
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  FileTextOutlined,
  FolderOpenOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  TeamOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../../stores/authStore'
import type { MenuProps } from 'antd'

const { Header, Sider, Content } = AntLayout
const { Text } = Typography

const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout, hasPermission } = useAuthStore()
  const {
    token: { colorBgContainer },
  } = theme.useToken()

  // 根据权限动态生成菜单项
  const getMenuItems = (): MenuProps['items'] => {
    const items: MenuProps['items'] = [
      {
        key: '/tasks',
        icon: <FileTextOutlined />,
        label: '任务管理',
      },
      {
        key: '/files',
        icon: <FolderOpenOutlined />,
        label: '文件库',
      },
    ]

    // 如果有用户管理权限，添加用户管理菜单
    if (hasPermission('user.manage')) {
      items.push({
        key: '/users',
        icon: <TeamOutlined />,
        label: '用户管理',
      })
    }

    return items
  }

  // 用户下拉菜单
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ]

  // 处理菜单点击
  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  // 处理用户菜单点击
  const handleUserMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'logout':
        logout()
        message.success('已退出登录')
        navigate('/login')
        break
      case 'profile':
        message.info('个人信息功能开发中...')
        break
      case 'settings':
        message.info('设置功能开发中...')
        break
    }
  }

  // 获取角色显示文本和颜色
  const getRoleInfo = (role: string) => {
    switch (role) {
      case 'super_admin':
        return { text: '超级管理员', color: 'red' }
      case 'admin':
        return { text: '管理员', color: 'blue' }
      case 'annotator':
        return { text: '标注员', color: 'green' }
      default:
        return { text: '未知', color: 'default' }
    }
  }

  // 获取当前选中的菜单项
  const selectedKeys = [location.pathname]
  const roleInfo = user ? getRoleInfo(user.role) : { text: '未知', color: 'default' }

  return (
    <AntLayout style={{ height: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: 18,
          fontWeight: 'bold',
        }}>
          {collapsed ? '标注' : '文书标注系统'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={selectedKeys}
          items={getMenuItems()}
          onClick={handleMenuClick}
        />
      </Sider>
      
      <AntLayout style={{ marginLeft: collapsed ? 80 : 200, transition: 'margin-left 0.2s' }}>
        <Header style={{ 
          padding: '0 24px', 
          background: colorBgContainer,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #f0f0f0',
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{
              fontSize: '16px',
              width: 64,
              height: 64,
            }}
          />
          
          <Space>
            <Space direction="vertical" size={0} style={{ textAlign: 'right' }}>
              <Text>欢迎，{user?.username}</Text>
              <Tag color={roleInfo.color}>
                {roleInfo.text}
              </Tag>
            </Space>
            <Dropdown
              menu={{
                items: userMenuItems,
                onClick: handleUserMenuClick,
              }}
              placement="bottomRight"
            >
              <Avatar 
                style={{ backgroundColor: '#1890ff', cursor: 'pointer' }}
                icon={<UserOutlined />}
              />
            </Dropdown>
          </Space>
        </Header>
        
        <Content
          style={{
            margin: 0,
            padding: 0,
            minHeight: 280,
            background: '#f5f5f5',
            overflow: 'auto',
          }}
        >
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  )
}

export default Layout 