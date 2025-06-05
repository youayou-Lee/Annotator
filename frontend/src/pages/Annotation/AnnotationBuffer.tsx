import React, { useEffect, useState, useRef, useMemo } from 'react'
import {
  Layout,
  Typography,
  Button,
  List,
  Space,
  Form,
  InputNumber,
  App,
  Spin,
  Breadcrumb,
  Badge,
  Row,
  Col,
  Card,
  Progress,
  Tooltip
} from 'antd'
import {
  ArrowLeftOutlined,
  SaveOutlined,
  CheckOutlined,
  LeftOutlined,
  RightOutlined,
  FileTextOutlined,
  EyeOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
  DownloadOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useAnnotationBufferStore } from '../../stores/annotationBufferStore'
import { useTaskStore } from '../../stores/taskStore'
import { annotationAPI } from '../../services/api'
import AnnotationFormRenderer from './components/AnnotationFormRenderer'
import MonacoEditor from '@monaco-editor/react'

const { Text } = Typography
const { Sider, Content } = Layout

// 文档数据接口
interface DocumentData {
  id: string
  filename: string
  originalContent: any
  annotatedContent: any
  status: 'pending' | 'in_progress' | 'completed'
}

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

// 单个JSON对象的数据缓冲区
interface ObjectBuffer {
  index: number
  originalData: Record<string, any>
  annotationData: Record<string, any>
  modifiedFields: Set<string>
  validationErrors: Record<string, string[]>
  isValid: boolean
  completionPercentage: number
}

// 整个文档的数据缓冲区
interface DocumentBuffer {
  documentId: string
  objectsCount: number
  currentObjectIndex: number
  objects: ObjectBuffer[]
}

