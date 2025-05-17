import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message, Divider, Radio, Space } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

const { Title } = Typography;

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  role: 'admin' | 'annotator';
}

const Register: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: RegisterFormData) => {
    if (values.password !== values.confirmPassword) {
      message.error('两次输入的密码不一致');
      return;
    }

    setLoading(true);
    try {
      // 去除确认密码字段
      const { confirmPassword, ...submitData } = values;
      
      // 发送注册请求
      await api.post('/auth/register', submitData);
      
      // 根据角色显示不同的成功信息
      if (values.role === 'admin') {
        message.success('管理员注册申请已提交，等待超级管理员审批');
      } else {
        message.success('标注人员注册成功，可以直接登录');
      }
      
      // 跳转到登录页
      navigate('/login');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '注册失败，请稍后再试');
      console.error('Registration error:', error);
    } finally {
      setLoading(false);
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
          width: 450,
          borderRadius: 8,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>文档标注系统</Title>
          <Divider>用户注册</Divider>
        </div>
        <Form
          form={form}
          name="register"
          onFinish={onFinish}
          layout="vertical"
          initialValues={{ role: 'annotator' }}
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
              size="large"
            />
          </Form.Item>
          
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="邮箱"
              size="large"
            />
          </Form.Item>
          
          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              size="large"
            />
          </Form.Item>
          
          <Form.Item
            name="confirmPassword"
            rules={[
              { required: true, message: '请确认密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="确认密码"
              size="large"
            />
          </Form.Item>
          
          <Form.Item
            name="role"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Radio.Group>
              <Radio value="annotator">标注人员</Radio>
              <Radio value="admin">管理员</Radio>
            </Radio.Group>
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 12 }}>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
              loading={loading}
            >
              注册
            </Button>
          </Form.Item>
          
          <Space style={{ display: 'flex', justifyContent: 'center' }}>
            <span>已有账号?</span>
            <Link to="/login">立即登录</Link>
          </Space>
        </Form>
      </Card>
    </div>
  );
};

export default Register; 