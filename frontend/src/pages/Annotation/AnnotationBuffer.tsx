import React, { useEffect, useState, useRef, useMemo } from 'react'
import {
  Layout,
  Typography,
  Button,
  List,
  Space,
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
  Row,
  Col,
  Card,
  Divider,
  Progress,
  Tooltip,
  Modal
} from 'antd'
import {
  ArrowLeftOutlined,
  SaveOutlined,
  CheckOutlined,
  LeftOutlined,
  RightOutlined,
  FileTextOutlined,
  FormOutlined,
  EyeOutlined,
  ReloadOutlined,
  EditOutlined,
  InfoCircleOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useAnnotationBufferStore } from '../../stores/annotationBufferStore'
import AnnotationFormRenderer from './components/AnnotationFormRenderer'
import MonacoEditor from '@monaco-editor/react'

const { Title, Text } = Typography
const { Sider, Content } = Layout

// 标注字段接口
interface AnnotationField {
  path: string
  type: string
  required: boolean
  description: string
  constraints: Record<string, any>
  defaultValue?: any
  originalValue?: any
}

// 数据缓冲区接口  
interface DataBuffer {
  documentId: string
  originalData: Record<string, any>
  annotationData: Record<string, any>
  modifiedFields: Set<string>
  validationErrors: Record<string, string[]>
  isValid: boolean
  completionPercentage: number
}

