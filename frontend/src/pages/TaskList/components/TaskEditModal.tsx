import React, { useState, useEffect } from 'react'
import {
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  App,
  Spin,
  Card,
  List,
  Typography,
  Space,
  Tag,
  Row,
  Col
} from 'antd'
import { FileTextOutlined, CodeOutlined, UserOutlined } from '@ant-design/icons'
import { useQuery, useMutation } from '@tanstack/react-query'
import { taskAPI, fileAPI, userAPI } from '../../../services/api'
import { useAuthStore } from '../../../stores/authStore'
import type { Task, CreateTaskRequest, FileItem } from '../../../types'
import dayjs from 'dayjs'

const { TextArea } = Input
const { Option } = Select
const { Text } = Typography

interface TaskEditModalProps {
  visible: boolean
  task: Task | null
  onCancel: () => void
  onSuccess: () => void
}

const TaskEditModal: React.FC<TaskEditModalProps> = ({
  visible,
  task,
  onCancel,
  onSuccess
}) => {
  const [form] = Form.useForm()
  const { user, hasPermission } = useAuthStore()
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const { message } = App.useApp()

  // 获取文档文件
  const { data: documentsResponse, isLoading: documentsLoading } = useQuery({
    queryKey: ['files', 'documents'],
    queryFn: () => fileAPI.getFiles('documents'),
    enabled: visible
  })

  // 获取模板文件
  const { data: templatesResponse, isLoading: templatesLoading } = useQuery({
    queryKey: ['files', 'templates'],
    queryFn: () => fileAPI.getFiles('templates'),
    enabled: visible
  })

  // 获取用户列表
  const { data: usersResponse, isLoading: usersLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => userAPI.getUsers(),
    enabled: visible && hasPermission('task.assign')
  })

  const documents = documentsResponse?.data || []
  const templates = templatesResponse?.data || []
  const users = usersResponse?.data || []

  // 更新任务
  const updateMutation = useMutation({
    mutationFn: ({ taskId, data }: { taskId: string; data: Partial<CreateTaskRequest> }) =>
      taskAPI.updateTask(taskId, data),
    onSuccess: () => {
      message.success('任务更新成功')
      onSuccess()
    },
    onError: (error: any) => {
      message.error(error.message || '更新任务失败')
    }
  })

  // 初始化表单数据
  useEffect(() => {
    if (task && visible) {
      form.setFieldsValue({
        name: task.name,
        description: task.description,
        assignee_id: task.assignee_id,
        deadline: task.deadline ? dayjs(task.deadline) : undefined
      })
      
      // 设置已选择的文档
      const documentIds = task.documents?.map(doc => doc.id) || []
      setSelectedDocuments(documentIds)
      
      // 设置已选择的模板
      setSelectedTemplate(task.template?.id || '')
    }
  }, [task, visible, form])

  // 处理表单提交
  const handleSubmit = async () => {
    if (!task) return
    
    try {
      const values = await form.validateFields()
      
      if (selectedDocuments.length === 0) {
        message.error('请选择至少一个文档文件')
        return
      }
      
      if (!selectedTemplate) {
        message.error('请选择一个模板文件')
        return
      }

      // 将文件ID转换为文件路径
      const selectedDocumentPaths = selectedDocuments.map(docId => {
        const doc = documents.find(d => d.id === docId)
        return doc?.file_path || ''
      }).filter(path => path !== '')

      const selectedTemplatePath = templates.find(t => t.id === selectedTemplate)?.file_path || ''

      if (selectedDocumentPaths.length === 0) {
        message.error('选择的文档文件无效')
        return
      }

      if (!selectedTemplatePath) {
        message.error('选择的模板文件无效')
        return
      }

      const taskData: Partial<CreateTaskRequest> = {
        name: values.name,
        description: values.description,
        documents: selectedDocumentPaths,  // 使用文件路径而不是ID
        template_path: selectedTemplatePath,  // 使用文件路径而不是ID
        assignee_id: values.assignee_id,
        deadline: values.deadline?.format('YYYY-MM-DD')
      }

      updateMutation.mutate({ taskId: task.id, data: taskData })
    } catch (error) {
      console.error('表单验证失败:', error)
    }
  }

  // 处理取消
  const handleCancel = () => {
    form.resetFields()
    setSelectedDocuments([])
    setSelectedTemplate('')
    onCancel()
  }

  // 过滤JSON/JSONL文件
  const jsonDocuments = documents.filter(file => 
    file.filename.toLowerCase().endsWith('.json') || 
    file.filename.toLowerCase().endsWith('.jsonl')
  )

  // 过滤Python模板文件
  const pythonTemplates = templates.filter(file => 
    file.filename.toLowerCase().endsWith('.py')
  )

  if (!task) return null

  return (
    <Modal
      title="编辑任务"
      open={visible}
      onCancel={handleCancel}
      onOk={handleSubmit}
      confirmLoading={updateMutation.isPending}
      width={800}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="name"
              label="任务名称"
              rules={[{ required: true, message: '请输入任务名称' }]}
            >
              <Input placeholder="请输入任务名称" />
            </Form.Item>
          </Col>
          <Col span={12}>
            {hasPermission('task.assign') ? (
              <Form.Item
                name="assignee_id"
                label="分配给"
              >
                <Select
                  placeholder="选择负责人（可稍后分配）"
                  allowClear
                  loading={usersLoading}
                  showSearch
                  filterOption={(input, option) =>
                    String(option?.children || '').toLowerCase().includes(input.toLowerCase())
                  }
                >
                  {users.map(user => (
                    <Option key={user.id} value={user.id}>
                      <Space>
                        <UserOutlined />
                        {user.username}
                        <Tag>{user.role}</Tag>
                      </Space>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            ) : (
              <Form.Item label="分配给">
                <Input value={task.assignee_id ? users.find(u => u.id === task.assignee_id)?.username : '未分配'} disabled />
              </Form.Item>
            )}
          </Col>
        </Row>

        <Form.Item
          name="description"
          label="任务描述"
          rules={[{ required: true, message: '请输入任务描述' }]}
        >
          <TextArea
            rows={3}
            placeholder="请描述任务的具体要求和标注规范"
          />
        </Form.Item>

        <Form.Item
          name="deadline"
          label="截止日期"
        >
          <DatePicker
            style={{ width: '100%' }}
            placeholder="选择截止日期（可选）"
          />
        </Form.Item>

        <Form.Item
          label="选择文档文件"
          required
        >
          <Card size="small" style={{ maxHeight: 200, overflow: 'auto' }}>
            <Spin spinning={documentsLoading}>
              {jsonDocuments.length === 0 ? (
                <Text type="secondary">暂无可用的JSON/JSONL文档文件</Text>
              ) : (
                <List
                  size="small"
                  dataSource={jsonDocuments}
                  renderItem={(file: FileItem) => (
                    <List.Item
                      style={{
                        cursor: 'pointer',
                        backgroundColor: selectedDocuments.includes(file.id) ? '#f0f8ff' : 'transparent'
                      }}
                      onClick={() => {
                        if (selectedDocuments.includes(file.id)) {
                          setSelectedDocuments(prev => prev.filter(id => id !== file.id))
                        } else {
                          setSelectedDocuments(prev => [...prev, file.id])
                        }
                      }}
                    >
                      <List.Item.Meta
                        avatar={<FileTextOutlined />}
                        title={file.filename}
                        description={`大小: ${(file.file_size / 1024).toFixed(1)} KB`}
                      />
                      {selectedDocuments.includes(file.id) && (
                        <Tag color="blue">已选择</Tag>
                      )}
                    </List.Item>
                  )}
                />
              )}
            </Spin>
          </Card>
          {selectedDocuments.length > 0 && (
            <Text type="secondary">已选择 {selectedDocuments.length} 个文档文件</Text>
          )}
        </Form.Item>

        <Form.Item
          label="选择模板文件"
          required
        >
          <Card size="small" style={{ maxHeight: 200, overflow: 'auto' }}>
            <Spin spinning={templatesLoading}>
              {pythonTemplates.length === 0 ? (
                <Text type="secondary">暂无可用的Python模板文件</Text>
              ) : (
                <List
                  size="small"
                  dataSource={pythonTemplates}
                  renderItem={(file: FileItem) => (
                    <List.Item
                      style={{
                        cursor: 'pointer',
                        backgroundColor: selectedTemplate === file.id ? '#f0f8ff' : 'transparent'
                      }}
                      onClick={() => {
                        setSelectedTemplate(selectedTemplate === file.id ? '' : file.id)
                      }}
                    >
                      <List.Item.Meta
                        avatar={<CodeOutlined />}
                        title={file.filename}
                        description={`大小: ${(file.file_size / 1024).toFixed(1)} KB`}
                      />
                      {selectedTemplate === file.id && (
                        <Tag color="green">已选择</Tag>
                      )}
                    </List.Item>
                  )}
                />
              )}
            </Spin>
          </Card>
          {selectedTemplate && (
            <Text type="secondary">已选择模板文件</Text>
          )}
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default TaskEditModal 