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
  InfoCircleOutlined,
  DownloadOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useAnnotationBufferStore } from '../../stores/annotationBufferStore'
import { annotationAPI } from '../../services/api'
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

  // 从嵌套对象中获取值 - 支持数组路径和复杂结构
  const getNestedValue = (obj: any, path: string): any => {
    if (!obj || !path) return undefined
    
    // 特殊处理：如果文档结构是 {items: [...], type: 'array'}，则从items[0]开始
    let current = obj
    if (obj.items && Array.isArray(obj.items) && obj.items.length > 0 && obj.type === 'array') {
      current = obj.items[0]
    }
    
    // 处理包含数组索引的路径 如: content_sections[].subsections[].analysis.topic
    if (path.includes('[]')) {
      // 找到第一个数组标记
      const firstArrayIndex = path.indexOf('[]')
      const beforeArray = path.substring(0, firstArrayIndex) // content_sections
      const afterArray = path.substring(firstArrayIndex + 2) // .subsections[].analysis.topic
      
      // 获取到数组
      const arrayKeys = beforeArray.split('.')
      for (const key of arrayKeys) {
        if (current && typeof current === 'object' && key in current) {
          current = current[key]
        } else {
          return undefined
        }
      }
      
      // 如果是数组，取第一个元素
      if (Array.isArray(current) && current.length > 0) {
        current = current[0]
        
        // 处理剩余路径（去掉开头的点号）
        let remainingPath = afterArray
        if (remainingPath && remainingPath.startsWith('.')) {
          remainingPath = remainingPath.substring(1)
        }
        
        if (remainingPath) {
          // 递归处理剩余路径（可能还有嵌套数组）
          return getNestedValue(current, remainingPath)
        } else {
          return current
        }
      } else {
        return undefined
      }
    } else {
      // 普通路径处理
      const keys = path.split('.')
      for (const key of keys) {
        if (current && typeof current === 'object' && key in current) {
          current = current[key]
        } else {
          return undefined
        }
      }
      return current
    }
  }

  // 在嵌套对象中设置值 - 支持数组路径和复杂结构
  const setNestedValue = (obj: any, path: string, value: any): any => {
    if (!path) return obj
    
    // 深拷贝对象
    const result = JSON.parse(JSON.stringify(obj))
    
    // 特殊处理：如果文档结构是 {items: [...], type: 'array'}，则在items[0]中设置
    let current = result
    let isItemsStructure = false
    if (result.items && Array.isArray(result.items) && result.items.length > 0 && result.type === 'array') {
      current = result.items[0]
      isItemsStructure = true
    }
    
    // 处理包含数组索引的路径
    if (path.includes('[]')) {
      // 找到第一个数组标记
      const firstArrayIndex = path.indexOf('[]')
      const beforeArray = path.substring(0, firstArrayIndex) // content_sections
      const afterArray = path.substring(firstArrayIndex + 2) // .subsections[].analysis.topic
      
      // 获取到数组
      const arrayKeys = beforeArray.split('.')
      for (let i = 0; i < arrayKeys.length - 1; i++) {
        const key = arrayKeys[i]
        if (!current[key] || typeof current[key] !== 'object') {
          current[key] = {}
        }
        current = current[key]
      }
      
      // 最后一个key应该是数组
      const lastArrayKey = arrayKeys[arrayKeys.length - 1]
      if (!current[lastArrayKey] || !Array.isArray(current[lastArrayKey])) {
        current[lastArrayKey] = [{}] // 确保至少有一个数组元素
      }
      
      // 在数组的第一个元素中设置值
      let arrayElement = current[lastArrayKey][0]
      if (!arrayElement || typeof arrayElement !== 'object') {
        arrayElement = current[lastArrayKey][0] = {}
      }
      
      // 处理剩余路径
      let remainingPath = afterArray
      if (remainingPath && remainingPath.startsWith('.')) {
        remainingPath = remainingPath.substring(1)
      }
      
      if (remainingPath) {
        // 递归处理剩余路径
        const updatedElement = setNestedValue(arrayElement, remainingPath, value)
        current[lastArrayKey][0] = updatedElement
      } else {
        current[lastArrayKey][0] = value
      }
    } else {
      // 普通路径处理
      const keys = path.split('.')
      
      // 创建嵌套结构
      for (let i = 0; i < keys.length - 1; i++) {
        const key = keys[i]
        if (!current[key] || typeof current[key] !== 'object') {
          current[key] = {}
        }
        current = current[key]
      }
      
      // 设置最终值
      current[keys[keys.length - 1]] = value
    }
    
    return result
  }

  // 初始化本地数据缓冲区
  const initializeBuffer = useMemo(() => {
    if (!currentDocument || !parseAnnotationFields.length) return null

    const originalData = currentDocument.originalContent || {}
    const existingAnnotationData = currentDocument.annotatedContent || {}
    
    // 为标注字段设置原始值
    const fieldsWithOriginalValues = parseAnnotationFields.map(field => ({
      ...field,
      originalValue: getNestedValue(originalData, field.path)
    }))
    
    setAnnotationFields(fieldsWithOriginalValues)
    
    // 使用原文档内容作为标注数据的初始值
    let initialAnnotationData = { ...originalData }
    
    // 检查已有的标注数据，如果存在则覆盖对应字段
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

  // 处理字段变化 - 添加null检查
  const handleFieldChange = (fieldPath: string, value: any) => {
    if (!localBuffer) return
    
    const updatedAnnotationData = setNestedValue(localBuffer.annotationData, fieldPath, value)
    
    // 同时更新原始数据以保持同步
    const updatedOriginalData = setNestedValue(localBuffer.originalData, fieldPath, value)
    
    // 验证字段
    const field = annotationFields.find(f => f.path === fieldPath)
    const fieldErrors = field ? validateField(field, value) : []
    
    const updatedErrors = { ...localBuffer.validationErrors }
    if (fieldErrors.length > 0) {
      updatedErrors[fieldPath] = fieldErrors
    } else {
      delete updatedErrors[fieldPath]
    }
    
    // 记录修改的字段
    const updatedModifiedFields = new Set(localBuffer.modifiedFields)
    updatedModifiedFields.add(fieldPath)
    
    // 计算完成度
    const { isValid } = validateAllFields(updatedAnnotationData)
    const completionPercentage = calculateCompletion(updatedAnnotationData)
    
    // 更新本地缓冲区
    setLocalBuffer({
      ...localBuffer,
      annotationData: updatedAnnotationData,
      originalData: updatedOriginalData,
      validationErrors: updatedErrors,
      modifiedFields: updatedModifiedFields,
      isValid,
      completionPercentage
    })
    
    // 立即更新store
    updateAnnotation(localBuffer.documentId, updatedAnnotationData)
    
    // 触发表单更新
    const formValue = getFormValue(value, field)
    form.setFieldValue(fieldPath, formValue)
    
    // 自动保存
    if (autoSaveEnabled) {
      scheduleAutoSave()
    }
  }

  // 自动保存调度 - 添加null检查
  const scheduleAutoSave = () => {
    if (!localBuffer) return
    
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current)
    }
    autoSaveTimerRef.current = setTimeout(() => {
      handleSave(true) // 自动保存
    }, 3000) // 3秒后自动保存
  }

  // 计算完成度
  const calculateCompletion = (data: Record<string, any>): number => {
    const filledCount = annotationFields.filter(field => {
      const fieldValue = getNestedValue(data, field.path)
      return fieldValue !== undefined && fieldValue !== '' && fieldValue !== null
    }).length
    
    return annotationFields.length > 0 ? (filledCount / annotationFields.length) * 100 : 0
  }

  // 获取表单值（根据字段类型转换）
  const getFormValue = (value: any, field: AnnotationField | undefined): any => {
    if (!field) return value
    
    switch (field.type) {
      case 'boolean':
        return Boolean(value)
      case 'number':
        return Number(value) || 0
      case 'array':
        return Array.isArray(value) ? value : []
      case 'object':
        return typeof value === 'object' ? value : {}
      default:
        return String(value || '')
    }
  }

  // 获取当前文档在列表中的索引
  const currentIndex = allDocuments.findIndex(doc => doc.id === currentDocument?.id)

  // 保存数据到后端 - 添加null检查
  const handleSave = async (isAutoSave = false) => {
    if (!localBuffer) return
    
    try {
      await saveToBackend()
      
      if (!isAutoSave) {
        message.success('保存成功')
      }
    } catch (error: any) {
      console.error('保存失败:', error)
      message.error('保存失败: ' + error.message)
    }
  }

  // 导出文件
  const handleExportFile = async () => {
    if (!localBuffer || !currentDocument) return
    
    try {
      // 创建导出的数据结构
      const exportData = {
        document_id: currentDocument.id,
        document_filename: currentDocument.filename,
        export_time: new Date().toISOString(),
        annotation_data: localBuffer.annotationData,
        completion_percentage: localBuffer.completionPercentage,
        modified_fields: Array.from(localBuffer.modifiedFields),
        validation_status: {
          is_valid: localBuffer.isValid,
          errors: localBuffer.validationErrors
        }
      }
      
      // 创建下载链接
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
        type: 'application/json' 
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `annotation_${currentDocument.id}_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      message.success('文件导出成功')
    } catch (error: any) {
      message.error('导出失败: ' + error.message)
    }
  }

  // 提交完成标注 - 添加null检查
  const handleSubmit = async () => {
    if (!localBuffer) return
    
    try {
      // 最终验证
      const validation = validateAllFields(localBuffer.annotationData)
      if (!validation.isValid) {
        message.error('存在验证错误，请修正后再提交')
        return
      }

      // 先保存，再提交
      await handleSave()
      
      // 调用提交API
      const submitData = {
        annotation_data: localBuffer.annotationData
      }
      
      const submitResult = await annotationAPI.submitAnnotation(taskId!, documentId!, submitData)
      
      if (submitResult.success) {
        message.success('标注提交成功！')
        
        // 重新加载任务数据以刷新文档状态
        await loadTaskData(taskId!)
        
        // 跳转到下一个文档或返回任务列表
        const currentIndex = allDocuments.findIndex(doc => doc.id === documentId)
        if (currentIndex < allDocuments.length - 1) {
          handleNextDocument()
        } else {
          navigate(`/tasks/${taskId}`)
        }
      } else {
        message.error('提交失败: ' + submitResult.message)
      }
    } catch (error: any) {
      console.error('提交失败:', error)
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

  // 重置字段 - 添加null检查
  const handleResetField = (fieldPath: string) => {
    if (!localBuffer) return
    
    const field = annotationFields.find(f => f.path === fieldPath)
    const originalValue = field?.originalValue || field?.defaultValue

    handleFieldChange(fieldPath, originalValue)
  }
  
  // 重置所有字段 - 添加null检查
  const handleResetAllFields = () => {
    if (!localBuffer) return
    
    const resetData = { ...localBuffer.originalData }
    
    setLocalBuffer({
      ...localBuffer,
      annotationData: resetData,
      modifiedFields: new Set(),
      validationErrors: {},
      isValid: true,
      completionPercentage: calculateCompletion(resetData)
    })
    
    // 重置表单
    const formData: Record<string, any> = {}
    annotationFields.forEach(field => {
      const originalValue = field.originalValue || field.defaultValue
      if (originalValue !== undefined) {
        formData[field.path] = getFormValue(originalValue, field)
      }
    })
    form.setFieldsValue(formData)
    
    message.success('已重置所有字段')
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
                  <Text strong style={{ color: localBuffer?.completionPercentage === 100 ? '#52c41a' : '#1890ff' }}>
                    {localBuffer?.completionPercentage?.toFixed(1)}%
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
                
                {(isDirty || (localBuffer?.modifiedFields?.size ?? 0) > 0) && (
                  <div style={{ textAlign: 'center' }}>
                    <Text type="warning" style={{ fontSize: 12, display: 'block' }}>
                      未保存更改
                    </Text>
                    <Text strong style={{ color: '#fa8c16' }}>
                      {localBuffer?.modifiedFields?.size ?? 0} 个字段
                    </Text>
                  </div>
                )}

                {/* 快速保存按钮组 */}
                <div style={{ marginLeft: '20px', borderLeft: '1px solid #f0f0f0', paddingLeft: '20px' }}>
                  <Space>
                    <Tooltip title="立即保存到后端">
                      <Button
                        type={(isDirty || (localBuffer?.modifiedFields?.size ?? 0) > 0) ? "primary" : "default"}
                        icon={<SaveOutlined />}
                        onClick={() => handleSave(false)}
                        loading={isLoading}
                        disabled={!isDirty && (localBuffer?.modifiedFields?.size ?? 0) === 0}
                        style={{
                          background: (isDirty || (localBuffer?.modifiedFields?.size ?? 0) > 0) ? '#52c41a' : undefined,
                          borderColor: (isDirty || (localBuffer?.modifiedFields?.size ?? 0) > 0) ? '#52c41a' : undefined
                        }}
                      >
                        {(isDirty || (localBuffer?.modifiedFields?.size ?? 0) > 0) ? '保存更改' : '已保存'}
                      </Button>
                    </Tooltip>
                    
                    <Tooltip title="导出标注数据为JSON文件">
                      <Button
                        icon={<DownloadOutlined />}
                        onClick={handleExportFile}
                        disabled={!localBuffer}
                      >
                        导出
                      </Button>
                    </Tooltip>
                  </Space>
                </div>
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
                  <EyeOutlined /> 当前标注内容
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
                  value={JSON.stringify(localBuffer?.annotationData || currentDocument.originalContent, null, 2)}
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
          <div style={{ flex: 1, padding: '24px', display: 'flex', flexDirection: 'column' }}>
            <Card
              title={
                <Space>
                  <span>标注表单</span>
                  <Badge 
                    count={`${annotationFields.filter(f => {
                      const value = getNestedValue(localBuffer?.annotationData, f.path)
                      return value !== undefined && value !== '' && value !== null
                    }).length}/${annotationFields.length}`}
                    style={{ backgroundColor: '#52c41a' }}
                  />
                  <Progress 
                    percent={localBuffer?.completionPercentage ?? 0} 
                    size="small" 
                    style={{ width: 60 }}
                    strokeColor={localBuffer?.completionPercentage === 100 ? '#52c41a' : '#1890ff'}
                  />
                  {(localBuffer?.modifiedFields?.size ?? 0) > 0 && (
                    <Badge 
                      count={`已修改: ${localBuffer?.modifiedFields?.size ?? 0}`}
                      style={{ backgroundColor: '#fa8c16' }}
                    />
                  )}
                  {!localBuffer?.isValid && (
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
                    disabled={(localBuffer?.modifiedFields?.size ?? 0) === 0}
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
              style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
              bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '16px' }}
            >
              {/* 表单内容区域 - 可滚动 */}
              <div style={{ 
                flex: 1, 
                overflowY: 'auto', 
                paddingRight: '8px',
                marginBottom: '16px',
                maxHeight: 'calc(100vh - 320px)' // 确保不超出视口
              }}>
                {annotationFields.length > 0 && (
                  <AnnotationFormRenderer
                    annotationFields={annotationFields}
                    formData={localBuffer?.annotationData ?? {}}
                    validationErrors={localBuffer?.validationErrors ?? {}}
                    modifiedFields={localBuffer?.modifiedFields ?? new Set()}
                    form={form}
                    onFieldChange={handleFieldChange}
                    onResetField={handleResetField}
                  />
                )}
              </div>
              
              {/* 底部按钮区域 - 固定 */}
              <div style={{ 
                borderTop: '1px solid #f0f0f0',
                paddingTop: '16px',
                textAlign: 'right',
                backgroundColor: '#fff'
              }}>
                <Space>
                  <Button
                    icon={<SaveOutlined />}
                    onClick={() => handleSave(false)}
                    loading={isLoading}
                    disabled={!isDirty && (localBuffer?.modifiedFields?.size ?? 0) === 0}
                  >
                    快速保存
                  </Button>
                  <Button
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={handleSubmit}
                    loading={isLoading}
                    disabled={!localBuffer?.isValid}
                  >
                    完成并提交
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