const AnnotationBuffer: React.FC = () => {
  const { taskId, documentId } = useParams<{ taskId: string; documentId: string }>()
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const { message, modal } = App.useApp()
  
  // 状态管理
  const [siderCollapsed, setSiderCollapsed] = useState(false)
  const [localBuffer, setLocalBuffer] = useState<DataBuffer | null>(null)
  const [annotationFields, setAnnotationFields] = useState<AnnotationField[]>([])
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true)
  const isInitializingRef = useRef(false)
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null)
  
  // 使用buffer store
  const {
    documents,
    template,
    currentDocumentId,
    isDirty,
    isLoading,
    loadTaskData,
    setCurrentDocument,
    updateAnnotation,
    saveToBackend,
    getCurrentDocument,
    getAllDocuments
  } = useAnnotationBufferStore()

  // 初始化加载数据
  useEffect(() => {
    if (taskId && taskId !== useAnnotationBufferStore.getState().taskId) {
      loadTaskData(taskId).catch(error => {
        message.error('加载任务数据失败: ' + error.message)
      })
    }
  }, [taskId, loadTaskData, message])

  // 设置当前文档
  useEffect(() => {
    if (documentId && documentId !== currentDocumentId) {
      setCurrentDocument(documentId)
    }
  }, [documentId, currentDocumentId, setCurrentDocument])

  // 获取当前文档数据
  const currentDocument = getCurrentDocument()
  const allDocuments = getAllDocuments()

  // 解析标注字段 - 专门处理 is_annotation: true 的字段
  const parseAnnotationFields = useMemo(() => {
    if (!template?.fields) return []
    
    const fields: AnnotationField[] = []
    
    template.fields.forEach((field: any) => {
      // 只处理标注字段
      if (field.constraints?.is_annotation === true || 
          field.description?.includes('标注') ||
          field.field_type !== 'str' || // 非字符串类型通常需要标注
          field.required) { // 必填字段通常需要标注
        
        fields.push({
          path: field.path,
          type: field.field_type,
          required: field.required || false,
          description: field.description || field.path,
          constraints: field.constraints || {},
          defaultValue: field.default_value,
          originalValue: undefined // 将在初始化buffer时设置
        })
      }
    })
    
    return fields
  }, [template])

  // 从嵌套对象中获取值
  const getNestedValue = (obj: any, path: string): any => {
    if (!obj || !path) return undefined
    return path.split('.').reduce((current, key) => current?.[key], obj)
  }

  // 在嵌套对象中设置值
  const setNestedValue = (obj: any, path: string, value: any): any => {
    if (!path) return obj
    
    const keys = path.split('.')
    const result = { ...obj }
    let current = result
    
    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i]
      if (!current[key] || typeof current[key] !== 'object') {
        current[key] = {}
      } else {
        current[key] = { ...current[key] }
      }
      current = current[key]
    }
    
    current[keys[keys.length - 1]] = value
    return result
  }

  // 初始化本地数据缓冲区
  const initializeBuffer = useMemo(() => {
    if (!currentDocument || !parseAnnotationFields.length) return null

    const originalData = currentDocument.originalContent || {}
    
    // 为标注字段设置原始值
    const fieldsWithOriginalValues = parseAnnotationFields.map(field => ({
      ...field,
      originalValue: getNestedValue(originalData, field.path)
    }))
    
    setAnnotationFields(fieldsWithOriginalValues)
    
    // 使用原文档内容作为标注数据的初始值
    let initialAnnotationData = { ...originalData }
    
    // 检查已有的标注数据，如果存在则覆盖对应字段
    const existingAnnotationData = currentDocument.annotatedContent || {}
    fieldsWithOriginalValues.forEach(field => {
      const existingValue = getNestedValue(existingAnnotationData, field.path)
      if (existingValue !== undefined) {
        initialAnnotationData = setNestedValue(initialAnnotationData, field.path, existingValue)
      }
    })
    
    // 计算完成度
    const filledCount = fieldsWithOriginalValues.filter(field => {
      const value = getNestedValue(initialAnnotationData, field.path)
      return value !== undefined && value !== '' && value !== null
    }).length
    
    const completionPercentage = fieldsWithOriginalValues.length > 0 
      ? (filledCount / fieldsWithOriginalValues.length) * 100 
      : 0

    return {
      documentId: currentDocument.id,
      originalData,
      annotationData: initialAnnotationData,
      modifiedFields: new Set<string>(),
      validationErrors: {},
      isValid: true,
      completionPercentage
    }
  }, [currentDocument, parseAnnotationFields])

  // 更新本地缓冲区
  useEffect(() => {
    if (initializeBuffer) {
      setLocalBuffer(initializeBuffer)
      
      // 初始化表单值 - 为嵌套字段创建正确的表单值结构
      isInitializingRef.current = true
      
      // 为每个标注字段设置表单值
      const formValues: Record<string, any> = {}
      annotationFields.forEach(field => {
        const fieldValue = getNestedValue(initializeBuffer.annotationData, field.path)
        formValues[field.path] = fieldValue
      })
      
      console.log('设置表单值:', formValues)
      form.setFieldsValue(formValues)
      
      setTimeout(() => {
        isInitializingRef.current = false
      }, 0)
    }
  }, [initializeBuffer, form, annotationFields])

  // 验证单个字段
  const validateField = (field: AnnotationField, value: any): string[] => {
    const errors: string[] = []
    
    // 必填验证
    if (field.required && (value === undefined || value === '' || value === null)) {
      errors.push(`${field.path}是必填项`)
    }
    
    // 类型验证
    if (value !== undefined && value !== null && value !== '') {
      const { constraints } = field
      
      if (field.type === 'str' && typeof value === 'string') {
        if (constraints.min_length && value.length < constraints.min_length) {
          errors.push(`${field.path}长度不能少于${constraints.min_length}个字符`)
        }
        if (constraints.max_length && value.length > constraints.max_length) {
          errors.push(`${field.path}长度不能超过${constraints.max_length}个字符`)
        }
      }
      
      if ((field.type === 'int' || field.type === 'float') && typeof value === 'number') {
        if (constraints.ge !== undefined && value < constraints.ge) {
          errors.push(`${field.path}不能小于${constraints.ge}`)
        }
        if (constraints.le !== undefined && value > constraints.le) {
          errors.push(`${field.path}不能大于${constraints.le}`)
        }
      }
    }
    
    return errors
  }

  // 验证所有字段
  const validateAllFields = (data: Record<string, any>): { isValid: boolean, errors: Record<string, string[]> } => {
    const errors: Record<string, string[]> = {}
    
    annotationFields.forEach(field => {
      const value = getNestedValue(data, field.path)
      const fieldErrors = validateField(field, value)
      if (fieldErrors.length > 0) {
        errors[field.path] = fieldErrors
      }
    })
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  // 处理字段变化
  const handleFieldChange = (fieldPath: string, value: any) => {
    if (isInitializingRef.current || !localBuffer) return

    console.log('字段变化:', fieldPath, '新值:', value)

    // 更新缓冲区数据（标注数据即为文档内容）
    const updatedAnnotationData = setNestedValue(localBuffer.annotationData, fieldPath, value)
    
    // 同时更新原始数据，确保文档内容与标注字段保持一致
    const updatedOriginalData = setNestedValue(localBuffer.originalData, fieldPath, value)
    
    // 验证变更字段
    const field = annotationFields.find(f => f.path === fieldPath)
    const fieldErrors = field ? validateField(field, value) : []
    
    // 更新验证错误
    const updatedErrors = { ...localBuffer.validationErrors }
    if (fieldErrors.length > 0) {
      updatedErrors[fieldPath] = fieldErrors
    } else {
      delete updatedErrors[fieldPath]
    }
    
    // 检查是否被修改（与原始文档内容比较）
    const updatedModifiedFields = new Set(localBuffer.modifiedFields)
    const originalValue = field?.originalValue
    if (value !== originalValue) {
      updatedModifiedFields.add(fieldPath)
    } else {
      updatedModifiedFields.delete(fieldPath)
    }
    
    // 计算完成度
    const filledCount = annotationFields.filter(field => {
      const fieldValue = getNestedValue(updatedAnnotationData, field.path)
      return fieldValue !== undefined && fieldValue !== '' && fieldValue !== null
    }).length
    
    const completionPercentage = annotationFields.length > 0 
      ? (filledCount / annotationFields.length) * 100 
      : 0

    // 更新本地缓冲区
    const updatedBuffer: DataBuffer = {
      ...localBuffer,
      originalData: updatedOriginalData,
      annotationData: updatedAnnotationData,
      modifiedFields: updatedModifiedFields,
      validationErrors: updatedErrors,
      isValid: Object.keys(updatedErrors).length === 0,
      completionPercentage
    }
    
    setLocalBuffer(updatedBuffer)
    
    // 同步到全局store，更新文档内容和标注数据
    updateAnnotation(currentDocument!.id, updatedAnnotationData)
    
    console.log('更新后的数据:', {
      originalData: updatedOriginalData,
      annotationData: updatedAnnotationData
    })
    
    // 自动保存
    if (autoSaveEnabled) {
      scheduleAutoSave()
    }
  }

  // 计划自动保存
  const scheduleAutoSave = () => {
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current)
    }
    
    autoSaveTimerRef.current = setTimeout(() => {
      handleSave(true)
    }, 2000) // 2秒后自动保存
  }

  // 保存标注数据
  const handleSave = async (isAutoSave = false) => {
    if (!localBuffer) return
    
    try {
      await saveToBackend()
      if (!isAutoSave) {
        message.success('保存成功')
      }
    } catch (error: any) {
      message.error('保存失败: ' + error.message)
    }
  }

  // 提交标注
  const handleSubmit = async () => {
    if (!localBuffer || !currentDocument) {
      message.error('数据未准备就绪')
      return
    }
    
    try {
      // 验证所有字段
      const validation = validateAllFields(localBuffer.annotationData)
      
      if (!validation.isValid) {
        const errorMessages = Object.entries(validation.errors)
          .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
          .join('; ')
        
        message.error(`表单验证失败: ${errorMessages}`)
        return
      }
      
      // 保存并提交
      await saveToBackend()
      message.success('提交成功')
      
      // 跳转到下一个文档
      const currentIndex = allDocuments.findIndex(doc => doc.id === currentDocument.id)
      if (currentIndex < allDocuments.length - 1) {
        const nextDoc = allDocuments[currentIndex + 1]
        navigate(`/tasks/${taskId}/documents/${nextDoc.id}/annotation-buffer`)
      } else {
        // 如果是最后一个文档，询问是否返回任务列表
        modal.confirm({
          title: '标注完成',
          content: '已完成所有文档的标注，是否返回任务列表？',
          onOk: () => navigate(`/tasks/${taskId}`)
        })
      }
    } catch (error: any) {
      message.error('提交失败: ' + error.message)
    }
  }

  // 切换文档
  const handleDocumentChange = (docId: string) => {
    // 如果有未保存的更改，提示用户
    if (isDirty) {
      modal.confirm({
        title: '有未保存的更改',
        content: '当前文档有未保存的更改，是否保存后切换？',
        onOk: async () => {
          await handleSave()
          navigate(`/tasks/${taskId}/documents/${docId}/annotation-buffer`)
        },
        onCancel: () => {
          navigate(`/tasks/${taskId}/documents/${docId}/annotation-buffer`)
        }
      })
    } else {
      navigate(`/tasks/${taskId}/documents/${docId}/annotation-buffer`)
    }
  }

  // 上一个/下一个文档
  const handlePrevDocument = () => {
    if (currentDocument) {
      const currentIndex = allDocuments.findIndex(doc => doc.id === currentDocument.id)
      if (currentIndex > 0) {
        const prevDoc = allDocuments[currentIndex - 1]
        handleDocumentChange(prevDoc.id)
      }
    }
  }

  const handleNextDocument = () => {
    if (currentDocument) {
      const currentIndex = allDocuments.findIndex(doc => doc.id === currentDocument.id)
      if (currentIndex < allDocuments.length - 1) {
        const nextDoc = allDocuments[currentIndex + 1]
        handleDocumentChange(nextDoc.id)
      }
    }
  }

  // 重置字段到原始值
  const handleResetField = (fieldPath: string) => {
    if (!localBuffer) return
    
    const field = annotationFields.find(f => f.path === fieldPath)
    if (field) {
      handleFieldChange(fieldPath, field.originalValue)
      form.setFieldValue(fieldPath, field.originalValue)
      message.success(`已重置 ${field.path} 到原始值`)
    }
  }
  
  // 重置所有字段到原始值
  const handleResetAllFields = () => {
    if (!localBuffer) return
    
    modal.confirm({
      title: '确认重置',
      content: '确定要将所有字段重置到原始值吗？此操作不可撤销。',
      onOk: () => {
        const resetData = { ...localBuffer.originalData }
        
        // 设置表单值
        form.setFieldsValue(resetData)
        
        // 更新缓冲区
        const updatedBuffer: DataBuffer = {
          ...localBuffer,
          annotationData: resetData,
          modifiedFields: new Set(),
          validationErrors: {},
          isValid: true
        }
        
        setLocalBuffer(updatedBuffer)
        updateAnnotation(currentDocument!.id, resetData)
        message.success('已重置所有字段到原始值')
      }
    })
  }

  // 清理定时器
  useEffect(() => {
    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }
    }
  }, [])

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip="加载任务数据中..." />
      </div>
    )
  }

  if (!currentDocument || !localBuffer) {
    return (
      <div style={{ padding: '20px' }}>
        <Alert message="未找到文档数据或缓冲区未初始化" type="warning" />
      </div>
    )
  }

  const currentIndex = allDocuments.findIndex(doc => doc.id === currentDocument.id)

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 左侧文档列表 */}
      <Sider
        width={300}
        collapsed={siderCollapsed}
        onCollapse={setSiderCollapsed}
        style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}
      >
        <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
          <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={5} style={{ margin: 0 }}>
              <FileTextOutlined /> 文档列表
            </Title>
          </div>
          
          <List
            size="small"
            dataSource={allDocuments}
            renderItem={(doc, index) => (
              <List.Item
                key={doc.id}
                onClick={() => handleDocumentChange(doc.id)}
                style={{
                  cursor: 'pointer',
                  backgroundColor: doc.id === currentDocument.id ? '#e6f7ff' : 'transparent',
                  borderRadius: '4px',
                  padding: '8px',
                  marginBottom: '4px'
                }}
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
                      <Text strong={doc.id === currentDocument.id} style={{ fontSize: 14 }}>
                        {index + 1}. {doc.filename}
                      </Text>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </div>
      </Sider>

      {/* 主内容区域 */}
      <Layout>
        {/* 顶部导航 */}
        <div style={{ background: '#fff', padding: '16px 24px', borderBottom: '1px solid #f0f0f0' }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Space size="large">
                <Button
                  icon={<ArrowLeftOutlined />}
                  onClick={() => navigate(`/tasks/${taskId}`)}
                >
                  返回任务
                </Button>
                <Breadcrumb
                  items={[
                    {
                      title: (
                        <span>
                          <FileTextOutlined /> 任务标注
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
                    {currentIndex + 1} / {allDocuments.length}
                  </Text>
                </div>
                
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                    完成度
                  </Text>
                  <Text strong style={{ color: localBuffer.completionPercentage === 100 ? '#52c41a' : '#1890ff' }}>
                    {localBuffer.completionPercentage.toFixed(1)}%
                  </Text>
                </div>
                
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                    自动保存
                  </Text>
                  <Switch
                    size="small"
                    checked={autoSaveEnabled}
                    onChange={setAutoSaveEnabled}
                  />
                </div>
                
                {(isDirty || localBuffer.modifiedFields.size > 0) && (
                  <div style={{ textAlign: 'center' }}>
                    <Text type="warning" style={{ fontSize: 12, display: 'block' }}>
                      未保存更改
                    </Text>
                    <Text strong style={{ color: '#fa8c16' }}>
                      {localBuffer.modifiedFields.size} 个字段
                    </Text>
                  </div>
                )}
              </Space>
            </Col>
          </Row>
        </div>

        <Content style={{ display: 'flex', height: 'calc(100vh - 80px)' }}>
          {/* 左侧：文档内容显示 */}
          <div style={{ flex: 1, padding: '24px', borderRight: '1px solid #f0f0f0' }}>
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography.Title level={5} style={{ margin: 0 }}>
                  <EyeOutlined /> 原始文档
                </Typography.Title>
                <Space>
                  <Tooltip title="显示标注字段路径">
                    <Button 
                      icon={<InfoCircleOutlined />} 
                      size="small"
                      onClick={() => {
                        modal.info({
                          title: '标注字段信息',
                          content: (
                            <div>
                              <p>当前模板包含 {annotationFields.length} 个标注字段：</p>
                              <ul>
                                {annotationFields.map(field => (
                                  <li key={field.path}>
                                    <strong>{field.path}</strong>: {field.description}
                                    {field.required && <span style={{ color: 'red' }}> *</span>}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          ),
                          width: 600
                        })
                      }}
                    />
                  </Tooltip>
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
                  value={JSON.stringify(currentDocument.originalContent, null, 2)}
                  options={{
                    readOnly: true,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    fontSize: 13,
                    lineNumbers: 'on',
                    folding: true,
                    wordWrap: 'on',
                    automaticLayout: true,
                    theme: 'vs-light'
                  }}
                />
              </div>
            </div>
          </div>

          {/* 右侧：标注表单 */}
          <div style={{ flex: 1, padding: '24px' }}>
            <Card
              title={
                <Space>
                  <span>标注表单</span>
                  <Badge 
                    count={`${annotationFields.filter(f => {
                      const value = getNestedValue(localBuffer.annotationData, f.path)
                      return value !== undefined && value !== '' && value !== null
                    }).length}/${annotationFields.length}`}
                    style={{ backgroundColor: '#52c41a' }}
                  />
                  <Progress 
                    percent={localBuffer.completionPercentage} 
                    size="small" 
                    style={{ width: 60 }}
                    strokeColor={localBuffer.completionPercentage === 100 ? '#52c41a' : '#1890ff'}
                  />
                  {localBuffer.modifiedFields.size > 0 && (
                    <Badge 
                      count={`已修改: ${localBuffer.modifiedFields.size}`}
                      style={{ backgroundColor: '#fa8c16' }}
                    />
                  )}
                  {!localBuffer.isValid && (
                    <Badge 
                      count="有错误" 
                      style={{ backgroundColor: '#ff4d4f' }}
                    />
                  )}
                </Space>
              }
              extra={
                <Space>
                  <Button
                    size="small"
                    icon={<ReloadOutlined />}
                    onClick={handleResetAllFields}
                    disabled={localBuffer.modifiedFields.size === 0}
                  >
                    重置所有
                  </Button>
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
                    disabled={currentIndex === allDocuments.length - 1}
                  >
                    下一个
                  </Button>
                </Space>
              }
              style={{ height: '100%' }}
            >
              <div style={{ height: 'calc(100% - 80px)', overflowY: 'auto' }}>
                {annotationFields.length > 0 && (
                  <AnnotationFormRenderer
                    annotationFields={annotationFields}
                    formData={localBuffer.annotationData}
                    validationErrors={localBuffer.validationErrors}
                    modifiedFields={localBuffer.modifiedFields}
                    form={form}
                    onFieldChange={handleFieldChange}
                    onResetField={handleResetField}
                  />
                )}
              </div>
              
              <Divider />
              
              <div style={{ textAlign: 'right' }}>
                <Space>
                  <Button
                    icon={<SaveOutlined />}
                    onClick={() => handleSave(false)}
                    loading={isLoading}
                    disabled={!isDirty && localBuffer.modifiedFields.size === 0}
                  >
                    保存
                  </Button>
                  <Button
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={handleSubmit}
                    loading={isLoading}
                    disabled={!localBuffer.isValid}
                  >
                    提交
                  </Button>
                </Space>
              </div>
            </Card>
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default AnnotationBuffer