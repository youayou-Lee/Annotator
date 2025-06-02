import React, { useState, useEffect, useCallback, useRef } from 'react'
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
  App,
  Spin,
  Alert,
  Breadcrumb,
  Badge,
  Tooltip,
  Row,
  Col,
  Tag,
  Card,
  Divider,
  Checkbox,
  Radio,
  TimePicker,
  Upload,
  Modal,
  notification
} from 'antd'
import {
  ArrowLeftOutlined,
  SaveOutlined,
  CheckOutlined,
  EyeOutlined,
  LeftOutlined,
  RightOutlined,
  ReloadOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  FileTextOutlined,
  FormOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { taskAPI, annotationAPI } from '../../services/api'
import MonacoEditor from '@monaco-editor/react'
import dayjs from 'dayjs'
import FormFieldRenderer, { FormField as FormFieldType } from './components/FormFieldRenderer'

const { Title, Text, Paragraph } = Typography
const { Sider, Content } = Layout
const { TextArea } = Input
const { Option } = Select
const { Group: CheckboxGroup } = Checkbox
const { Group: RadioGroup } = Radio

// 设置 Monaco Editor 环境变量，避免 CDN 加载
if (typeof window !== 'undefined') {
  (window as any).MonacoEnvironment = {
    getWorker: () => {
      // 返回一个简单的 worker，避免网络请求
      return new Worker(
        URL.createObjectURL(
          new Blob([`
            self.onmessage = function() {
              // 简单的 worker，不做任何操作
              self.postMessage({});
            };
          `], { type: 'application/javascript' })
        )
      )
    }
  }
}

// 字段类型定义
interface FormField {
  name: string
  type: 'string' | 'text' | 'number' | 'boolean' | 'date' | 'datetime' | 'time' | 'select' | 'multiselect' | 'radio' | 'checkbox' | 'array' | 'object' | 'file'
  required: boolean
  label: string
  description?: string
  placeholder?: string
  default?: any
  options?: Array<{ value: string; label: string }>
  validation?: {
    max_length?: number
    min_length?: number
    max_value?: number
    min_value?: number
    pattern?: string
    message?: string
  }
  ui?: {
    rows?: number
    multiple?: boolean
    format?: string
    showTime?: boolean
  }
  properties?: Record<string, FormField>
  items?: FormField
  dependencies?: string[]
  conditional?: {
    field: string
    value: any
    operator: 'eq' | 'ne' | 'gt' | 'lt' | 'in' | 'not_in'
  }
}

// 文档状态类型
interface DocumentItem {
  id: string
  filename: string
  status: 'pending' | 'in_progress' | 'completed' | 'reviewed'
  progress?: number
  last_modified?: string
  assignee?: string
}

// 进度信息类型
interface ProgressInfo {
  total_documents: number
  completed_documents: number
  in_progress_documents: number
  pending_documents: number
  progress_percentage: number
  current_document_index?: number
}

const Annotation: React.FC = () => {
  const { taskId, documentId } = useParams<{ taskId: string; documentId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form] = Form.useForm()
  const { message } = App.useApp()
  
  // 状态管理
  const [siderCollapsed, setSiderCollapsed] = useState(false)
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true)
  const [lastSaveTime, setLastSaveTime] = useState<Date | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const [isValidating, setIsValidating] = useState(false)
  const [documentContent, setDocumentContent] = useState<any>(null)
  const [formFields, setFormFields] = useState<FormFieldType[]>([])
  const [currentDocumentIndex, setCurrentDocumentIndex] = useState(0)
  
  // 自动保存定时器
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null)
  const validationTimerRef = useRef<NodeJS.Timeout | null>(null)

  // 获取任务详情
  const { data: taskResponse, isLoading: taskLoading } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => taskAPI.getTask(taskId!),
    enabled: !!taskId
  })

  // 获取文档列表
  const { data: documentsResponse, isLoading: documentsLoading } = useQuery({
    queryKey: ['documents', taskId],
    queryFn: () => annotationAPI.getDocuments(taskId!),
    enabled: !!taskId
  })

  // 获取当前文档内容
  const { data: contentResponse, isLoading: contentLoading } = useQuery({
    queryKey: ['document-content', taskId, documentId],
    queryFn: () => annotationAPI.getDocumentContent(taskId!, documentId!),
    enabled: !!taskId && !!documentId
  })

  // 获取表单配置
  const { data: formConfigResponse, isLoading: formConfigLoading } = useQuery({
    queryKey: ['form-config', taskId, documentId],
    queryFn: () => annotationAPI.getFormConfig(taskId!, documentId!),
    enabled: !!taskId && !!documentId
  })

  // 获取标注数据
  const { data: annotationResponse, isLoading: annotationLoading } = useQuery({
    queryKey: ['annotation', taskId, documentId],
    queryFn: () => annotationAPI.getAnnotation(taskId!, documentId!),
    enabled: !!taskId && !!documentId
  })

  // 获取任务进度
  const { data: progressResponse } = useQuery({
    queryKey: ['task-progress', taskId, documentId],
    queryFn: () => annotationAPI.getTaskProgress(taskId!, documentId),
    enabled: !!taskId && !!documentId,
    refetchInterval: 30000 // 每30秒刷新一次进度
  })

  // 保存标注数据
  const saveAnnotationMutation = useMutation({
    mutationFn: (data: any) => annotationAPI.saveAnnotation(taskId!, documentId!, {
      annotated_data: data,
      is_auto_save: autoSaveEnabled
    }),
    onSuccess: (response) => {
      if (response.success) {
        setLastSaveTime(new Date())
        setHasUnsavedChanges(false)
        setValidationErrors({})
        if (!autoSaveEnabled) {
          message.success('保存成功')
        }
        queryClient.invalidateQueries({ queryKey: ['annotation', taskId, documentId] })
        queryClient.invalidateQueries({ queryKey: ['task-progress', taskId] })
      }
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '保存失败')
    }
  })

  // 提交标注
  const submitAnnotationMutation = useMutation({
    mutationFn: (data: any) => annotationAPI.submitAnnotation(taskId!, documentId!, {
      annotated_data: data,
      submit_comment: '标注完成'
    }),
    onSuccess: (response) => {
      if (response.success) {
        message.success('提交成功')
        queryClient.invalidateQueries({ queryKey: ['annotation', taskId, documentId] })
        queryClient.invalidateQueries({ queryKey: ['documents', taskId] })
        queryClient.invalidateQueries({ queryKey: ['task-progress', taskId] })
        
        // 自动跳转到下一个文档
        const documents = documentsResponse?.data?.documents || []
        const normalizedDocuments = documents.map((doc: any) => ({
          id: doc.document_id || doc.id,
          filename: doc.document_name || doc.filename,
          status: doc.status,
          progress: doc.completion_percentage,
          last_modified: doc.last_modified,
          assignee: doc.assignee
        }))
        const currentIndex = normalizedDocuments.findIndex((doc: DocumentItem) => doc.id === documentId)
        if (currentIndex < normalizedDocuments.length - 1) {
          const nextDoc = normalizedDocuments[currentIndex + 1]
          navigate(`/tasks/${taskId}/documents/${nextDoc.id}/annotation`)
        }
      }
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '提交失败')
    }
  })

  // 实时验证
  const validatePartialMutation = useMutation({
    mutationFn: (data: any) => annotationAPI.validatePartial({
      task_id: taskId!,
      document_id: documentId!,
      partial_data: data,
      fields: formFields.map(f => f.name)
    }),
    onSuccess: (response) => {
      if (response.success) {
        setValidationErrors(response.data.errors || {})
      }
    }
  })

  // 表单值变化处理
  const handleFormChange = useCallback((changedValues: any, allValues: any) => {
    setHasUnsavedChanges(true)
    
    // 清除自动保存定时器
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current)
    }
    
    // 清除验证定时器
    if (validationTimerRef.current) {
      clearTimeout(validationTimerRef.current)
    }

    // 实时验证（防抖）
    validationTimerRef.current = setTimeout(() => {
      validatePartialMutation.mutate(allValues)
    }, 500)

    // 自动保存（防抖）
    if (autoSaveEnabled) {
      autoSaveTimerRef.current = setTimeout(() => {
        handleSave(allValues)
      }, 2000)
    }
  }, [autoSaveEnabled, taskId, documentId])

  // 保存标注数据
  const handleSave = useCallback(async (values?: any) => {
    try {
      const formValues = values || await form.validateFields()
      saveAnnotationMutation.mutate(formValues)
    } catch (error) {
      console.error('表单验证失败:', error)
    }
  }, [form, saveAnnotationMutation])

  // 提交标注
  const handleSubmit = useCallback(async () => {
    try {
      const values = await form.validateFields()
      
      // 先保存再提交
      await saveAnnotationMutation.mutateAsync(values)
      await submitAnnotationMutation.mutateAsync(values)
    } catch (error) {
      console.error('提交失败:', error)
      message.error('请检查表单填写是否完整')
    }
  }, [form, saveAnnotationMutation, submitAnnotationMutation])

  // 切换文档
  const handleDocumentChange = useCallback((docId: string) => {
    if (hasUnsavedChanges) {
      Modal.confirm({
        title: '未保存的更改',
        content: '当前文档有未保存的更改，是否保存后切换？',
        okText: '保存并切换',
        cancelText: '直接切换',
        onOk: async () => {
          await handleSave()
          navigate(`/tasks/${taskId}/documents/${docId}/annotation`)
        },
        onCancel: () => {
          navigate(`/tasks/${taskId}/documents/${docId}/annotation`)
        }
      })
    } else {
      navigate(`/tasks/${taskId}/documents/${docId}/annotation`)
    }
  }, [hasUnsavedChanges, handleSave, navigate, taskId])

  // 上一个/下一个文档
  const handlePrevDocument = useCallback(() => {
    const documents = documentsResponse?.data?.documents || []
    const normalizedDocuments = documents.map((doc: any) => ({
      id: doc.document_id || doc.id,
      filename: doc.document_name || doc.filename,
      status: doc.status,
      progress: doc.completion_percentage,
      last_modified: doc.last_modified,
      assignee: doc.assignee
    }))
    const currentIndex = normalizedDocuments.findIndex((doc: DocumentItem) => doc.id === documentId)
    if (currentIndex > 0) {
      const prevDoc = normalizedDocuments[currentIndex - 1]
      handleDocumentChange(prevDoc.id)
    }
  }, [documentsResponse, documentId, handleDocumentChange])

  const handleNextDocument = useCallback(() => {
    const documents = documentsResponse?.data?.documents || []
    const normalizedDocuments = documents.map((doc: any) => ({
      id: doc.document_id || doc.id,
      filename: doc.document_name || doc.filename,
      status: doc.status,
      progress: doc.completion_percentage,
      last_modified: doc.last_modified,
      assignee: doc.assignee
    }))
    const currentIndex = normalizedDocuments.findIndex((doc: DocumentItem) => doc.id === documentId)
    if (currentIndex < normalizedDocuments.length - 1) {
      const nextDoc = normalizedDocuments[currentIndex + 1]
      handleDocumentChange(nextDoc.id)
    }
  }, [documentsResponse, documentId, handleDocumentChange])

  // 获取当前文档和进度信息
  const documents = documentsResponse?.data?.documents || []
  // 适配后端API返回的字段名
  const normalizedDocuments = documents.map((doc: any) => ({
    id: doc.document_id || doc.id,
    filename: doc.document_name || doc.filename,
    status: doc.status,
    progress: doc.completion_percentage,
    last_modified: doc.last_modified,
    assignee: doc.assignee
  }))
  const currentDocument = normalizedDocuments.find((doc: DocumentItem) => doc.id === documentId)
  const currentIndex = normalizedDocuments.findIndex((doc: DocumentItem) => doc.id === documentId)
  const progress = progressResponse?.data as ProgressInfo
  // 适配任务数据结构 - taskResponse.data直接是任务对象
  const task = taskResponse?.data

  // 处理文档内容数据
  useEffect(() => {
    if (contentResponse?.success && contentResponse.data?.content) {
      setDocumentContent(contentResponse.data.content)
    }
  }, [contentResponse])

  // 处理表单配置数据
  useEffect(() => {
    if (formConfigResponse?.success && formConfigResponse.data?.fields) {
      // 转换后端字段格式为前端期望的格式
      const convertedFields: FormFieldType[] = formConfigResponse.data.fields.map((field: any) => {
        // 字段类型映射
        const typeMapping: Record<string, FormFieldType['type']> = {
          'str': 'string',
          'int': 'number',
          'float': 'number',
          'bool': 'boolean',
          'List': 'array',
          'dict': 'object',
          'date': 'date',
          'datetime': 'datetime',
          'time': 'time'
        }

        // 根据约束条件判断是否为文本域
        const isTextArea = field.constraints?.max_length > 100 || 
                          field.description?.includes('文本') || 
                          field.description?.includes('内容')

        const fieldType = field.field_type === 'str' && isTextArea ? 'text' : 
                         typeMapping[field.field_type] || 'string'

        return {
          name: field.path,
          type: fieldType,
          required: field.required || false,
          label: field.path,
          description: field.description,
          placeholder: `请输入${field.description || field.path}`,
          default: field.default_value,
          options: field.options ? field.options.map((opt: any) => ({
            value: opt.value || opt,
            label: opt.label || opt
          })) : undefined,
          validation: {
            max_length: field.constraints?.max_length,
            min_length: field.constraints?.min_length,
            max_value: field.constraints?.le,
            min_value: field.constraints?.ge,
          },
          ui: {
            rows: isTextArea ? 4 : undefined,
          }
        }
      })
      
      setFormFields(convertedFields)
      console.log('转换后的表单字段:', convertedFields)
    }
  }, [formConfigResponse])

  // 处理标注数据
  useEffect(() => {
    if (annotationResponse?.success && annotationResponse.data?.annotated_data) {
      form.setFieldsValue(annotationResponse.data.annotated_data)
      setHasUnsavedChanges(false)
    }
  }, [annotationResponse, form])

  // 清理定时器
  useEffect(() => {
    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }
      if (validationTimerRef.current) {
        clearTimeout(validationTimerRef.current)
      }
    }
  }, [])

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 's':
            e.preventDefault()
            handleSave()
            break
          case 'Enter':
            e.preventDefault()
            handleSubmit()
            break
          case 'ArrowLeft':
            e.preventDefault()
            handlePrevDocument()
            break
          case 'ArrowRight':
            e.preventDefault()
            handleNextDocument()
            break
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleSave, handleSubmit, handlePrevDocument, handleNextDocument])

  // 页面离开前提醒
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault()
        e.returnValue = '您有未保存的更改，确定要离开吗？'
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [hasUnsavedChanges])

  if (taskLoading || documentsLoading || contentLoading || formConfigLoading || annotationLoading) {
    return (
      <div style={{ 
        height: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        flexDirection: 'column'
      }}>
        <Spin size="large" />
        <Text style={{ marginTop: 16, color: '#666' }}>
          正在加载标注工作台...
        </Text>
      </div>
    )
  }

  if (!task || !currentDocument) {
    return (
      <div style={{ padding: '50px' }}>
        <Alert
          message="加载失败"
          description="无法加载任务或文档信息，请检查网络连接或刷新页面重试"
          type="error"
          showIcon
          action={
            <Button size="small" onClick={() => window.location.reload()}>
              刷新页面
            </Button>
          }
        />
      </div>
    )
  }

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部导航栏 */}
      <div style={{ 
        padding: '12px 24px', 
        borderBottom: '1px solid #f0f0f0',
        background: '#fff',
        boxShadow: '0 1px 4px rgba(0,0,0,0.1)'
      }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space size="large">
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate(`/tasks/${taskId}`)}
                type="text"
              >
                返回任务
              </Button>
              <Breadcrumb
                items={[
                  {
                    title: (
                      <span>
                        <FileTextOutlined /> {task.name}
                      </span>
                    )
                  },
                  {
                    title: (
                      <span>
                        <FormOutlined /> {currentDocument.filename}
                      </span>
                    )
                  }
                ]}
              />
            </Space>
          </Col>
          <Col>
            <Space size="large">
              <div style={{ textAlign: 'center' }}>
                <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                  文档进度
                </Text>
                <Text strong>
                  {currentIndex + 1} / {normalizedDocuments.length}
                </Text>
              </div>
              
              {progress && (
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                    任务进度
                  </Text>
                  <Progress 
                    percent={Math.round(progress.progress_percentage)} 
                    size="small" 
                    style={{ width: 120 }}
                    format={(percent) => `${progress.completed_documents}/${progress.total_documents}`}
                  />
                </div>
              )}
              
              <div style={{ textAlign: 'center' }}>
                <Space>
                  {hasUnsavedChanges && (
                    <Tag color="orange" icon={<ExclamationCircleOutlined />}>
                      未保存
                    </Tag>
                  )}
                  {currentDocument.status === 'completed' && (
                    <Tag color="green" icon={<CheckCircleOutlined />}>
                      已完成
                    </Tag>
                  )}
                  {lastSaveTime && (
                    <Tooltip title={`最后保存时间: ${lastSaveTime.toLocaleString()}`}>
                      <Tag icon={<ClockCircleOutlined />}>
                        {lastSaveTime.toLocaleTimeString()}
                      </Tag>
                    </Tooltip>
                  )}
                </Space>
              </div>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 主要内容区域 - 三栏布局 */}
      <Layout style={{ flex: 1 }}>
        {/* 左侧文档列表 */}
        <Sider
          width={300}
          collapsed={siderCollapsed}
          onCollapse={setSiderCollapsed}
          style={{ 
            background: '#fafafa', 
            borderRight: '1px solid #e8e8e8'
          }}
          collapsible
        >
          <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={5} style={{ margin: 0 }}>
                <FileTextOutlined /> 文档列表
              </Title>
              <Button
                type="text"
                size="small"
                icon={<ReloadOutlined />}
                onClick={() => queryClient.invalidateQueries({ queryKey: ['documents', taskId] })}
              />
            </div>
            
            <div style={{ flex: 1, overflow: 'auto' }}>
              <List
                size="small"
                dataSource={normalizedDocuments}
                renderItem={(doc: DocumentItem, index) => (
                  <List.Item
                    style={{
                      cursor: 'pointer',
                      padding: '12px',
                      borderRadius: '8px',
                      marginBottom: '8px',
                      background: doc.id === documentId ? '#e6f7ff' : '#fff',
                      border: doc.id === documentId ? '2px solid #1890ff' : '1px solid #e8e8e8',
                      transition: 'all 0.2s'
                    }}
                    onClick={() => handleDocumentChange(doc.id)}
                  >
                    <List.Item.Meta
                      avatar={
                        <Badge
                          status={
                            doc.status === 'completed' ? 'success' : 
                            doc.status === 'in_progress' ? 'processing' : 'default'
                          }
                          dot
                        />
                      }
                      title={
                        <div>
                          <Text strong={doc.id === documentId} style={{ fontSize: 14 }}>
                            {index + 1}. {doc.filename}
                          </Text>
                          {doc.id === documentId && (
                            <Tag color="blue" style={{ marginLeft: 8 }}>
                              当前
                            </Tag>
                          )}
                        </div>
                      }
                      description={
                        <div>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            {doc.status === 'completed' ? '已完成' : 
                             doc.status === 'in_progress' ? '标注中' : '待标注'}
                          </Text>
                          {doc.progress !== undefined && (
                            <Progress 
                              percent={doc.progress} 
                              size="small" 
                              style={{ marginTop: 4 }}
                              showInfo={false}
                            />
                          )}
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            </div>
          </div>
        </Sider>

        {/* 中间文档内容区域 */}
        <Content style={{ background: '#fff', borderRight: '1px solid #e8e8e8', minWidth: 400 }}>
          <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={5} style={{ margin: 0 }}>
                <EyeOutlined /> 原始文档
              </Title>
              <Space>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {currentDocument.filename}
                </Text>
              </Space>
            </div>
            
            <div style={{ 
              flex: 1, 
              border: '1px solid #d9d9d9', 
              borderRadius: '8px',
              overflow: 'hidden'
            }}>
              <MonacoEditor
                height="100%"
                language="json"
                value={documentContent ? JSON.stringify(documentContent, null, 2) : '{}'}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  fontSize: 13,
                  lineNumbers: 'on',
                  folding: true,
                  wordWrap: 'on',
                  automaticLayout: true,
                  theme: 'vs-light',
                  // 禁用所有可能触发网络请求的功能
                  quickSuggestions: false,
                  suggestOnTriggerCharacters: false,
                  acceptSuggestionOnEnter: 'off',
                  tabCompletion: 'off',
                  wordBasedSuggestions: 'off',
                  parameterHints: { enabled: false },
                  hover: { enabled: false },
                  links: false,
                  colorDecorators: false,
                  codeLens: false,
                  contextmenu: false
                }}
              />
            </div>
          </div>
        </Content>

        {/* 右侧标注表单区域 */}
        <Content style={{ 
          background: '#fff', 
          width: '450px', 
          minWidth: '450px',
          maxWidth: '450px'
        }}>
          <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={5} style={{ margin: 0 }}>
                <FormOutlined /> 标注表单
              </Title>
              <Space>
                <Tooltip title="自动保存">
                  <Switch
                    size="small"
                    checked={autoSaveEnabled}
                    onChange={setAutoSaveEnabled}
                    checkedChildren="自动"
                    unCheckedChildren="手动"
                  />
                </Tooltip>
                {isValidating && (
                  <Spin size="small" />
                )}
              </Space>
            </div>
            
            <div style={{ flex: 1, overflow: 'auto', paddingRight: 8 }}>
              {formFields.length > 0 ? (
                <Form
                  form={form}
                  layout="vertical"
                  onValuesChange={handleFormChange}
                  disabled={currentDocument.status === 'completed'}
                  size="middle"
                >
                  {formFields.map(field => (
                    <FormFieldRenderer 
                      key={field.name}
                      field={field} 
                      form={form}
                      validationErrors={validationErrors}
                      disabled={currentDocument.status === 'completed'}
                    />
                  ))}
                </Form>
              ) : (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '50px 20px',
                  color: '#999'
                }}>
                  <InfoCircleOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                  <Paragraph>
                    暂无表单配置
                  </Paragraph>
                </div>
              )}
            </div>
          </div>
        </Content>
      </Layout>

      {/* 底部操作栏 */}
      <div style={{
        padding: '12px 24px',
        borderTop: '1px solid #e8e8e8',
        background: '#fafafa',
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
            上一个 (Ctrl+←)
          </Button>
          <Button
            icon={<RightOutlined />}
            onClick={handleNextDocument}
            disabled={currentIndex === normalizedDocuments.length - 1}
          >
            下一个 (Ctrl+→)
          </Button>
        </Space>

        <Space>
          <Text type="secondary" style={{ fontSize: 12 }}>
            快捷键: Ctrl+S 保存, Ctrl+Enter 提交
          </Text>
          <Button
            icon={<SaveOutlined />}
            onClick={() => handleSave()}
            loading={saveAnnotationMutation.isPending}
            disabled={currentDocument.status === 'completed'}
          >
            保存 (Ctrl+S)
          </Button>
          <Button
            type="primary"
            icon={<CheckOutlined />}
            onClick={handleSubmit}
            loading={submitAnnotationMutation.isPending}
            disabled={currentDocument.status === 'completed'}
          >
            {currentDocument.status === 'completed' ? '已完成' : '提交 (Ctrl+Enter)'}
          </Button>
        </Space>
      </div>
    </div>
  )
}

export default Annotation 