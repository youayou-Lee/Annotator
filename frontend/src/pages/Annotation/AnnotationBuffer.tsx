import React, { useEffect, useState } from 'react'
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
  Divider
} from 'antd'
import {
  ArrowLeftOutlined,
  SaveOutlined,
  CheckOutlined,
  LeftOutlined,
  RightOutlined,
  FileTextOutlined,
  FormOutlined,
  EyeOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useAnnotationBufferStore } from '../../stores/annotationBufferStore'
import FormFieldRenderer, { FormField as FormFieldType } from './components/FormFieldRenderer'
import MonacoEditor from '@monaco-editor/react'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { Sider, Content } = Layout
const { TextArea } = Input
const { Option } = Select

// 辅助函数：获取嵌套对象的值
const getNestedValue = (obj: any, path: string): any => {
  if (!obj || !path) return undefined
  
  const keys = path.split('.')
  let current = obj
  
  for (const key of keys) {
    if (current === null || current === undefined) {
      return undefined
    }
    current = current[key]
  }
  
  return current
}

// 辅助函数：设置嵌套对象的值
const setNestedValue = (obj: any, path: string, value: any): any => {
  if (!path) return obj
  
  const keys = path.split('.')
  const result = { ...obj }
  let current = result
  
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i]
    if (current[key] === undefined || current[key] === null) {
      current[key] = {}
    } else {
      current[key] = { ...current[key] }
    }
    current = current[key]
  }
  
  current[keys[keys.length - 1]] = value
  return result
}

const AnnotationBuffer: React.FC = () => {
  const { taskId, documentId } = useParams<{ taskId: string; documentId: string }>()
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const { message } = App.useApp()
  
  // 状态管理
  const [siderCollapsed, setSiderCollapsed] = useState(false)
  
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

  // 初始化表单数据 - 将原始文档内容映射到表单字段
  useEffect(() => {
    if (currentDocument && template?.fields) {
      // 合并原始文档内容和已标注内容
      const initialValues = { ...currentDocument.annotatedContent }
      
      // 将原始文档内容按字段路径映射到表单
      template.fields.forEach((field: any) => {
        const fieldPath = field.path
        const originalValue = getNestedValue(currentDocument.originalContent, fieldPath)
        
        // 如果标注内容中没有该字段值，则使用原始文档的值
        if (initialValues[fieldPath] === undefined && originalValue !== undefined) {
          initialValues[fieldPath] = originalValue
        }
      })
      
      form.setFieldsValue(initialValues)
      
      // 同步到buffer
      if (Object.keys(initialValues).length > 0) {
        updateAnnotation(currentDocument.id, initialValues)
      }
    }
  }, [currentDocument, template, form, updateAnnotation])

  // 表单值变化处理 - 支持嵌套字段路径
  const handleFormChange = (changedValues: any, allValues: any) => {
    if (currentDocument) {
      // 处理嵌套字段路径
      let updatedValues = { ...currentDocument.annotatedContent }
      
      // 遍历变化的值，按字段路径设置到正确位置
      Object.keys(changedValues).forEach(fieldPath => {
        if (fieldPath.includes('.')) {
          // 嵌套字段路径
          updatedValues = setNestedValue(updatedValues, fieldPath, changedValues[fieldPath])
        } else {
          // 简单字段
          updatedValues[fieldPath] = changedValues[fieldPath]
        }
      })
      
      // 合并所有表单值
      Object.keys(allValues).forEach(fieldPath => {
        if (fieldPath.includes('.')) {
          updatedValues = setNestedValue(updatedValues, fieldPath, allValues[fieldPath])
        } else {
          updatedValues[fieldPath] = allValues[fieldPath]
        }
      })
      
      updateAnnotation(currentDocument.id, updatedValues)
    }
  }

  // 保存标注数据
  const handleSave = async () => {
    try {
      await saveToBackend()
      message.success('保存成功')
    } catch (error: any) {
      message.error('保存失败: ' + error.message)
    }
  }

  // 提交标注
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (currentDocument) {
        updateAnnotation(currentDocument.id, values)
        await saveToBackend()
        message.success('提交成功')
        
        // 跳转到下一个文档
        const currentIndex = allDocuments.findIndex(doc => doc.id === currentDocument.id)
        if (currentIndex < allDocuments.length - 1) {
          const nextDoc = allDocuments[currentIndex + 1]
          navigate(`/tasks/${taskId}/documents/${nextDoc.id}/annotation-buffer`)
        }
      }
    } catch (error: any) {
      message.error('提交失败: ' + error.message)
    }
  }

  // 切换文档
  const handleDocumentChange = (docId: string) => {
    navigate(`/tasks/${taskId}/documents/${docId}/annotation-buffer`)
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

  // 转换后端字段格式为前端期望的格式
  const convertFieldsToFormFields = (fields: any[]): FormFieldType[] => {
    return fields.map((field: any) => {
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

      // 获取原始文档中对应字段的值作为默认值
      const originalValue = currentDocument ? getNestedValue(currentDocument.originalContent, field.path) : undefined
      const annotatedValue = currentDocument ? getNestedValue(currentDocument.annotatedContent, field.path) : undefined
      
      // 优先使用已标注的值，其次使用原始文档的值，最后使用字段定义的默认值
      const defaultValue = annotatedValue !== undefined ? annotatedValue : 
                          originalValue !== undefined ? originalValue : 
                          field.default_value

      return {
        name: field.path,
        type: fieldType,
        required: field.required || false,
        label: field.description || field.path,
        description: field.description,
        placeholder: originalValue ? `原始值: ${String(originalValue).substring(0, 50)}${String(originalValue).length > 50 ? '...' : ''}` : `请输入${field.description || field.path}`,
        default: defaultValue,
        originalValue: originalValue,  // 添加原始值
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
  }

  // 获取转换后的表单字段
  const formFields = template?.fields ? convertFieldsToFormFields(template.fields) : []

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip="加载任务数据中..." />
      </div>
    )
  }

  if (!currentDocument) {
    return (
      <div style={{ padding: '20px' }}>
        <Alert message="未找到文档数据" type="warning" />
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
                
                {isDirty && (
                  <div style={{ textAlign: 'center' }}>
                    <Text type="warning" style={{ fontSize: 12, display: 'block' }}>
                      有未保存更改
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
                  value={currentDocument.originalContent ? JSON.stringify(currentDocument.originalContent, null, 2) : '{}'}
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
          </div>

          {/* 右侧：标注表单 */}
          <div style={{ flex: 1, padding: '24px' }}>
            <Card
              title="标注表单"
              extra={
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
                    disabled={currentIndex === allDocuments.length - 1}
                  >
                    下一个
                  </Button>
                </Space>
              }
              style={{ height: '100%' }}
            >
              <div style={{ height: 'calc(100% - 60px)', overflowY: 'auto' }}>
                <Form
                  form={form}
                  layout="vertical"
                  onValuesChange={handleFormChange}
                >
                  {formFields.map((field: FormFieldType) => (
                    <FormFieldRenderer
                      key={field.name}
                      field={field}
                      form={form}
                      validationErrors={{}}
                      disabled={false}
                    />
                  ))}
                </Form>
              </div>
              
              <Divider />
              
              <div style={{ textAlign: 'right' }}>
                <Space>
                  <Button
                    icon={<SaveOutlined />}
                    onClick={handleSave}
                    loading={isLoading}
                  >
                    保存
                  </Button>
                  <Button
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={handleSubmit}
                    loading={isLoading}
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