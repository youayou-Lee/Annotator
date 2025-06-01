import React, { useState, useEffect } from 'react'
import {
  Layout,
  Typography,
  Button,
  List,
  Space,
  Progress,
  Form,
  Input,
  Select,
  Switch,
  DatePicker,
  InputNumber,
  message,
  Spin,
  Alert,
  Breadcrumb,
  Badge,
  Tooltip,
  Row,
  Col,
  Tag
} from 'antd'
import {
  ArrowLeftOutlined,
  SaveOutlined,
  CheckOutlined,
  EyeOutlined,
  LeftOutlined,
  RightOutlined,
  ReloadOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { taskAPI, annotationAPI } from '../../services/api'
import MonacoEditor from '@monaco-editor/react'

const { Title, Text } = Typography
const { Sider, Content } = Layout
const { TextArea } = Input
const { Option } = Select

interface AnnotationField {
  name: string
  type: 'string' | 'text' | 'number' | 'boolean' | 'date' | 'select' | 'multiselect' | 'array' | 'object'
  required: boolean
  description?: string
  placeholder?: string
  default?: any
  options?: Array<{ value: string; label: string }>
  max_length?: number
  min_length?: number
  max_value?: number
  min_value?: number
  rows?: number
  properties?: Record<string, AnnotationField>
  item_type?: string
}

const Annotation: React.FC = () => {
  const { taskId, documentId } = useParams<{ taskId: string; documentId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form] = Form.useForm()
  
  const [siderCollapsed, setSiderCollapsed] = useState(false)
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true)
  const [lastSaveTime, setLastSaveTime] = useState<Date | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  // 获取任务详情
  const { data: taskResponse, isLoading: taskLoading } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => taskAPI.getTask(taskId!),
    enabled: !!taskId
  })

  const task = taskResponse?.data

  // 获取当前文档的标注数据
  const { data: annotationResponse, isLoading: annotationLoading } = useQuery({
    queryKey: ['annotation', taskId, documentId],
    queryFn: () => annotationAPI.getAnnotation(taskId!, documentId!),
    enabled: !!taskId && !!documentId
  })

  const annotation = annotationResponse?.data

  // 保存标注数据
  const saveAnnotationMutation = useMutation({
    mutationFn: (data: any) => annotationAPI.saveAnnotation(taskId!, documentId!, { annotated_data: data }),
    onSuccess: () => {
      setLastSaveTime(new Date())
      setHasUnsavedChanges(false)
      message.success('保存成功')
      queryClient.invalidateQueries({ queryKey: ['annotation', taskId, documentId] })
    },
    onError: () => {
      message.error('保存失败')
    }
  })

  // 提交标注
  const submitAnnotationMutation = useMutation({
    mutationFn: () => annotationAPI.submitAnnotation(taskId!, documentId!),
    onSuccess: () => {
      message.success('提交成功')
      queryClient.invalidateQueries({ queryKey: ['task', taskId] })
      queryClient.invalidateQueries({ queryKey: ['annotation', taskId, documentId] })
    },
    onError: () => {
      message.error('提交失败')
    }
  })

  // 获取当前文档
  const currentDocument = task?.documents.find(doc => doc.id === documentId)

  // 获取模板字段定义（这里模拟从模板文件解析）
  const getTemplateFields = (): AnnotationField[] => {
    // 这里应该从模板文件解析，现在先用模拟数据
    return [
      {
        name: 'title',
        type: 'string',
        required: true,
        description: '文档标题',
        max_length: 100,
        placeholder: '请输入文档标题'
      },
      {
        name: 'category',
        type: 'select',
        required: true,
        description: '文档类别',
        options: [
          { value: 'contract', label: '合同' },
          { value: 'report', label: '报告' },
          { value: 'invoice', label: '发票' }
        ]
      },
      {
        name: 'content',
        type: 'text',
        required: true,
        description: '文档内容',
        rows: 5,
        placeholder: '请输入文档内容'
      },
      {
        name: 'amount',
        type: 'number',
        required: false,
        description: '金额',
        min_value: 0,
        max_value: 999999
      },
      {
        name: 'is_valid',
        type: 'boolean',
        required: false,
        description: '是否有效',
        default: false
      },
      {
        name: 'tags',
        type: 'multiselect',
        required: false,
        description: '标签',
        options: [
          { value: 'urgent', label: '紧急' },
          { value: 'important', label: '重要' },
          { value: 'confidential', label: '机密' }
        ]
      }
    ]
  }

  const templateFields = getTemplateFields()

  // 表单值变化处理
  const handleFormChange = () => {
    setHasUnsavedChanges(true)
    if (autoSaveEnabled) {
      // 防抖保存
      const timer = setTimeout(() => {
        handleSave()
      }, 2000)
      return () => clearTimeout(timer)
    }
  }

  // 保存标注数据
  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      saveAnnotationMutation.mutate(values)
    } catch (error) {
      console.error('表单验证失败:', error)
    }
  }

  // 提交标注
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      await saveAnnotationMutation.mutateAsync(values)
      await submitAnnotationMutation.mutateAsync()
    } catch (error) {
      console.error('提交失败:', error)
    }
  }

  // 切换文档
  const handleDocumentChange = (docId: string) => {
    if (hasUnsavedChanges) {
      message.warning('请先保存当前文档的修改')
      return
    }
    navigate(`/tasks/${taskId}/documents/${docId}/annotation`)
  }

  // 上一个/下一个文档
  const handlePrevDocument = () => {
    if (!task?.documents) return
    const currentIndex = task.documents.findIndex(doc => doc.id === documentId)
    if (currentIndex > 0) {
      const prevDoc = task.documents[currentIndex - 1]
      handleDocumentChange(prevDoc.id)
    }
  }

  const handleNextDocument = () => {
    if (!task?.documents) return
    const currentIndex = task.documents.findIndex(doc => doc.id === documentId)
    if (currentIndex < task.documents.length - 1) {
      const nextDoc = task.documents[currentIndex + 1]
      handleDocumentChange(nextDoc.id)
    }
  }

  // 渲染表单字段
  const renderFormField = (field: AnnotationField) => {
    const commonProps = {
      placeholder: field.placeholder,
      disabled: annotation?.status === 'completed'
    }

    switch (field.type) {
      case 'string':
        return (
          <Input
            {...commonProps}
            maxLength={field.max_length}
            showCount={!!field.max_length}
          />
        )
      
      case 'text':
        return (
          <TextArea
            {...commonProps}
            rows={field.rows || 4}
            maxLength={field.max_length}
            showCount={!!field.max_length}
          />
        )
      
      case 'number':
        return (
          <InputNumber
            {...commonProps}
            min={field.min_value}
            max={field.max_value}
            style={{ width: '100%' }}
          />
        )
      
      case 'boolean':
        return <Switch disabled={annotation?.status === 'completed'} />
      
      case 'date':
        return <DatePicker {...commonProps} style={{ width: '100%' }} />
      
      case 'select':
        return (
          <Select {...commonProps}>
            {field.options?.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        )
      
      case 'multiselect':
        return (
          <Select {...commonProps} mode="multiple">
            {field.options?.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        )
      
      default:
        return <Input {...commonProps} />
    }
  }

  // 初始化表单数据
  useEffect(() => {
    if (annotation?.annotated_data) {
      form.setFieldsValue(annotation.annotated_data)
      setHasUnsavedChanges(false)
    }
  }, [annotation, form])

  if (taskLoading || annotationLoading) {
    return (
      <div className="page-container">
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>加载标注数据中...</Text>
          </div>
        </div>
      </div>
    )
  }

  if (!task || !currentDocument) {
    return (
      <div className="page-container">
        <Alert
          message="加载失败"
          description="无法加载任务或文档信息"
          type="error"
          showIcon
        />
      </div>
    )
  }

  const currentIndex = task.documents.findIndex(doc => doc.id === documentId)
  const progress = Math.round(((currentIndex + 1) / task.documents.length) * 100)

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部导航栏 */}
      <div style={{ 
        padding: '16px 24px', 
        borderBottom: '1px solid #f0f0f0',
        background: '#fff'
      }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate(`/tasks/${taskId}`)}
              >
                返回任务
              </Button>
              <Breadcrumb>
                <Breadcrumb.Item>{task.name}</Breadcrumb.Item>
                <Breadcrumb.Item>{currentDocument.filename}</Breadcrumb.Item>
              </Breadcrumb>
            </Space>
          </Col>
          <Col>
            <Space>
              <Text type="secondary">
                进度: {currentIndex + 1}/{task.documents.length}
              </Text>
              <Progress percent={progress} size="small" style={{ width: 100 }} />
              {hasUnsavedChanges && (
                <Tag color="orange">未保存</Tag>
              )}
              {lastSaveTime && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  最后保存: {lastSaveTime.toLocaleTimeString()}
                </Text>
              )}
            </Space>
          </Col>
        </Row>
      </div>

      {/* 主要内容区域 */}
      <Layout style={{ flex: 1 }}>
        {/* 左侧文档列表 */}
        <Sider
          width={280}
          collapsed={siderCollapsed}
          onCollapse={setSiderCollapsed}
          style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}
        >
          <div style={{ padding: '16px' }}>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={5} style={{ margin: 0 }}>文档列表</Title>
              <Button
                type="text"
                size="small"
                icon={<ReloadOutlined />}
                onClick={() => queryClient.invalidateQueries({ queryKey: ['task', taskId] })}
              />
            </div>
            <List
              size="small"
              dataSource={task.documents}
              renderItem={(doc) => (
                <List.Item
                  style={{
                    cursor: 'pointer',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    marginBottom: '4px',
                    background: doc.id === documentId ? '#e6f7ff' : 'transparent',
                    border: doc.id === documentId ? '1px solid #91d5ff' : '1px solid transparent'
                  }}
                  onClick={() => handleDocumentChange(doc.id)}
                >
                  <List.Item.Meta
                    avatar={
                      <Badge
                        status={doc.status === 'completed' ? 'success' : 'processing'}
                        dot
                      />
                    }
                    title={
                      <Text strong={doc.id === documentId}>
                        {doc.filename}
                      </Text>
                    }
                    description={
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {doc.status === 'completed' ? '已完成' : '待标注'}
                      </Text>
                    }
                  />
                </List.Item>
              )}
            />
          </div>
        </Sider>

        {/* 中间文档内容区域 */}
        <Content style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}>
          <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={5} style={{ margin: 0 }}>原始文档</Title>
              <Space>
                <Button
                  type="text"
                  size="small"
                  icon={<EyeOutlined />}
                >
                  格式化
                </Button>
              </Space>
            </div>
            <div style={{ flex: 1, border: '1px solid #d9d9d9', borderRadius: '6px' }}>
              <MonacoEditor
                height="100%"
                language="json"
                value={JSON.stringify(annotation?.original_data || {}, null, 2)}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  fontSize: 14,
                  lineNumbers: 'on',
                  folding: true,
                  wordWrap: 'on'
                }}
                theme="vs"
              />
            </div>
          </div>
        </Content>

        {/* 右侧标注表单区域 */}
        <Content style={{ background: '#fff', width: '400px', minWidth: '400px' }}>
          <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={5} style={{ margin: 0 }}>标注表单</Title>
              <Space>
                <Tooltip title="自动保存">
                  <Switch
                    size="small"
                    checked={autoSaveEnabled}
                    onChange={setAutoSaveEnabled}
                  />
                </Tooltip>
              </Space>
            </div>
            
            <div style={{ flex: 1, overflow: 'auto' }}>
              <Form
                form={form}
                layout="vertical"
                onValuesChange={handleFormChange}
                disabled={annotation?.status === 'completed'}
              >
                {templateFields.map(field => (
                  <Form.Item
                    key={field.name}
                    name={field.name}
                    label={field.description || field.name}
                    rules={[
                      { required: field.required, message: `请输入${field.description || field.name}` }
                    ]}
                  >
                    {renderFormField(field)}
                  </Form.Item>
                ))}
              </Form>
            </div>
          </div>
        </Content>
      </Layout>

      {/* 底部操作栏 */}
      <div style={{
        padding: '16px 24px',
        borderTop: '1px solid #f0f0f0',
        background: '#fff',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Space>
          <Button
            icon={<LeftOutlined />}
            onClick={handlePrevDocument}
            disabled={currentIndex === 0}
          >
            上一个
          </Button>
          <Button
            icon={<RightOutlined />}
            onClick={handleNextDocument}
            disabled={currentIndex === task.documents.length - 1}
          >
            下一个
          </Button>
        </Space>

        <Space>
          <Button
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saveAnnotationMutation.isPending}
            disabled={annotation?.status === 'completed'}
          >
            保存
          </Button>
          <Button
            type="primary"
            icon={<CheckOutlined />}
            onClick={handleSubmit}
            loading={submitAnnotationMutation.isPending}
            disabled={annotation?.status === 'completed'}
          >
            {annotation?.status === 'completed' ? '已完成' : '提交'}
          </Button>
        </Space>
      </div>
    </div>
  )
}

export default Annotation 