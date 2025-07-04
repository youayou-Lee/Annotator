import React, { useState, useEffect, useCallback } from 'react'
import {
  Form,
  Input,
  Select,
  Switch,
  DatePicker,
  InputNumber,
  Checkbox,
  Radio,
  Button,
  Space,
  Card,
  Typography,
  Tag,
  Tooltip,
  Alert,
  Divider,
  Row,
  Col
} from 'antd'
import { FormInstance } from 'antd/es/form'
import { 
  ReloadOutlined, 
  ExclamationCircleOutlined, 
  CheckCircleOutlined,
  EditOutlined,
  InfoCircleOutlined,
  LockOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'

const { TextArea } = Input
const { Option } = Select
const { Group: CheckboxGroup } = Checkbox
const { Group: RadioGroup } = Radio
const { Text } = Typography

/**
 * 标注表单渲染器
 * 
 * 注意：此组件现在只进行基础的前端类型校验（必填项检查）
 * 复杂的数据校验（如约束检查、格式验证等）交由后端处理
 * 前端允许用户输入各种值，在保存时后端会返回详细的校验错误信息
 */

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

interface AnnotationFormRendererProps {
  annotationFields: AnnotationField[]
  formData: Record<string, any>
  validationErrors: Record<string, string[]>
  modifiedFields: Set<string>
  form: FormInstance
  onFieldChange: (fieldPath: string, value: any) => void
  onResetField: (fieldPath: string) => void
}

const AnnotationFormRenderer: React.FC<AnnotationFormRendererProps> = ({
  annotationFields,
  formData,
  validationErrors,
  modifiedFields,
  form,
  onFieldChange,
  onResetField
}) => {
  
  // 本地输入状态，用于处理实时输入
  const [localInputValues, setLocalInputValues] = useState<Record<string, any>>({})
  
  // 当formData变化时，更新本地状态（主要用于对象切换）
  useEffect(() => {
    // 清理所有防抖定时器，避免延迟更新干扰新对象的数据
    Object.values(debounceTimeouts.current).forEach(timeout => {
      if (timeout) clearTimeout(timeout)
    })
    debounceTimeouts.current = {}
    
    const newLocalValues: Record<string, any> = {}
    annotationFields.forEach(field => {
      const value = getNestedValue(formData, field.path)
      newLocalValues[field.path] = value
    })
    setLocalInputValues(newLocalValues)
    
    // 同时更新表单的值，确保表单和本地状态同步
    const formValues: Record<string, any> = {}
    annotationFields.forEach(field => {
      const value = getNestedValue(formData, field.path)
      formValues[field.path] = value
    })
    form.setFieldsValue(formValues)
  }, [formData, annotationFields, form])
  
  // 防抖处理输入变化
  const debounceTimeouts = React.useRef<Record<string, NodeJS.Timeout>>({})
  
  const handleInputChange = useCallback((fieldPath: string, value: any) => {
    // 立即更新本地状态，确保UI响应
    setLocalInputValues(prev => ({
      ...prev,
      [fieldPath]: value
    }))
    
    // 清除之前的防抖定时器
    if (debounceTimeouts.current[fieldPath]) {
      clearTimeout(debounceTimeouts.current[fieldPath])
    }
    
    // 设置新的防抖定时器
    debounceTimeouts.current[fieldPath] = setTimeout(() => {
      onFieldChange(fieldPath, value)
      delete debounceTimeouts.current[fieldPath]
    }, 300) // 300ms 防抖，比之前更长
  }, [onFieldChange])
  
  // 组件卸载时清理定时器
  useEffect(() => {
    return () => {
      Object.values(debounceTimeouts.current).forEach(timeout => {
        if (timeout) clearTimeout(timeout)
      })
      debounceTimeouts.current = {}
    }
  }, [])

  // 从嵌套对象中获取值 - 支持数组路径和复杂结构
  const getNestedValue = (obj: any, path: string): any => {
    if (!obj || !path) return undefined
    
    // 特殊处理：如果文档结构是 {items: [...], type: 'array'}，则从items[0]开始
    let current = obj
    if (obj.items && Array.isArray(obj.items) && obj.items.length > 0 && obj.type === 'array') {
      current = obj.items[0]
    }
    
    // 处理包含数组索引的路径 如: content_sections[].text
    if (path.includes('[]')) {
      const parts = path.split('[]')
      let arrayPath = parts[0] // content_sections
      let remainingPath = parts[1] // .text
      
      // 获取到数组
      const arrayKeys = arrayPath.split('.')
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

  // 格式化显示值 - 处理复杂对象和数组
  const formatDisplayValue = (value: any): string => {
    if (value === undefined || value === null) {
      return ''
    }
    
    if (typeof value === 'string') {
      return value
    }
    
    if (typeof value === 'number' || typeof value === 'boolean') {
      return String(value)
    }
    
    if (Array.isArray(value)) {
      // 数组：显示为逗号分隔的字符串
      return value.map(item => 
        typeof item === 'object' ? JSON.stringify(item) : String(item)
      ).join(', ')
    }
    
    if (typeof value === 'object') {
      // 对象：显示为JSON字符串
      return JSON.stringify(value, null, 2)
    }
    
    return String(value)
  }

  // 解析输入值 - 将各种类型的输入值转换为合适的格式
  const parseInputValue = (value: any, fieldType: string, originalValue: any): any => {
    // 调试日志 - 在开发环境下显示输入值类型
    if (process.env.NODE_ENV === 'development') {
      console.log('parseInputValue:', { value, type: typeof value, fieldType })
    }
    
    // 如果是 null 或 undefined，直接返回
    if (value === null || value === undefined) {
      return undefined
    }
    
    // 对于空字符串，保持原样，让后端进行验证
    if (value === '') {
      return ''
    }
    
    // 如果是字符串类型，进行trim检查
    if (typeof value === 'string' && value.trim() === '') {
      return undefined
    }
    
    // 如果已经是目标类型，直接返回（比如InputNumber返回的数字）
    switch (fieldType) {
      case 'int':
      case 'float':
        if (typeof value === 'number') {
          return value
        }
        // 如果是字符串，尝试转换
        if (typeof value === 'string') {
          const numVal = fieldType === 'int' ? parseInt(value, 10) : parseFloat(value)
          return isNaN(numVal) ? value : numVal
        }
        return value

      case 'bool':
        if (typeof value === 'boolean') {
          return value
        }
        // 如果是字符串，尝试转换布尔值
        if (typeof value === 'string') {
          if (value === 'true' || value === '1' || value === 'yes' || value === 'True') {
            return true
          } else if (value === 'false' || value === '0' || value === 'no' || value === 'False') {
            return false
          }
        }
        return value

      case 'str':
      default:
        // 如果原始值是对象或数组，且输入是字符串，尝试解析JSON
        if (originalValue && typeof originalValue === 'object' && typeof value === 'string') {
          try {
            return JSON.parse(value)
          } catch (e) {
            // JSON解析失败，保持字符串形式，让后端验证
            return value
          }
        }
        
        // 对于字符串类型，确保返回字符串
        return String(value)
    }
  }

  // 渲染字段标签
  const renderFieldLabel = (field: AnnotationField) => {
    const isModified = modifiedFields.has(field.path)
    const hasError = validationErrors[field.path]?.length > 0
    
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <span>
          {field.path}
          {field.required && <span style={{ color: 'red' }}> *</span>}
        </span>
        
        {isModified && (
          <Tag color="orange">已修改</Tag>
        )}
        
        {hasError && (
          <Tag color="red" icon={<ExclamationCircleOutlined />}>
            错误
          </Tag>
        )}
        
        {field.type && (
          <Tag style={{ fontSize: '10px', marginLeft: 'auto' }}>
            {field.type}
          </Tag>
        )}
        
        {isModified && (
          <Tooltip title="重置为原始值">
            <Button
              type="text"
              size="small"
              icon={<ReloadOutlined />}
              onClick={() => onResetField(field.path)}
              style={{ 
                padding: '0 4px', 
                height: 'auto', 
                minWidth: 'auto',
                color: '#1890ff'
              }}
            />
          </Tooltip>
        )}
      </div>
    )
  }

  // 渲染字段帮助信息
  const renderFieldHelp = (field: AnnotationField) => {
    const errors = validationErrors[field.path] || []
    const currentValue = getNestedValue(formData, field.path)
    const originalValue = field.originalValue
    
    const helpElements = []
    
    // 显示验证错误（主要来自后端）
    if (errors.length > 0) {
      helpElements.push(
        <div key="errors" style={{ color: '#ff4d4f' }}>
          {errors.map((error, index) => (
            <div key={index}>• {error}</div>
          ))}
        </div>
      )
    }
    
    // 简化的约束提示（只显示基本信息）
    const basicInfo = []
    if (field.type === 'str' && field.constraints?.max_length) {
      basicInfo.push(`最多${field.constraints.max_length}字符`)
    }
    if (field.type === 'int' || field.type === 'float') {
      const range = []
      if (field.constraints?.ge !== undefined) {
        range.push(`≥${field.constraints.ge}`)
      }
      if (field.constraints?.le !== undefined) {
        range.push(`≤${field.constraints.le}`)
      }
      if (range.length > 0) {
        basicInfo.push(range.join(', '))
      }
    }
    
    if (basicInfo.length > 0) {
      helpElements.push(
        <div key="basic-info" style={{ color: '#8c8c8c', fontSize: 12 }}>
          {basicInfo.join(', ')}
        </div>
      )
    }
    
    // 显示原始值
    if (originalValue !== undefined && originalValue !== currentValue) {
      helpElements.push(
        <div key="original" style={{ color: '#1890ff', fontSize: 12 }}>
          原始值: {formatDisplayValue(originalValue)}
        </div>
      )
    }
    
    return helpElements.length > 0 ? (
      <div style={{ marginTop: 4 }}>
        {helpElements}
      </div>
    ) : null
  }

  // 渲染不同类型的输入控件
  const renderInputControl = (field: AnnotationField) => {
    const currentValue = localInputValues[field.path]
    const displayValue = formatDisplayValue(currentValue)
    
    const isComplexValue = currentValue && typeof currentValue === 'object'
    const isTextArea = field.type === 'str' && (
      field.constraints?.max_length > 100 || 
      field.description?.includes('文本') || 
      field.description?.includes('内容') ||
      isComplexValue
    )

    // 处理值变化
    const handleValueChange = (value: any) => {
      try {
        const parsedValue = parseInputValue(value, field.type, currentValue)
        handleInputChange(field.path, parsedValue)
      } catch (error) {
        console.error('Error in handleValueChange:', error, { value, fieldType: field.type, fieldPath: field.path })
        // 如果解析失败，直接传递原值
        handleInputChange(field.path, value)
      }
    }

    switch (field.type) {
      case 'str':
        if (isTextArea || isComplexValue) {
          return (
            <TextArea
              value={displayValue}
              onChange={(e) => handleValueChange(e.target.value)}
              placeholder={field.description || `请输入${field.path}`}
              rows={isComplexValue ? 6 : 4}
              showCount={field.constraints?.max_length ? true : false}
              maxLength={field.constraints?.max_length}
            />
          )
        } else {
          return (
            <Input
              value={displayValue}
              onChange={(e) => handleValueChange(e.target.value)}
              placeholder={field.description || `请输入${field.path}`}
              maxLength={field.constraints?.max_length}
            />
          )
        }

      case 'int':
        return (
          <InputNumber
            value={currentValue}
            onChange={(value) => handleValueChange(value)}
            placeholder={field.description || `请输入${field.path}`}
            style={{ width: '100%' }}
            min={field.constraints?.ge}
            max={field.constraints?.le}
            precision={0}
          />
        )

      case 'float':
        return (
          <InputNumber
            value={currentValue}
            onChange={(value) => handleValueChange(value)}
            placeholder={field.description || `请输入${field.path}`}
            style={{ width: '100%' }}
            min={field.constraints?.ge}
            max={field.constraints?.le}
            step={0.1}
          />
        )

      case 'bool':
        return (
          <Switch
            checked={currentValue}
            onChange={(checked) => handleValueChange(checked)}
            checkedChildren="是"
            unCheckedChildren="否"
          />
        )

      case 'date':
        return (
          <DatePicker
            value={currentValue ? dayjs(currentValue) : undefined}
            onChange={(date) => handleValueChange(date ? date.format('YYYY-MM-DD') : undefined)}
            style={{ width: '100%' }}
            placeholder={field.description || `请选择${field.path}`}
          />
        )

      case 'datetime':
        return (
          <DatePicker
            value={currentValue ? dayjs(currentValue) : undefined}
            onChange={(date) => handleValueChange(date ? date.toISOString() : undefined)}
            style={{ width: '100%' }}
            showTime
            placeholder={field.description || `请选择${field.path}`}
          />
        )

      default:
        // 处理枚举类型或其他复杂类型
        if (field.constraints?.enum) {
          return (
            <Select
              value={currentValue}
              onChange={(value) => handleValueChange(value)}
              placeholder={field.description || `请选择${field.path}`}
              style={{ width: '100%' }}
              allowClear
            >
              {field.constraints.enum.map((option: any) => (
                <Option key={option} value={option}>
                  {option}
                </Option>
              ))}
            </Select>
          )
        }
        
        // 复杂类型使用多行文本框
        if (isComplexValue) {
          return (
            <TextArea
              value={displayValue}
              onChange={(e) => handleValueChange(e.target.value)}
              placeholder={field.description || `请输入${field.path}（JSON格式）`}
              rows={6}
            />
          )
        }
        
        // 默认使用文本输入
        return (
          <Input
            value={displayValue}
            onChange={(e) => handleValueChange(e.target.value)}
            placeholder={field.description || `请输入${field.path}`}
          />
        )
    }
  }

  // 按字段路径分组
  const groupedFields = annotationFields.reduce((groups, field) => {
    const parts = field.path.split('.')
    const group = parts.length > 1 ? parts[0] : 'root'
    
    if (!groups[group]) {
      groups[group] = []
    }
    groups[group].push(field)
    
    return groups
  }, {} as Record<string, AnnotationField[]>)

  // 渲染字段组
  const renderFieldGroup = (groupName: string, fields: AnnotationField[]) => {
    const hasGroupErrors = fields.some(field => validationErrors[field.path]?.length > 0)
    const modifiedCount = fields.filter(field => modifiedFields.has(field.path)).length
    
    return (
      <Card
        key={groupName}
        size="small"
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>{groupName === 'root' ? '基础字段' : groupName}</span>
            {modifiedCount > 0 && (
              <Tag color="orange">
                {modifiedCount} 个已修改
              </Tag>
            )}
            {hasGroupErrors && (
              <Tag color="red">
                有错误
              </Tag>
            )}
          </div>
        }
        style={{ marginBottom: 16 }}
        bodyStyle={{ padding: '12px 16px' }}
      >
        <Row gutter={[16, 16]}>
          {fields.map(field => (
            <Col 
              key={field.path} 
              span={field.type === 'str' && field.constraints?.max_length > 100 ? 24 : 12}
            >
              <Form.Item
                name={field.path}
                label={renderFieldLabel(field)}
                validateStatus={validationErrors[field.path]?.length > 0 ? 'error' : ''}
                help={renderFieldHelp(field)}
                rules={[
                  {
                    required: field.required,
                    message: `${field.path}是必填项`
                  }
                ]}
              >
                {(() => {
                  try {
                    return renderInputControl(field)
                  } catch (error: any) {
                    console.error('Error rendering field:', field.path, error)
                    return (
                      <Input 
                        placeholder={`字段渲染错误: ${field.path}`}
                        disabled
                        style={{ color: 'red' }}
                        value={`Error: ${error?.message || '未知错误'}`}
                      />
                    )
                  }
                })()}
              </Form.Item>
            </Col>
          ))}
        </Row>
      </Card>
    )
  }

  // 统计信息
  const totalFields = annotationFields.length
  const filledFields = annotationFields.filter(field => {
    const value = getNestedValue(formData, field.path)
    return value !== undefined && value !== '' && value !== null
  }).length
  const errorFields = Object.keys(validationErrors).length
  const modifiedFieldsCount = modifiedFields.size

  return (
    <div>
      {/* 表单统计 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={16} style={{ textAlign: 'center' }}>
          <Col span={6}>
            <div>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: '#1890ff' }}>
                {totalFields}
              </div>
              <div style={{ fontSize: 12, color: '#8c8c8c' }}>总字段数</div>
            </div>
          </Col>
          <Col span={6}>
            <div>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: '#52c41a' }}>
                {filledFields}
              </div>
              <div style={{ fontSize: 12, color: '#8c8c8c' }}>已填写</div>
            </div>
          </Col>
          <Col span={6}>
            <div>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: '#fa8c16' }}>
                {modifiedFieldsCount}
              </div>
              <div style={{ fontSize: 12, color: '#8c8c8c' }}>已修改</div>
            </div>
          </Col>
          <Col span={6}>
            <div>
              <div style={{ fontSize: 20, fontWeight: 'bold', color: errorFields > 0 ? '#ff4d4f' : '#52c41a' }}>
                {errorFields}
              </div>
              <div style={{ fontSize: 12, color: '#8c8c8c' }}>错误数</div>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 全局错误提示 */}
      {errorFields > 0 && (
        <Alert
          message="表单验证错误,详情请按F12查看"
          description={`发现 ${errorFields} 个字段存在验证错误，请检查并修正。`}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 表单字段 */}
      <Form
        form={form}
        layout="vertical"
        size="small"
      >
        {Object.entries(groupedFields).map(([groupName, fields]) =>
          renderFieldGroup(groupName, fields)
        )}
      </Form>

      {/* 操作提示 */}
      {modifiedFieldsCount > 0 && (
        <Alert
          message="有未保存的修改"
          description={`您已修改了 ${modifiedFieldsCount} 个字段，请记得保存您的更改。`}
          type="warning"
          showIcon
          style={{ marginTop: 16 }}
        />
      )}
    </div>
  )
}

export default AnnotationFormRenderer 