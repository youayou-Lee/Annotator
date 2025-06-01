import React from 'react'
import { Card, Typography, Space, Tag } from 'antd'
import { useAuthStore } from '../../stores/authStore'

const { Title, Text } = Typography

const TaskList: React.FC = () => {
  const { user, hasPermission, hasRole } = useAuthStore()

  return (
    <div style={{ padding: '24px' }}>
      <Card title="任务列表">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Title level={4}>欢迎使用文书标注系统</Title>
            <Text type="secondary">
              这是任务列表页面，您可以在这里查看和管理标注任务。
            </Text>
          </div>

          <div>
            <Title level={5}>当前用户信息</Title>
            <Space direction="vertical">
              <Text>用户名: {user?.username}</Text>
              <Text>角色: {user?.role}</Text>
              <Text>创建时间: {user?.created_at ? new Date(user.created_at).toLocaleString() : '未知'}</Text>
            </Space>
          </div>

          <div>
            <Title level={5}>权限检查</Title>
            <Space wrap>
              <Tag color={hasPermission('user.manage') ? 'green' : 'red'}>
                用户管理: {hasPermission('user.manage') ? '有权限' : '无权限'}
              </Tag>
              <Tag color={hasPermission('file.upload') ? 'green' : 'red'}>
                文件上传: {hasPermission('file.upload') ? '有权限' : '无权限'}
              </Tag>
              <Tag color={hasPermission('task.create') ? 'green' : 'red'}>
                任务创建: {hasPermission('task.create') ? '有权限' : '无权限'}
              </Tag>
              <Tag color={hasPermission('task.annotate') ? 'green' : 'red'}>
                任务标注: {hasPermission('task.annotate') ? '有权限' : '无权限'}
              </Tag>
              <Tag color={hasPermission('task.review') ? 'green' : 'red'}>
                任务复审: {hasPermission('task.review') ? '有权限' : '无权限'}
              </Tag>
            </Space>
          </div>

          <div>
            <Title level={5}>角色检查</Title>
            <Space wrap>
              <Tag color={hasRole('super_admin') ? 'green' : 'red'}>
                超级管理员: {hasRole('super_admin') ? '是' : '否'}
              </Tag>
              <Tag color={hasRole('admin') ? 'green' : 'red'}>
                管理员: {hasRole('admin') ? '是' : '否'}
              </Tag>
              <Tag color={hasRole('annotator') ? 'green' : 'red'}>
                标注员: {hasRole('annotator') ? '是' : '否'}
              </Tag>
              <Tag color={hasRole(['admin', 'super_admin']) ? 'green' : 'red'}>
                管理员或超级管理员: {hasRole(['admin', 'super_admin']) ? '是' : '否'}
              </Tag>
            </Space>
          </div>

          <div>
            <Text type="secondary">
              注意：这是一个演示页面，用于展示用户认证和权限控制功能。
              实际的任务列表功能将在后续开发中实现。
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  )
}

export default TaskList 