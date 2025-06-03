import React, { useMemo } from 'react'
import {
  Form,
  Input,
  Select,
  Switch,
  DatePicker,
  InputNumber,
  Checkbox,
  Radio,
  TimePicker,
  Button,
  Space,
  Card,
  Typography,
  Divider,
  Tag,
  Tooltip
} from 'antd'
import { FormInstance } from 'antd/es/form'
import { InfoCircleOutlined, EyeOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'

const { TextArea } = Input
const { Option } = Select
const { Group: CheckboxGroup } = Checkbox
const { Group: RadioGroup } = Radio
const { Text } = Typography

// 模板字段类型定义
export interface TemplateField {
  path: string
  field_type: string
  required: boolean
  description: string
  constraints: Record<string, any>
  default_value?: any
  options?: any[]
}

// 表单字段配置
export interface FormFieldConfig {
  name: string
  type: 'string' | 'text' | 'number' | 'boolean' | 'date' | 'datetime' | 'time' | 'select' | 'multiselect' | 'radio' | 'checkbox' | 'array' | 'object'
  required: boolean
  label: string
  description?: string
  placeholder?: string
  defaultValue?: any
  originalValue?: any
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
}

interface DynamicFormGeneratorProps {
  templateFields: TemplateField[]
  documentContent: Record<string, any>
  annotatedContent: Record<string, any>
  form: FormInstance
  onFieldChange?: (fieldPath: string, value: any) => void
  onValuesChange?: (changedValues: any, allValues: any) => void
  disabled?: boolean
}

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

// 类型映射
const TYPE_MAPPING: Record<string, FormFieldConfig['type']> = {
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

const DynamicFormGenerator: React.FC<DynamicFormGeneratorProps> = ({
  templateFields,
  documentContent,
  annotatedContent,
  form,
  onFieldChange,
  onValuesChange,
  disabled = false
}) => {
  // 转换模板字段为表单配置
  const formFields = useMemo(() => {
    return templateFields.map((field): FormFieldConfig => {
      // 获取原始文档中的值
      const originalValue = getNestedValue(documentContent, field.path)
      // 获取已标注的值
      const annotatedValue = getNestedValue(annotatedContent, field.path)
      
      // 确定字段类型
      const isTextArea = field.constraints?.max_length > 100 || 
                        field.description?.includes('文本') || 
                        field.description?.includes('内容') ||
                        field.description?.includes('描述')
      
      const fieldType = field.field_type === 'str' && isTextArea ? 'text' : 
                       TYPE_MAPPING[field.field_type] || 'string'
      
      // 确定默认值：优先使用已标注值，其次原始值，最后模板默认值
      const defaultValue = annotatedValue !== undefined ? annotatedValue : 
                          originalValue !== undefined ? originalValue : 
                          field.default_value
      
      // 处理选项
      const options = field.options ? field.options.map((opt: any) => ({
        value: typeof opt === 'object' ? opt.value : opt,
        label: typeof opt === 'object' ? opt.label : opt
      })) : undefined
      
      return {
        name: field.path,
        type: fieldType,
        required: field.required,
        label: field.description || field.path,
        description: field.description,
        placeholder: originalValue ? 
          `原始值: ${String(originalValue).substring(0, 50)}${String(originalValue).length > 50 ? '...' : ''}` : 
          `请输入${field.description || field.path}`,
        defaultValue,
        originalValue,
        options,
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
  }, [templateFields, documentContent, annotatedContent])
  
  // 渲染单个字段
  const renderField = (field: FormFieldConfig) => {
    const commonProps = {
      placeholder: field.placeholder,
      disabled,
      onChange: (value: any) => {
        if (onFieldChange) {
          onFieldChange(field.name, value)
        }
      }
    }
    
    // 处理数组字段
    if (field.name.includes('[]')) {
      const basePath = field.name.split('[]')[0]
      const subPath = field.name.split('[]')[1]?.substring(1) // 去掉开头的点
      
      return (
        <Card size="small" title={`${field.label} (数组)`} style={{ marginBottom: 16 }}>
          <Form.List name={basePath}>
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Card key={key} size="small" style={{ marginBottom: 8 }}>
                    <Space style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <Form.Item
                          {...restField}
                          name={subPath ? [name, ...subPath.split('.')] : [name]}
                          label={`${field.label} ${name + 1}`}
                          rules={[{ required: field.required, message: `请填写${field.label}` }]}
                        >
                          {renderBasicInput(field, commonProps)}
                        </Form.Item>
                      </div>
                      <Button type="link" onClick={() => remove(name)} disabled={disabled} danger>
                        删除
                      </Button>
                    </Space>
                  </Card>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block disabled={disabled}>
                    添加 {field.label}
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>
        </Card>
      )
    }
    
    // 处理嵌套字段
    const fieldPath = field.name.includes('.') ? field.name.split('.') : [field.name]
    
    return (
      <Form.Item
        name={fieldPath}
        initialValue={field.defaultValue}
        label={
          <Space>
            <span>{field.label}</span>
            {field.required && <span style={{ color: 'red' }}>*</span>}
            {field.description && (
              <Tooltip title={field.description}>
                <InfoCircleOutlined style={{ color: '#1890ff' }} />
              </Tooltip>
            )}
          </Space>
        }
        rules={[
          { required: field.required, message: `请填写${field.label}` },
          ...(field.validation?.pattern ? [{
            pattern: new RegExp(field.validation.pattern),
            message: field.validation.message || '格式不正确'
          }] : []),
          ...(field.validation?.max_length ? [{
            max: field.validation.max_length,
            message: `最多${field.validation.max_length}个字符`
          }] : []),
          ...(field.validation?.min_length ? [{
            min: field.validation.min_length,
            message: `至少${field.validation.min_length}个字符`
          }] : [])
        ]}
        extra={
          <div>
            {field.originalValue !== undefined && (
              <div style={{ 
                fontSize: '12px', 
                color: '#666', 
                backgroundColor: '#f5f5f5', 
                padding: '4px 8px', 
                borderRadius: '4px',
                marginTop: '4px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                <EyeOutlined />
                <strong>原始值:</strong> 
                <span style={{ wordBreak: 'break-all' }}>
                  {String(field.originalValue).length > 100 ? 
                    `${String(field.originalValue).substring(0, 100)}...` : 
                    String(field.originalValue)
                  }
                </span>
              </div>
            )}
          </div>
        }
      >
        {renderBasicInput(field, commonProps)}
      </Form.Item>
    )
  }
  
  // 渲染基础输入组件
  const renderBasicInput = (field: FormFieldConfig, commonProps: any) => {
    switch (field.type) {
      case 'string':
        return (
          <Input
            {...commonProps}
            maxLength={field.validation?.max_length}
            showCount={!!field.validation?.max_length}
          />
        )
      
      case 'text':
        return (
          <TextArea
            {...commonProps}
            rows={field.ui?.rows || 4}
            maxLength={field.validation?.max_length}
            showCount={!!field.validation?.max_length}
          />
        )
      
      case 'number':
        return (
          <InputNumber
            {...commonProps}
            min={field.validation?.min_value}
            max={field.validation?.max_value}
            style={{ width: '100%' }}
          />
        )
      
      case 'boolean':
        return <Switch disabled={disabled} />
      
      case 'date':
        return (
          <DatePicker
            {...commonProps}
            style={{ width: '100%' }}
            format={field.ui?.format || 'YYYY-MM-DD'}
          />
        )
      
      case 'datetime':
        return (
          <DatePicker
            {...commonProps}
            showTime={field.ui?.showTime !== false}
            style={{ width: '100%' }}
            format={field.ui?.format || 'YYYY-MM-DD HH:mm:ss'}
          />
        )
      
      case 'time':
        return (
          <TimePicker
            {...commonProps}
            style={{ width: '100%' }}
            format={field.ui?.format || 'HH:mm:ss'}
          />
        )
      
      case 'select':
        return (
          <Select {...commonProps} allowClear>
            {field.options?.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        )
      
      case 'multiselect':
        return (
          <Select {...commonProps} mode="multiple" allowClear>
            {field.options?.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        )
      
      case 'radio':
        return (
          <RadioGroup disabled={disabled}>
            {field.options?.map(option => (
              <Radio key={option.value} value={option.value}>
                {option.label}
              </Radio>
            ))}
          </RadioGroup>
        )
      
      case 'checkbox':
        return (
          <CheckboxGroup disabled={disabled}>
            {field.options?.map(option => (
              <Checkbox key={option.value} value={option.value}>
                {option.label}
              </Checkbox>
            ))}
          </CheckboxGroup>
        )
      
      case 'array':
        return (
          <Form.List name={field.name}>
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                    <Form.Item
                      {...restField}
                      name={[name]}
                      rules={[{ required: field.required, message: '请填写此项' }]}
                    >
                      <Input placeholder="请输入" />
                    </Form.Item>
                    <Button type="link" onClick={() => remove(name)} disabled={disabled}>
                      删除
                    </Button>
                  </Space>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block disabled={disabled}>
                    添加项目
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>
        )
      
      default:
        return <Input {...commonProps} />
    }
  }
  
  return (
    <Form
      form={form}
      layout="vertical"
      onValuesChange={onValuesChange}
    >
      {formFields.map((field) => (
        <div key={field.name}>
          {renderField(field)}
        </div>
      ))}
    </Form>
  )
}

export default DynamicFormGenerator
export { getNestedValue, setNestedValue }
export type { TemplateField, FormFieldConfig }