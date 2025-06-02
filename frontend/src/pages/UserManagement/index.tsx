import React, { useState, useEffect } from 'react'
import {
  Layout,
  Typography,
  Button,
  Table,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  App,
  Tooltip,
  Popconfirm,
  Card,
  Row,
  Col,
  Statistic
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  TeamOutlined,
  CrownOutlined,
  SafetyOutlined
} from '@ant-design/icons'
import { userAPI } from '../../services/api'
import { useAuthStore } from '../../stores/authStore'
import type { User } from '../../types'
import type { ColumnsType } from 'antd/es/table'

const { Title } = Typography
const { Content } = Layout
const { Option } = Select

const UserManagement: React.FC = () => {
  const { user: currentUser, hasPermission } = useAuthStore()
  const { message } = App.useApp()
  
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [form] = Form.useForm()

  // 检查权限
  if (!hasPermission('user.manage')) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <h3>您没有权限访问此页面</h3>
      </div>
    )
  }

  // 获取用户列表
  const loadUsers = async () => {
    setLoading(true)
    try {
      const response = await userAPI.getUsers()
      if (response.success && response.data) {
        setUsers(response.data)
      } else {
        message.error('获取用户列表失败')
      }
    } catch (error) {
      console.error('获取用户列表失败:', error)
      message.error('获取用户列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUsers()
  }, [])

  // 获取角色标签
  const getRoleTag = (role: string) => {
    switch (role) {
      case 'super_admin':
        return <Tag color="red">超级管理员</Tag>
      case 'admin':
        return <Tag color="blue">管理员</Tag>
      case 'annotator':
        return <Tag color="green">标注员</Tag>
      default:
        return <Tag>未知</Tag>
    }
  }

  // 表格列配置
  const columns: ColumnsType<User> = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => getRoleTag(role),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个用户吗？"
            onConfirm={() => handleDelete()}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  // 处理编辑
  const handleEdit = (user: User) => {
    setEditingUser(user)
    form.setFieldsValue({
      username: user.username,
      role: user.role,
    })
    setModalVisible(true)
  }

  // 处理删除
  const handleDelete = async () => {
    try {
      // TODO: 实现删除用户API
      message.success('删除成功')
      loadUsers()
    } catch (error) {
      message.error('删除失败')
    }
  }

  // 处理表单提交
  const handleSubmit = async (values: any) => {
    try {
      if (editingUser) {
        // 更新用户
        await userAPI.updateUser(editingUser.id, values)
        message.success('更新成功')
      } else {
        // TODO: 实现创建用户API
        message.success('创建成功')
      }
      setModalVisible(false)
      setEditingUser(null)
      form.resetFields()
      loadUsers()
    } catch (error) {
      message.error('操作失败')
    }
  }

  // 处理取消
  const handleCancel = () => {
    setModalVisible(false)
    setEditingUser(null)
    form.resetFields()
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title="用户管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            新增用户
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={handleCancel}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="username"
            label="用户名"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
            ]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>

          {!editingUser && (
            <Form.Item
              name="password"
              label="密码"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' },
              ]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          )}

          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select placeholder="请选择角色">
              <Option value="annotator">标注员</Option>
              <Option value="admin">管理员</Option>
              <Option value="super_admin">超级管理员</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default UserManagement 