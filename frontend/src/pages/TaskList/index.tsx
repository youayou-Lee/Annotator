import React, { useState } from 'react'
import {
  Card,
  Typography,
  Space,
  Tag,
  Button,
  Row,
  Col,
  Input,
  Select,
  Statistic,
  Progress,
  Dropdown,
  Modal,
  message,
  Spin,
  Empty,
  Tooltip,
  Layout,
  App
} from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  CalendarOutlined,
  FileTextOutlined,
  MoreOutlined,
  EyeOutlined,
  TeamOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  PlayCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { taskAPI, userAPI } from '../../services/api'
import { useAuthStore } from '../../stores/authStore'
import type { Task, TaskFilters } from '../../types'
import TaskCreateModal from './components/TaskCreateModal'
import TaskEditModal from './components/TaskEditModal'

const { Title, Text } = Typography
const { Search } = Input
const { Option } = Select
const { Content } = Layout

const TaskList: React.FC = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, hasPermission } = useAuthStore()
  const { message } = App.useApp()
  
  // 状态管理
  const [filters, setFilters] = useState<TaskFilters>({})
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)

  // 获取任务列表
  const { data: tasksResponse, isLoading: tasksLoading, refetch: refetchTasks } = useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => taskAPI.getTasks(filters)
  })

  const tasks = Array.isArray(tasksResponse?.data) ? tasksResponse.data : []

  // 获取用户列表
  const { data: usersResponse } = useQuery({
    queryKey: ['users'],
    queryFn: () => userAPI.getUsers()
  })

  const users = Array.isArray(usersResponse?.data) ? usersResponse.data : []

  // 删除任务
  const deleteMutation = useMutation({
    mutationFn: taskAPI.deleteTask,
    onSuccess: () => {
      message.success('任务删除成功')
      refetchTasks()
    },
    onError: (error: any) => {
      message.error(error.message || '删除任务失败')
    }
  })

  // 获取用户名
  const getUserName = (userId: string) => {
    const user = users.find(u => u.id === userId)
    return user?.username || '未知用户'
  }

  // 获取状态配置
  const getStatusConfig = (status: string) => {
    const configs = {
      pending: { color: 'orange', text: '待开始', icon: <ClockCircleOutlined /> },
      in_progress: { color: 'blue', text: '进行中', icon: <PlayCircleOutlined /> },
      completed: { color: 'green', text: '已完成', icon: <CheckCircleOutlined /> }
    }
    return configs[status as keyof typeof configs] || configs.pending
  }

  // 计算任务统计
  const getTaskStats = () => {
    // 确保tasks是数组
    if (!Array.isArray(tasks)) {
      return {
        total: 0,
        pending: 0,
        in_progress: 0,
        completed: 0
      }
    }
    
    const stats = {
      total: tasks.length,
      pending: tasks.filter(t => t.status === 'pending').length,
      in_progress: tasks.filter(t => t.status === 'in_progress').length,
      completed: tasks.filter(t => t.status === 'completed').length
    }
    return stats
  }

  // 计算任务进度
  const getTaskProgress = (task: Task) => {
    if (!task.documents || task.documents.length === 0) return 0
    const completed = task.documents.filter(doc => doc.status === 'completed').length
    return Math.round((completed / task.documents.length) * 100)
  }

  // 处理搜索
  const handleSearch = (value: string) => {
    setFilters(prev => ({ ...prev, search: value || undefined }))
  }

  // 处理筛选
  const handleFilterChange = (key: keyof TaskFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value || undefined }))
  }

  // 处理任务操作
  const handleViewTask = (taskId: string) => {
    navigate(`/tasks/${taskId}`)
  }

  const handleEditTask = (task: Task) => {
    setSelectedTask(task)
    setEditModalVisible(true)
  }

  const handleDeleteTask = (taskId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个任务吗？此操作不可撤销。',
      icon: <ExclamationCircleOutlined />,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: () => deleteMutation.mutate(taskId)
    })
  }

  // 任务卡片操作菜单
  const getTaskActions = (task: Task) => {
    const canEdit = hasPermission('task.create') || user?.id === task.creator_id
    const canDelete = hasPermission('task.create') || user?.id === task.creator_id
    
    const items = [
      {
        key: 'view',
        label: '查看详情',
        icon: <EyeOutlined />,
        onClick: () => handleViewTask(task.id)
      }
    ]

    if (canEdit) {
      items.push({
        key: 'edit',
        label: '编辑任务',
        icon: <EditOutlined />,
        onClick: () => handleEditTask(task)
      })
    }

    if (canDelete) {
      items.push({
        key: 'delete',
        label: '删除任务',
        icon: <DeleteOutlined />,
        onClick: () => handleDeleteTask(task.id)
      } as any)
    }

    return items
  }

  const stats = getTaskStats()

  return (
    <div style={{ padding: '24px' }}>
      {/* 页面标题和操作 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>任务管理</Title>
        </Col>
        <Col>
          {hasPermission('task.create') && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              创建任务
            </Button>
          )}
        </Col>
      </Row>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={stats.total}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待开始"
              value={stats.pending}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="进行中"
              value={stats.in_progress}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completed}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 搜索和筛选 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Search
              placeholder="搜索任务名称或描述"
              allowClear
              onSearch={handleSearch}
              style={{ width: '100%' }}
              prefix={<SearchOutlined />}
            />
          </Col>
          <Col>
            <Select
              placeholder="状态筛选"
              allowClear
              style={{ width: 120 }}
              onChange={(value) => handleFilterChange('status', value)}
            >
              <Option value="pending">待开始</Option>
              <Option value="in_progress">进行中</Option>
              <Option value="completed">已完成</Option>
            </Select>
          </Col>
          <Col>
            <Select
              placeholder="负责人筛选"
              allowClear
              style={{ width: 150 }}
              onChange={(value) => handleFilterChange('assignee_id', value)}
              showSearch
              filterOption={(input, option) =>
                String(option?.children || '').toLowerCase().includes(input.toLowerCase())
              }
            >
              {users.map(user => (
                <Option key={user.id} value={user.id}>
                  {user.username}
                </Option>
              ))}
            </Select>
          </Col>
          <Col>
            <Select
              placeholder="创建人筛选"
              allowClear
              style={{ width: 150 }}
              onChange={(value) => handleFilterChange('creator_id', value)}
              showSearch
              filterOption={(input, option) =>
                String(option?.children || '').toLowerCase().includes(input.toLowerCase())
              }
            >
              {users.map(user => (
                <Option key={user.id} value={user.id}>
                  {user.username}
                </Option>
              ))}
            </Select>
          </Col>
        </Row>
      </Card>

      {/* 任务列表 */}
      <Spin spinning={tasksLoading}>
        {tasks.length === 0 ? (
          <Card>
            <Empty
              description="暂无任务"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              {hasPermission('task.create') && (
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setCreateModalVisible(true)}
                >
                  创建第一个任务
                </Button>
              )}
            </Empty>
          </Card>
        ) : (
          <Row gutter={[16, 16]}>
            {tasks.map(task => {
              const statusConfig = getStatusConfig(task.status)
              const progress = getTaskProgress(task)
              
              return (
                <Col key={task.id} xs={24} sm={12} lg={8} xl={6}>
                  <Card
                    hoverable
                    actions={[
                      <Tooltip title="查看详情">
                        <EyeOutlined onClick={() => handleViewTask(task.id)} />
                      </Tooltip>,
                      <Dropdown
                        menu={{ items: getTaskActions(task) }}
                        trigger={['click']}
                      >
                        <MoreOutlined />
                      </Dropdown>
                    ]}
                  >
                    <Card.Meta
                      title={
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Text strong ellipsis style={{ flex: 1 }}>
                              {task.name}
                            </Text>
                            <Tag color={statusConfig.color} icon={statusConfig.icon}>
                              {statusConfig.text}
                            </Tag>
                          </div>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <Text type="secondary" ellipsis>
                            {task.description}
                          </Text>
                          
                          <div>
                            <Text type="secondary">进度：</Text>
                            <Progress
                              percent={progress}
                              size="small"
                              status={progress === 100 ? 'success' : 'active'}
                            />
                          </div>

                          <Space size="small">
                            <UserOutlined />
                            <Text type="secondary">
                              负责人: {task.assignee_id ? getUserName(task.assignee_id) : '未分配'}
                            </Text>
                          </Space>

                          <Space size="small">
                            <TeamOutlined />
                            <Text type="secondary">
                              创建人: {getUserName(task.creator_id)}
                            </Text>
                          </Space>

                          <Space size="small">
                            <FileTextOutlined />
                            <Text type="secondary">
                              文档: {task.documents?.length || 0} 个
                            </Text>
                          </Space>

                          <Space size="small">
                            <CalendarOutlined />
                            <Text type="secondary">
                              创建: {new Date(task.created_at).toLocaleDateString()}
                            </Text>
                          </Space>

                          {task.deadline && (
                            <Space size="small">
                              <ClockCircleOutlined />
                              <Text type="secondary">
                                截止: {new Date(task.deadline).toLocaleDateString()}
                              </Text>
                            </Space>
                          )}
                        </Space>
                      }
                    />
                  </Card>
                </Col>
              )
            })}
          </Row>
        )}
      </Spin>

      {/* 创建任务模态框 */}
      <TaskCreateModal
        visible={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        onSuccess={() => {
          setCreateModalVisible(false)
          refetchTasks()
        }}
      />

      {/* 编辑任务模态框 */}
      <TaskEditModal
        visible={editModalVisible}
        task={selectedTask}
        onCancel={() => {
          setEditModalVisible(false)
          setSelectedTask(null)
        }}
        onSuccess={() => {
          setEditModalVisible(false)
          setSelectedTask(null)
          refetchTasks()
        }}
      />
    </div>
  )
}

export default TaskList 