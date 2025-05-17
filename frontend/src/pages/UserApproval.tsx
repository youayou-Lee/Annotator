import React, { useEffect, useState } from 'react';
import { Table, Badge, Button, Space, Card, message, Modal, Typography, Divider } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import api from '../services/api';

const { Title } = Typography;
const { confirm } = Modal;

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
}

const UserApproval: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [pendingAdmins, setPendingAdmins] = useState<User[]>([]);

  // 获取待审批的管理员列表
  const fetchPendingAdmins = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/auth/pending-admins');
      setPendingAdmins(data);
    } catch (error: any) {
      message.error('获取待审批管理员失败: ' + (error.response?.data?.detail || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  // 组件加载时获取数据
  useEffect(() => {
    fetchPendingAdmins();
  }, []);

  // 审批用户
  const handleApprove = (userId: number, status: 'approved' | 'rejected') => {
    confirm({
      title: `确认${status === 'approved' ? '批准' : '拒绝'}此用户?`,
      icon: <ExclamationCircleOutlined />,
      content: `您确定要${status === 'approved' ? '批准' : '拒绝'}此用户的管理员申请吗?`,
      onOk: async () => {
        try {
          await api.post('/auth/approve', {
            user_id: userId,
            status: status
          });
          message.success(`${status === 'approved' ? '批准' : '拒绝'}成功`);
          fetchPendingAdmins(); // 刷新列表
        } catch (error: any) {
          message.error(`操作失败: ${error.response?.data?.detail || '未知错误'}`);
        }
      }
    });
  };

  // 表格列定义
  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => (
        <Badge
          status="processing" 
          text={role === 'admin' ? '管理员' : role === 'superuser' ? '超级管理员' : '标注人员'}
        />
      )
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString()
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record: User) => (
        <Space size="middle">
          <Button
            type="primary"
            icon={<CheckCircleOutlined />}
            onClick={() => handleApprove(record.id, 'approved')}
          >
            批准
          </Button>
          <Button
            danger
            icon={<CloseCircleOutlined />}
            onClick={() => handleApprove(record.id, 'rejected')}
          >
            拒绝
          </Button>
        </Space>
      )
    },
  ];

  return (
    <Card>
      <Title level={2}>管理员审批</Title>
      <Divider />
      <Table
        dataSource={pendingAdmins}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
        locale={{ emptyText: '没有待审批的管理员请求' }}
      />
    </Card>
  );
};

export default UserApproval; 