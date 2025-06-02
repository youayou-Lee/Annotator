import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  Form,
  Input,
  Button,
  Card,
  Typography,
  message,
  Space,
  Divider,
  Checkbox,
  Tabs,
  App,
} from 'antd'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import { useAuthStore } from '../../stores/authStore'
import { authAPI } from '../../services/api'
import type { LoginRequest } from '../../types'
import './index.css'
import Register from './Register'

const { Title, Text } = Typography

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const { message } = App.useApp()

  const handleLogin = async (values: LoginRequest & { remember?: boolean }) => {
    setLoading(true)
    try {
      const { remember, ...loginData } = values
      const response = await authAPI.login(loginData)
      if (response.success && response.data) {
        login(response.data.user, response.data.token)
        message.success('登录成功')
        navigate('/tasks')
      } else {
        message.error(response.message || '登录失败')
      }
    } catch (error: any) {
      message.error(error.response?.data?.message || '登录失败，请检查网络连接')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-content">
        <Card className="login-card">
          <div className="login-header">
            <Title level={2} className="login-title">
              文书标注系统
            </Title>
            <Text type="secondary">
              请登录您的账户以继续使用系统
            </Text>
          </div>

          <Form
            form={form}
            name="login"
            onFinish={handleLogin}
            autoComplete="off"
            size="large"
            initialValues={{ remember: true }}
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="用户名"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
              />
            </Form.Item>

            <Form.Item>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Form.Item name="remember" valuePropName="checked" noStyle>
                  <Checkbox>记住登录状态</Checkbox>
                </Form.Item>
              </div>
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
              >
                登录
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center', marginBottom: '16px' }}>
            <Space>
              <Text type="secondary">还没有账户？</Text>
              <Link to="/register">
                <Button type="link" style={{ padding: 0 }}>
                  立即注册
                </Button>
              </Link>
            </Space>
          </div>

          <Divider>
            <Text type="secondary">演示账户</Text>
          </Divider>

          <Space direction="vertical" style={{ width: '100%' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              管理员: admin / admin123
            </Text>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              标注员: annotator / 123456
            </Text>
          </Space>
        </Card>
      </div>
    </div>
  )
}

export default Login 