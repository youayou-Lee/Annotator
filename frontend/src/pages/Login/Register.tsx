import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  Form,
  Input,
  Button,
  Card,
  Typography,
  message,
  Select,
  Space,
} from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useAuthStore } from '../../stores/authStore'
import { authAPI } from '../../services/api'
import type { RegisterRequest } from '../../types'
import './index.css'

const { Title, Text } = Typography
const { Option } = Select

const Register: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleRegister = async (values: RegisterRequest) => {
    setLoading(true)
    try {
      const response = await authAPI.register(values)
      if (response.success && response.data) {
        login(response.data.user, response.data.token)
        message.success('注册成功，欢迎使用文书标注系统！')
        navigate('/tasks')
      } else {
        message.error(response.message || '注册失败')
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '注册失败，请检查网络连接'
      message.error(errorMessage)
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
              注册账户
            </Title>
            <Text type="secondary">
              创建您的账户以开始使用文书标注系统
            </Text>
          </div>

          <Form
            form={form}
            name="register"
            onFinish={handleRegister}
            autoComplete="off"
            size="large"
            layout="vertical"
          >
            <Form.Item
              name="username"
              label="用户名"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' },
                { max: 20, message: '用户名最多20个字符' },
                { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="请输入用户名"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="密码"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' },
                { max: 50, message: '密码最多50个字符' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="请输入密码"
              />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              label="确认密码"
              dependencies={['password']}
              rules={[
                { required: true, message: '请确认密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve()
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'))
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="请再次输入密码"
              />
            </Form.Item>

            <Form.Item
              name="role"
              label="角色"
              rules={[{ required: true, message: '请选择角色' }]}
              initialValue="annotator"
            >
              <Select placeholder="请选择角色">
                <Option value="annotator">标注员</Option>
                <Option value="admin">管理员</Option>
              </Select>
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
              >
                注册
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center', marginTop: '16px' }}>
            <Space>
              <Text type="secondary">已有账户？</Text>
              <Link to="/login">
                <Button type="link" style={{ padding: 0 }}>
                  立即登录
                </Button>
              </Link>
            </Space>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Register 