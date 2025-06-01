import React, { useState } from 'react'
import {
  Card,
  Typography,
  Button,
  Space,
  Table,
  Tag,
  Progress,
  Row,
  Col,
  Statistic,
  Modal,
  message,
  Spin,
  Alert,
  Descriptions,
  Avatar,
  Divider
} from 'antd'
import {
  PlayCircleOutlined,
  EditOutlined,
  FileTextOutlined,
  UserOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  EyeOutlined,
  ArrowLeftOutlined,
  ExportOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { taskAPI, userAPI, exportAPI } from '../../services/api'
import { TaskDocument, ExportRequest } from '../../types'
import { useAuthStore } from '../../stores/authStore'
import type { TableColumnsType } from 'antd'

const { Title, Text, Paragraph } = Typography

const TaskDetail: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [exportModalVisible, setExportModalVisible] = useState(false)

  // 获取任务详情
  const { data: taskResponse, isLoading: taskLoading, error: taskError } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => taskAPI.getTask(taskId!),
    enabled: !!taskId
  })

  const task = taskResponse?.data

  // 获取用户列表
  const { data: usersResponse } = useQuery({
    queryKey: ['users'],
    queryFn: () => userAPI.getUsers()
  })

  const users = usersResponse?.data || []

  // 导出任务
  const exportMutation = useMutation({
    mutationFn: exportAPI.exportTask,
    onSuccess: (response) => {
      message.success('导出任务已创建，请稍后下载')
      setExportModalVisible(false)
      // 可以在这里处理下载逻辑
      if (response.data?.download_url) {
        window.open(response.data.download_url, '_blank')
      }
    },
    onError: () => {
      message.error('导出失败')
    }
  })

  // 获取用户名
  const getUserName = (userId: string) => {
    const user = users.find(u => u.id === userId)
    return user?.username || userId
  }

  // 获取用户角色
  const getUserRole = (userId: string) => {
    const user = users.find(u => u.id === userId)
    return user?.role || ''
  }

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusMap = {
      pending: { color: 'orange', text: '待开始', icon: <ClockCircleOutlined /> },
      in_progress: { color: 'blue', text: '进行中', icon: <PlayCircleOutlined /> },
      completed: { color: 'green', text: '已完成', icon: <CheckCircleOutlined /> }
    }
    const config = statusMap[status as keyof typeof statusMap] || { 
      color: 'default', 
      text: status, 
      icon: <ClockCircleOutlined /> 
    }
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    )
  }

  // 获取文档状态标签
  const getDocumentStatusTag = (status: string) => {
    const statusMap = {
      pending: { color: 'orange', text: '待标注' },
      completed: { color: 'green', text: '已完成' }
    }
    const config = statusMap[status as keyof typeof statusMap] || { color: 'default', text: status }
    return <Tag color={config.color}>{config.text}</Tag>
  }

  // 计算任务进度
  const getTaskProgress = () => {
    if (!task?.documents) return 0
    const completedDocs = task.documents.filter(doc => doc.status === 'completed').length
    const totalDocs = task.documents.length
    return totalDocs > 0 ? Math.round((completedDocs / totalDocs) * 100) : 0
  }

  // 开始标注
  const handleStartAnnotation = (documentId: string) => {
    navigate(`/tasks/${taskId}/documents/${documentId}/annotation`)
  }

  // 查看标注结果
  const handleViewAnnotation = (documentId: string) => {
    navigate(`/tasks/${taskId}/documents/${documentId}/review`)
  }

  // 导出任务数据
  const handleExport = (format: 'json' | 'csv' | 'excel') => {
    if (!taskId) return
    
    const exportData: ExportRequest = {
      task_id: taskId,
      format,
      include_original: true
    }
    
    exportMutation.mutate(exportData)
  }

  // 文档表格列配置
  const documentColumns: TableColumnsType<TaskDocument> = [
    {
      title: '文档名称',
      dataIndex: 'filename',
      key: 'filename',
      render: (text: string) => (
        <Space>
          <FileTextOutlined />
          <Text strong>{text}</Text>
        </Space>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getDocumentStatusTag(status)
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record: TaskDocument) => {
        const canAnnotate = user?.id === task?.assignee_id || user?.role === 'super_admin' || user?.role === 'admin'
        const canReview = user?.role === 'super_admin' || user?.role === 'admin'

        return (
          <Space>
            {canAnnotate && record.status === 'pending' && (
              <Button
                type="primary"
                size="small"
                icon={<EditOutlined />}
                onClick={() => handleStartAnnotation(record.id)}
              >
                开始标注
              </Button>
            )}
            {record.status === 'completed' && (
              <Button
                size="small"
                icon={<EyeOutlined />}
                onClick={() => handleViewAnnotation(record.id)}
              >
                查看结果
              </Button>
            )}
            {canReview && record.status === 'completed' && (
              <Button
                size="small"
                type="dashed"
                onClick={() => navigate(`/tasks/${taskId}/review/${record.id}`)}
              >
                复审
              </Button>
            )}
          </Space>
        )
      }
    }
  ]

  if (taskLoading) {
    return (
      <div className="page-container">
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>加载任务详情中...</Text>
          </div>
        </div>
      </div>
    )
  }

  if (taskError || !task) {
    return (
      <div className="page-container">
        <Alert
          message="加载失败"
          description="无法加载任务详情，请检查任务ID是否正确"
          type="error"
          showIcon
          action={
            <Button size="small" onClick={() => navigate('/tasks')}>
              返回任务列表
            </Button>
          }
        />
      </div>
    )
  }

  const progress = getTaskProgress()
  const canEdit = user?.role === 'super_admin' || user?.role === 'admin' || user?.id === task.creator_id
  const canExport = user?.role === 'super_admin' || user?.role === 'admin'

  return (
    <div className="page-container">
      <div className="page-header">
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/tasks')}
          >
            返回
          </Button>
          <Title level={3} className="page-title">{task.name}</Title>
          {getStatusTag(task.status)}
        </Space>
        <Space>
          {canEdit && (
            <Button
              icon={<EditOutlined />}
              onClick={() => navigate(`/tasks/${taskId}/edit`)}
            >
              编辑任务
            </Button>
          )}
          {canExport && (
            <Button
              type="primary"
              icon={<ExportOutlined />}
              onClick={() => setExportModalVisible(true)}
            >
              导出数据
            </Button>
          )}
        </Space>
      </div>

      <Row gutter={[16, 16]}>
        {/* 任务概览 */}
        <Col span={24}>
          <Card title="任务概览">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="总进度"
                  value={progress}
                  suffix="%"
                  valueStyle={{ color: progress === 100 ? '#3f8600' : '#1890ff' }}
                />
                <Progress percent={progress} size="small" />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="文档总数"
                  value={task.documents.length}
                  suffix="个"
                />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="已完成"
                  value={task.documents.filter(d => d.status === 'completed').length}
                  suffix="个"
                  valueStyle={{ color: '#3f8600' }}
                />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="待标注"
                  value={task.documents.filter(d => d.status === 'pending').length}
                  suffix="个"
                  valueStyle={{ color: '#cf1322' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 任务信息 */}
        <Col xs={24} lg={12}>
          <Card title="任务信息">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="任务名称">
                <Text strong>{task.name}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="任务描述">
                <Paragraph>{task.description}</Paragraph>
              </Descriptions.Item>
              <Descriptions.Item label="任务状态">
                {getStatusTag(task.status)}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                <Space>
                  <ClockCircleOutlined />
                  <Text>{new Date(task.created_at).toLocaleString()}</Text>
                </Space>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 人员信息 */}
        <Col xs={24} lg={12}>
          <Card title="人员信息">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="创建者">
                <Space>
                  <Avatar size="small" icon={<UserOutlined />} />
                  <Text>{getUserName(task.creator_id)}</Text>
                  <Tag>{getUserRole(task.creator_id)}</Tag>
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="负责人">
                <Space>
                  <Avatar size="small" icon={<UserOutlined />} />
                  <Text>{task.assignee_id ? getUserName(task.assignee_id) : '未分配'}</Text>
                  {task.assignee_id && <Tag>{getUserRole(task.assignee_id)}</Tag>}
                </Space>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 模板信息 */}
        <Col span={24}>
          <Card title="模板信息">
            <Descriptions column={2} size="small">
              <Descriptions.Item label="模板文件">
                <Space>
                  <FileTextOutlined />
                  <Text>{task.template.filename}</Text>
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="文件路径">
                <Text type="secondary">{task.template.file_path}</Text>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        {/* 文档列表 */}
        <Col span={24}>
          <Card title="文档列表">
            <Table
              columns={documentColumns}
              dataSource={task.documents}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      {/* 导出模态框 */}
      <Modal
        title="导出任务数据"
        open={exportModalVisible}
        onCancel={() => setExportModalVisible(false)}
        footer={null}
        width={400}
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <Text>选择导出格式：</Text>
          <Divider />
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Button
              block
              size="large"
              onClick={() => handleExport('json')}
              loading={exportMutation.isPending}
            >
              JSON 格式
            </Button>
            <Button
              block
              size="large"
              onClick={() => handleExport('csv')}
              loading={exportMutation.isPending}
            >
              CSV 格式
            </Button>
            <Button
              block
              size="large"
              onClick={() => handleExport('excel')}
              loading={exportMutation.isPending}
            >
              Excel 格式
            </Button>
          </Space>
        </div>
      </Modal>
    </div>
  )
}

export default TaskDetail 