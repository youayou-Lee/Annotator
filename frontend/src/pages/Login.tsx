import React from 'react';
import { Form, Input, Button, Card, Typography, message, Divider, Space } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

const { Title } = Typography;

interface LoginFormData {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

const Login: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const onFinish = async (values: LoginFormData) => {
    try {
      // 向后端发送登录请求
      console.log('Login form submitted:', values);
      
      // 将表单数据转换为FormData格式（OAuth2要求）
      const formData = new FormData();
      formData.append('username', values.username);
      formData.append('password', values.password);
      
      // 调用登录API - 由于api.ts中的拦截器，此处直接得到的是response.data
      const data = await api.post<LoginResponse>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      console.log('登录响应数据:', data);
      
      // 存储token
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      message.success('登录成功');
      
      // 使用location.href刷新页面，确保新token被应用
      window.location.href = '/';
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码');
      console.error('Login error:', error);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      background: '#f0f2f5',
    }}>
      <Card
        style={{
          width: 400,
          borderRadius: 8,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>Document Annotation System</Title>
          <Divider>User Login</Divider>
        </div>
        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          layout="vertical"
          initialValues={{ username: '', password: '' }}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Please input your username' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Username/Email"
              size="large"
            />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please input your password' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Password"
              size="large"
            />
          </Form.Item>
          <Form.Item style={{ marginBottom: 12 }}>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
            >
              Login
            </Button>
          </Form.Item>
          <Space style={{ display: 'flex', justifyContent: 'center' }}>
            <span>No account?</span>
            <Link to="/register">Register now</Link>
          </Space>
        </Form>
      </Card>
    </div>
  );
};

export default Login;