const AnnotationBuffer: React.FC = () => {
  const { taskId, documentId } = useParams<{ taskId: string; documentId: string }>()
  const navigate = useNavigate()
  const { message, modal } = App.useApp()

  // 状态管理
  const [isLoading, setIsLoading] = useState(false)
  const [annotationFields, setAnnotationFields] = useState<AnnotationField[]>([])
  const [documentBuffer, setDocumentBuffer] = useState<DocumentBuffer | null>(null)
  const [currentObjectIndex, setCurrentObjectIndex] = useState(0)
  
  // 单个表单实例 - 在对象切换时重置数据
  const [form] = Form.useForm()
  const isInitializingRef = useRef(false)
  const fieldChangeTimeoutRef = useRef<Record<string, NodeJS.Timeout>>({})

  // Store hooks
  const {
    template,
    loadTaskData,
    setCurrentDocument,
    updateAnnotation,
    getCurrentDocument,
    getAllDocuments
  } = useAnnotationBufferStore()

  const { currentTask } = useTaskStore()

  // 获取当前文档和所有文档
  const currentDocument = getCurrentDocument()
  const allDocuments = getAllDocuments()

  // 初始化数据
  useEffect(() => {
    if (taskId && documentId) {
      setIsLoading(true)
      loadTaskData(taskId)
        .then(() => {
          setCurrentDocument(documentId)
        })
        .finally(() => {
          setIsLoading(false)
        })
    }
  }, [taskId, documentId, loadTaskData, setCurrentDocument])

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
    
    const keys = path.split('.')
    let current = obj
    for (const key of keys) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key]
      } else {
        return undefined
      }
    }
    return current
  }

  // 在嵌套对象中设置值
  const setNestedValue = (obj: any, path: string, value: any): any => {
    if (!path) return obj
    
    // 深拷贝对象
    const result = JSON.parse(JSON.stringify(obj))
    const keys = path.split('.')
    let current = result
    
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
    return result
  }

  // 检测文档是否包含多个JSON对象
  const parseDocumentObjects = useMemo(() => {
    if (!currentDocument?.originalContent) return []
    
    const content = currentDocument.originalContent
    
    // 检查是否为数组格式
    if (Array.isArray(content)) {
      return content
    }
    
    // 检查是否为 {items: [...]} 格式
    if (content.items && Array.isArray(content.items)) {
      return content.items
    }
    
    // 单个对象
    return [content]
  }, [currentDocument])

  // 初始化文档缓冲区
  const initializeDocumentBuffer = useMemo(() => {
    if (!currentDocument || !parseAnnotationFields.length || !parseDocumentObjects.length) return null

    const objectBuffers: ObjectBuffer[] = parseDocumentObjects.map((objData: any, index: number) => {
      // 为标注字段设置原始值
      const fieldsWithOriginalValues = parseAnnotationFields.map(field => ({
        ...field,
        originalValue: getNestedValue(objData, field.path)
      }))
      
      // 使用原对象数据作为标注数据的初始值
      let initialAnnotationData = { ...objData }
      
      // 检查已有的标注数据
      const existingAnnotationData = currentDocument.annotatedContent || {}
      let existingObjectData = {}
      
      // 如果已有标注数据是数组，取对应索引的数据
      if (Array.isArray(existingAnnotationData)) {
        existingObjectData = existingAnnotationData[index] || {}
      } else if (existingAnnotationData.items && Array.isArray(existingAnnotationData.items)) {
        existingObjectData = existingAnnotationData.items[index] || {}
      } else if (index === 0) {
        // 如果是单对象且是第一个索引，使用整个已有数据
        existingObjectData = existingAnnotationData
      }
      
      // 如果存在已有标注数据，覆盖对应字段
      fieldsWithOriginalValues.forEach(field => {
        const existingValue = getNestedValue(existingObjectData, field.path)
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
        index,
        originalData: objData,
        annotationData: initialAnnotationData,
        modifiedFields: new Set<string>(),
        validationErrors: {},
        isValid: true,
        completionPercentage
      }
    })

    return {
      documentId: currentDocument.id,
      objectsCount: parseDocumentObjects.length,
      currentObjectIndex: 0,
      objects: objectBuffers
    }
  }, [currentDocument, parseAnnotationFields, parseDocumentObjects])

  // 更新文档缓冲区
  useEffect(() => {
    if (initializeDocumentBuffer) {
      setDocumentBuffer(initializeDocumentBuffer)
      setAnnotationFields(parseAnnotationFields.map(field => ({
        ...field,
        originalValue: undefined // 会在切换对象时动态设置
      })))
      
      // 初始化第一个对象的表单数据
      isInitializingRef.current = true
      
      if (initializeDocumentBuffer.objects.length > 0) {
        const firstObject = initializeDocumentBuffer.objects[0]
        
        // 设置标注字段的原始值
        const updatedFields = parseAnnotationFields.map(field => ({
          ...field,
          originalValue: getNestedValue(firstObject.originalData, field.path)
        }))
        setAnnotationFields(updatedFields)
        
        // 由于表单组件现在使用本地状态，只需要等待一下让组件重新渲染
        setTimeout(() => {
          isInitializingRef.current = false
        }, 100)
      } else {
        isInitializingRef.current = false
      }
    }
  }, [initializeDocumentBuffer, parseAnnotationFields, form])

  // 组件卸载时清理定时器
  useEffect(() => {
    return () => {
      Object.values(fieldChangeTimeoutRef.current).forEach(timeout => {
        if (timeout) clearTimeout(timeout)
      })
      fieldChangeTimeoutRef.current = {}
    }
  }, [])

  // 获取当前对象缓冲区
  const currentObjectBuffer = useMemo(() => {
    return documentBuffer?.objects[currentObjectIndex] || null
  }, [documentBuffer, currentObjectIndex])

  // 验证单个字段 - 简化为只检查必填项
  const validateField = (field: AnnotationField, value: any): string[] => {
    const errors: string[] = []
    
    // 只进行必填验证，其他复杂校验留给后端
    if (field.required && (value === undefined || value === '' || value === null)) {
      errors.push(`${field.path}是必填项`)
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

  // 处理字段变更
  const handleFieldChange = (fieldPath: string, value: any) => {
    if (!documentBuffer || !currentObjectBuffer || isInitializingRef.current) return
    
    // 清除之前的防抖定时器
    if (fieldChangeTimeoutRef.current[fieldPath]) {
      clearTimeout(fieldChangeTimeoutRef.current[fieldPath])
    }
    
    // 设置新的防抖定时器，只更新本地状态，不触发保存
    fieldChangeTimeoutRef.current[fieldPath] = setTimeout(() => {
      const objectIndex = currentObjectIndex
      const updatedBuffer = { ...documentBuffer }
      const objectBuffer = { ...updatedBuffer.objects[objectIndex] }
      
      // 更新标注数据
      const updatedAnnotationData = setNestedValue(objectBuffer.annotationData, fieldPath, value)
      
      // 验证字段
      const field = annotationFields.find(f => f.path === fieldPath)
      const fieldErrors = field ? validateField(field, value) : []
      
      // 更新验证错误
      const updatedErrors = { ...objectBuffer.validationErrors }
      if (fieldErrors.length > 0) {
        updatedErrors[fieldPath] = fieldErrors
      } else {
        delete updatedErrors[fieldPath]
      }
      
      // 更新修改字段集合
      const updatedModifiedFields = new Set(objectBuffer.modifiedFields)
      const originalValue = getNestedValue(objectBuffer.originalData, fieldPath)
      if (JSON.stringify(value) !== JSON.stringify(originalValue)) {
        updatedModifiedFields.add(fieldPath)
      } else {
        updatedModifiedFields.delete(fieldPath)
      }
      
      // 计算完成度
      const { isValid } = validateAllFields(updatedAnnotationData)
      const completionPercentage = calculateCompletion(updatedAnnotationData)
      
      // 更新对象缓冲区
      objectBuffer.annotationData = updatedAnnotationData
      objectBuffer.validationErrors = updatedErrors
      objectBuffer.modifiedFields = updatedModifiedFields
      objectBuffer.isValid = isValid
      objectBuffer.completionPercentage = completionPercentage
      
      updatedBuffer.objects[objectIndex] = objectBuffer
      setDocumentBuffer(updatedBuffer)
      
      // 只更新本地状态，不调用 updateAnnotation 进行自动保存
      
      // 清除该字段的防抖定时器
      delete fieldChangeTimeoutRef.current[fieldPath]
    }, 150) // 150ms 防抖延迟
  }

  // 构造完整的标注数据
  const constructCompleteAnnotationData = (buffer: DocumentBuffer): any => {
    if (buffer.objectsCount === 1) {
      // 单个对象，直接返回该对象的标注数据
      return buffer.objects[0].annotationData
    } else {
      // 多个对象，根据原始文档结构返回
      const allAnnotationData = buffer.objects.map(obj => obj.annotationData)
      
      // 如果原始文档有items结构，保持该结构
      if (currentDocument?.originalContent?.items) {
        return {
          ...currentDocument.originalContent,
          items: allAnnotationData
        }
      } else {
        // 否则返回数组
        return allAnnotationData
      }
    }
  }

  // 计算完成度
  const calculateCompletion = (data: Record<string, any>): number => {
    const filledCount = annotationFields.filter(field => {
      const fieldValue = getNestedValue(data, field.path)
      return fieldValue !== undefined && fieldValue !== '' && fieldValue !== null
    }).length
    
    return annotationFields.length > 0 ? (filledCount / annotationFields.length) * 100 : 0
  }

  // 获取当前文档在列表中的索引
  const currentDocumentIndex = allDocuments.findIndex((doc: DocumentData) => doc.id === currentDocument?.id)

  // 是否有未保存的更改
  const isDirty = useMemo(() => {
    return documentBuffer?.objects.some(obj => obj.modifiedFields.size > 0) || false
  }, [documentBuffer])

  // 获取提交按钮的文本和提示
  const getSubmitButtonInfo = useMemo(() => {
    if (!documentBuffer) {
      return {
        text: '完成并提交',
        tooltip: '正在加载...',
        disabled: true
      }
    }
    
    const invalidObjects = documentBuffer.objects.filter(obj => !obj.isValid)
    
    if (invalidObjects.length > 0) {
      return {
        text: '存在校验错误',
        tooltip: `第 ${invalidObjects.map(obj => obj.index + 1).join(', ')} 个对象存在校验错误，请修正后再提交`,
        disabled: true
      }
    }
    
    if (isDirty) {
      return {
        text: '保存并提交',
        tooltip: '检测到未保存的修改，点击将先进行数据校验，通过后自动提交',
        disabled: false
      }
    }
    
    return {
      text: '完成并提交',
      tooltip: '所有数据已保存且通过校验，可以提交',
      disabled: false
    }
  }, [documentBuffer, isDirty])

  // 保存数据到后端
  const handleSave = async () => {
    if (!documentBuffer) return
    
    try {
      const completeAnnotationData = constructCompleteAnnotationData(documentBuffer)
      
      const saveData = {
        annotation_data: completeAnnotationData
      }
      
      const result = await annotationAPI.saveAnnotation(taskId!, documentId!, saveData)
      
      if (result.success) {
        // 更新store中的标注数据
        updateAnnotation(documentBuffer.documentId, completeAnnotationData)
        
        // 如果保存成功，清除所有校验错误和修改标记
        const updatedBuffer = { ...documentBuffer }
        updatedBuffer.objects.forEach(obj => {
          obj.modifiedFields.clear()
          obj.validationErrors = {} // 清除前端校验错误
          obj.isValid = true // 后端验证通过，标记为有效
        })
        setDocumentBuffer(updatedBuffer)
        
        message.success('保存成功')
      } else {
        // API返回了失败状态，检查是否有详细的错误信息
        console.log('[DEBUG] API返回失败:', result)
        
        let validationErrors: Record<string, any> | null = null
        let errorMessage = result.message || '保存失败'
        
        // 检查是否有详细的错误信息
        if (result.detail) {
          console.log('[DEBUG] API返回的错误详情:', result.detail)
          
          // 处理复杂的校验错误对象
          if (result.detail.error_details) {
            validationErrors = {}
            const errorDetails = result.detail.error_details || []
            
            errorDetails.forEach((errorItem: any) => {
              const field = errorItem.field || 'unknown'
              const message = errorItem.message || errorItem.original_message || errorItem.type || '校验失败'
              
              if (!validationErrors![field]) {
                validationErrors![field] = []
              }
              
              // 为用户提供详细信息
              let displayMessage = message
              if (errorItem.input !== undefined && errorItem.input !== null) {
                displayMessage += ` (当前输入: ${errorItem.input})`
              }
              if (errorItem.type && errorItem.type !== message) {
                displayMessage += ` [类型: ${errorItem.type}]`
              }
              
              validationErrors![field].push(displayMessage)
              console.log(`[DEBUG] 字段错误 - ${field}: ${displayMessage}`)
            })
          }
        }
        
        if (validationErrors && Object.keys(validationErrors).length > 0) {
          // 处理后端返回的校验错误
          const updatedBuffer = { ...documentBuffer }
          
          // 清除所有对象的现有校验错误
          updatedBuffer.objects.forEach(obj => {
            obj.validationErrors = {}
            obj.isValid = true
          })
          
          // 应用后端校验错误
          Object.entries(validationErrors).forEach(([path, errors]) => {
            const errorArray = Array.isArray(errors) ? errors : [errors]
            
            // 判断错误属于哪个对象（如果是多对象情况）
            if (updatedBuffer.objectsCount === 1) {
              updatedBuffer.objects[0].validationErrors[path] = errorArray
              updatedBuffer.objects[0].isValid = false
            } else {
              // 多对象情况，需要根据路径判断属于哪个对象
              updatedBuffer.objects.forEach(obj => {
                obj.validationErrors[path] = errorArray
                obj.isValid = false
              })
            }
          })
          
          setDocumentBuffer(updatedBuffer)
          
          // 显示详细的校验错误信息
          const errorFieldsCount = Object.keys(validationErrors).length
          const totalErrorsCount = Object.values(validationErrors).flat().length
          
          message.error({
            content: `${errorMessage}（${errorFieldsCount} 个字段，共 ${totalErrorsCount} 个错误）`,
            duration: 5
          })
          
          // 自动滚动到第一个有错误的字段
          setTimeout(() => {
            const firstErrorField = Object.keys(validationErrors!)[0]
            if (firstErrorField) {
              const errorElement = document.querySelector(`[data-field-path="${firstErrorField}"]`)
              if (errorElement) {
                errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
              }
            }
          }, 100)
          
        } else {
          // 非校验错误
          message.error({
            content: errorMessage,
            duration: 4
          })
        }
      }
    } catch (error: any) {
      // 这里处理网络错误或其他意外错误
      console.error('保存过程中发生异常:', error)
      message.error({
        content: '保存过程中发生异常: ' + (error.message || String(error)),
        duration: 4
      })
    }
  }

  // 导出文件
  const handleExportFile = async () => {
    if (!documentBuffer || !currentDocument) return
    
    try {
      // 创建导出的数据结构
      const exportData = {
        document_id: currentDocument.id,
        document_filename: currentDocument.filename,
        export_time: new Date().toISOString(),
        objects_count: documentBuffer.objectsCount,
        annotation_data: constructCompleteAnnotationData(documentBuffer),
        objects_status: documentBuffer.objects.map((obj, index) => ({
          index,
          completion_percentage: obj.completionPercentage,
          modified_fields: Array.from(obj.modifiedFields),
          validation_status: {
            is_valid: obj.isValid,
            errors: obj.validationErrors
          }
        }))
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

  // 提交完成标注
  const handleSubmit = async () => {
    if (!documentBuffer) return
    
    try {
      // 先进行前端基础校验
      const invalidObjects = documentBuffer.objects.filter(obj => !obj.isValid)
      if (invalidObjects.length > 0) {
        message.error(`第 ${invalidObjects.map(obj => obj.index + 1).join(', ')} 个对象存在验证错误，请修正后再提交`)
        return
      }

      // 如果有未保存的修改，必须先保存并通过后端校验
      if (isDirty) {
        message.info('检测到未保存的修改，正在进行数据校验...')
        
        // 先保存，这会触发后端校验
        const completeAnnotationData = constructCompleteAnnotationData(documentBuffer)
        
        const saveData = {
          annotation_data: completeAnnotationData
        }
        
        const saveResult = await annotationAPI.saveAnnotation(taskId!, documentId!, saveData)
        
        if (!saveResult.success) {
          // 保存失败，说明有校验错误，阻止提交
          message.error('数据校验失败，请修正错误后再提交')
          
          // 处理校验错误显示（复用现有逻辑）
          let validationErrors: Record<string, any> | null = null
          
          if (saveResult.detail && saveResult.detail.error_details) {
            validationErrors = {}
            const errorDetails = saveResult.detail.error_details || []
            
            errorDetails.forEach((errorItem: any) => {
              const field = errorItem.field || 'unknown'
              const message = errorItem.message || errorItem.original_message || errorItem.type || '校验失败'
              
              if (!validationErrors![field]) {
                validationErrors![field] = []
              }
              
              let displayMessage = message
              if (errorItem.input !== undefined && errorItem.input !== null) {
                displayMessage += ` (当前输入: ${errorItem.input})`
              }
              
              validationErrors![field].push(displayMessage)
            })
            
            // 更新缓冲区的校验错误状态
            const updatedBuffer = { ...documentBuffer }
            
            // 清除所有对象的现有校验错误
            updatedBuffer.objects.forEach(obj => {
              obj.validationErrors = {}
              obj.isValid = true
            })
            
            // 应用后端校验错误
            Object.entries(validationErrors).forEach(([path, errors]) => {
              const errorArray = Array.isArray(errors) ? errors : [errors]
              
              if (updatedBuffer.objectsCount === 1) {
                updatedBuffer.objects[0].validationErrors[path] = errorArray
                updatedBuffer.objects[0].isValid = false
              } else {
                updatedBuffer.objects.forEach(obj => {
                  obj.validationErrors[path] = errorArray
                  obj.isValid = false
                })
              }
            })
            
            setDocumentBuffer(updatedBuffer)
          }
          
          return // 阻止提交
        }
        
        // 保存成功，更新本地状态
        updateAnnotation(documentBuffer.documentId, completeAnnotationData)
        
        // 清除修改标记
        const updatedBuffer = { ...documentBuffer }
        updatedBuffer.objects.forEach(obj => {
          obj.modifiedFields.clear()
          obj.validationErrors = {}
          obj.isValid = true
        })
        setDocumentBuffer(updatedBuffer)
        
        message.success('数据校验通过，正在提交...')
      }
      
      // 调用提交API
      const submitData = {
        annotation_data: constructCompleteAnnotationData(documentBuffer)
      }
      
      const submitResult = await annotationAPI.submitAnnotation(taskId!, documentId!, submitData)
      
      if (submitResult.success) {
        message.success('标注提交成功！')
        
        // 跳转到下一个文档或返回任务列表
        if (currentDocumentIndex < allDocuments.length - 1) {
          handleNextDocument()
        } else {
          // 使用强制刷新返回任务详情，确保状态同步
          window.location.href = `/tasks/${taskId}`
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
      const currentIndex = allDocuments.findIndex((doc: DocumentData) => doc.id === currentDocument.id)
      if (currentIndex > 0) {
        const prevDoc = allDocuments[currentIndex - 1]
        handleDocumentChange(prevDoc.id)
      }
    }
  }

  const handleNextDocument = () => {
    if (currentDocument) {
      const currentIndex = allDocuments.findIndex((doc: DocumentData) => doc.id === currentDocument.id)
      if (currentIndex < allDocuments.length - 1) {
        const nextDoc = allDocuments[currentIndex + 1]
        handleDocumentChange(nextDoc.id)
      }
    }
  }

  // 切换对象
  const handleObjectChange = (objectIndex: number) => {
    if (objectIndex === currentObjectIndex) return // 避免重复切换
    
    // 设置初始化标志，防止表单变更触发
    isInitializingRef.current = true
    
    setCurrentObjectIndex(objectIndex)
    
    // 更新表单数据为当前对象的标注数据
    if (documentBuffer && documentBuffer.objects[objectIndex]) {
      const currentObject = documentBuffer.objects[objectIndex]
      
      // 更新标注字段的原始值
      const updatedFields = annotationFields.map(field => ({
        ...field,
        originalValue: getNestedValue(currentObject.originalData, field.path)
      }))
      setAnnotationFields(updatedFields)
      
      // 由于表单组件现在使用本地状态，只需要等待一下让组件重新渲染
      setTimeout(() => {
        isInitializingRef.current = false
      }, 100)
    } else {
      isInitializingRef.current = false
    }
  }

  // 重置字段
  const handleResetField = (fieldPath: string) => {
    if (!currentObjectBuffer) return
    
    const originalValue = getNestedValue(currentObjectBuffer.originalData, fieldPath)
    handleFieldChange(fieldPath, originalValue)
  }

  // 重置所有字段
  const handleResetAllFields = () => {
    if (!currentObjectBuffer) return
    
    modal.confirm({
      title: '确认重置',
      content: '是否将当前对象的所有字段重置为原始值？',
      onOk: () => {
        annotationFields.forEach(field => {
          const originalValue = getNestedValue(currentObjectBuffer.originalData, field.path)
          handleFieldChange(field.path, originalValue)
        })
      }
    })
  }

  // 渲染loading状态
  if (isLoading || !currentDocument || !documentBuffer) {
    return (
      <div style={{ 
        height: '100vh', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center' 
      }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 左侧文档列表 */}
      <Sider 
        width={320} 
        style={{ 
          backgroundColor: '#fff', 
          borderRight: '1px solid #f0f0f0',
          overflow: 'auto'
        }}
      >
        <div style={{ padding: '16px' }}>
          <div style={{ marginBottom: 16 }}>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => {
                if (isDirty) {
                  modal.confirm({
                    title: '有未保存的更改',
                    content: '当前有未保存的更改，是否保存后返回？',
                    onOk: async () => {
                      await handleSave()
                      window.location.href = `/tasks/${taskId}`
                    },
                    onCancel: () => {
                      window.location.href = `/tasks/${taskId}`
                    }
                  })
                } else {
                  window.location.href = `/tasks/${taskId}`
                }
              }}
              style={{ marginBottom: 12 }}
            >
              返回任务
            </Button>
            
            <Breadcrumb style={{ fontSize: 12 }}>
              <Breadcrumb.Item>{currentTask?.name || '任务标注'}</Breadcrumb.Item>
              <Breadcrumb.Item>文档标注</Breadcrumb.Item>
            </Breadcrumb>
          </div>
          
          <Typography.Title level={5} style={{ margin: '0 0 16px 0' }}>
            <FileTextOutlined /> 文档列表
          </Typography.Title>
          
          <List
            size="small"
            dataSource={allDocuments}
            renderItem={(doc: DocumentData, index: number) => (
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
        {/* 顶部工具栏 */}
        <div style={{ 
          backgroundColor: '#fff', 
          borderBottom: '1px solid #f0f0f0', 
          padding: '12px 24px' 
        }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Space size="large">
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                    当前文档
                  </Text>
                  <Text strong style={{ color: '#1890ff' }}>
                    {currentDocumentIndex + 1} / {allDocuments.length}
                  </Text>
                </div>
                
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                    对象数量
                  </Text>
                  <Text strong style={{ color: '#52c41a' }}>
                    {documentBuffer.objectsCount} 个
                  </Text>
                </div>
                
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                    当前对象
                  </Text>
                  <Text strong style={{ color: '#722ed1' }}>
                    {currentObjectIndex + 1} / {documentBuffer.objectsCount}
                  </Text>
                </div>
                
                <div style={{ textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                    完成度
                  </Text>
                  <Text strong style={{ color: currentObjectBuffer?.completionPercentage === 100 ? '#52c41a' : '#1890ff' }}>
                    {currentObjectBuffer?.completionPercentage?.toFixed(1)}%
                  </Text>
                </div>
                
                {isDirty && (
                  <div style={{ textAlign: 'center' }}>
                    <Text type="warning" style={{ fontSize: 12, display: 'block' }}>
                      未保存更改
                    </Text>
                    <Text strong style={{ color: '#fa8c16' }}>
                      {documentBuffer.objects.reduce((sum, obj) => sum + obj.modifiedFields.size, 0)} 个字段
                    </Text>
                  </div>
                )}

                {/* 保存和导出按钮 */}
                <div style={{ marginLeft: '20px', borderLeft: '1px solid #f0f0f0', paddingLeft: '20px' }}>
                  <Space>
                    <Tooltip title="立即保存到后端">
                      <Button
                        type={isDirty ? "primary" : "default"}
                        icon={<SaveOutlined />}
                        onClick={handleSave}
                        loading={isLoading}
                        disabled={!isDirty}
                        style={{
                          background: isDirty ? '#52c41a' : undefined,
                          borderColor: isDirty ? '#52c41a' : undefined
                        }}
                      >
                        {isDirty ? '保存更改' : '已保存'}
                      </Button>
                    </Tooltip>
                    
                    <Tooltip title="导出标注数据为JSON文件">
                      <Button
                        icon={<DownloadOutlined />}
                        onClick={handleExportFile}
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
                  <EyeOutlined /> 当前对象内容
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
                  value={JSON.stringify(currentObjectBuffer?.annotationData || {}, null, 2)}
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
                      const value = getNestedValue(currentObjectBuffer?.annotationData, f.path)
                      return value !== undefined && value !== '' && value !== null
                    }).length}/${annotationFields.length}`}
                    style={{ backgroundColor: '#52c41a' }}
                  />
                  <Progress 
                    percent={currentObjectBuffer?.completionPercentage ?? 0} 
                    size="small" 
                    style={{ width: 60 }}
                    strokeColor={currentObjectBuffer?.completionPercentage === 100 ? '#52c41a' : '#1890ff'}
                  />
                  {(currentObjectBuffer?.modifiedFields?.size ?? 0) > 0 && (
                    <Badge 
                      count={`已修改: ${currentObjectBuffer?.modifiedFields?.size ?? 0}`}
                      style={{ backgroundColor: '#fa8c16' }}
                    />
                  )}
                  {!currentObjectBuffer?.isValid && (
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
                    disabled={(currentObjectBuffer?.modifiedFields?.size ?? 0) === 0}
                  >
                    重置当前对象
                  </Button>
                  <Button
                    icon={<LeftOutlined />}
                    onClick={handlePrevDocument}
                    disabled={currentDocumentIndex === 0}
                  >
                    上一个文档
                  </Button>
                  <Button
                    icon={<RightOutlined />}
                    onClick={handleNextDocument}
                    disabled={currentDocumentIndex === allDocuments.length - 1}
                  >
                    下一个文档
                  </Button>
                </Space>
              }
              style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
              bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '16px' }}
            >
              {/* 对象切换器 - 简化版 */}
              {documentBuffer.objectsCount > 1 && (
                <div style={{ marginBottom: 16, padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Space>
                        <Text strong>对象导航：</Text>
                        <Text type="secondary">
                          第 {currentObjectIndex + 1} 个，共 {documentBuffer.objectsCount} 个
                        </Text>
                        <Progress 
                          percent={currentObjectBuffer?.completionPercentage ?? 0} 
                          size="small" 
                          style={{ width: 80 }}
                          strokeColor={currentObjectBuffer?.completionPercentage === 100 ? '#52c41a' : '#1890ff'}
                        />
                      </Space>
                    </Col>
                    <Col>
                      <Space>
                        <Button
                          icon={<LeftOutlined />}
                          size="small"
                          onClick={() => handleObjectChange(currentObjectIndex - 1)}
                          disabled={currentObjectIndex === 0}
                        >
                          上一个
                        </Button>
                        <InputNumber
                          size="small"
                          min={1}
                          max={documentBuffer.objectsCount}
                          value={currentObjectIndex + 1}
                          onChange={(value) => {
                            if (value && value >= 1 && value <= documentBuffer.objectsCount) {
                              handleObjectChange(value - 1)
                            }
                          }}
                          style={{ width: 80 }}
                        />
                        <Button
                          icon={<RightOutlined />}
                          size="small"
                          onClick={() => handleObjectChange(currentObjectIndex + 1)}
                          disabled={currentObjectIndex === documentBuffer.objectsCount - 1}
                        >
                          下一个
                        </Button>
                      </Space>
                    </Col>
                  </Row>
                </div>
              )}
              
              {/* 表单内容区域 - 可滚动 */}
              <div style={{ 
                flex: 1, 
                overflowY: 'auto', 
                paddingRight: '8px',
                marginBottom: '16px',
                maxHeight: 'calc(100vh - 400px)' // 确保不超出视口
              }}>
                {annotationFields.length > 0 && currentObjectBuffer && (
                  <AnnotationFormRenderer
                    annotationFields={annotationFields}
                    formData={currentObjectBuffer.annotationData}
                    validationErrors={currentObjectBuffer.validationErrors}
                    modifiedFields={currentObjectBuffer.modifiedFields}
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
                    onClick={handleSave}
                    loading={isLoading}
                    disabled={!isDirty}
                  >
                    保存所有对象
                  </Button>
                  <Tooltip title={getSubmitButtonInfo.tooltip}>
                    <Button
                      type="primary"
                      icon={<CheckOutlined />}
                      onClick={handleSubmit}
                      loading={isLoading}
                      disabled={getSubmitButtonInfo.disabled}
                    >
                      {getSubmitButtonInfo.text}
                    </Button>
                  </Tooltip>
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