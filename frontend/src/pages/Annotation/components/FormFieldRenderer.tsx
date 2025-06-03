import React from 'react'
import {
  Input,
  Select,
  Switch,
  DatePicker,
  InputNumber,
  Checkbox,
  Radio,
  TimePicker,
  Form,
  Button,
  Space,
  Card,
  Typography,
  Divider
} from 'antd'
import { FormInstance } from 'antd/es/form'

const { TextArea } = Input
const { Option } = Select
const { Group: CheckboxGroup } = Checkbox
const { Group: RadioGroup } = Radio
const { Text } = Typography

// 字段类型定义
export interface FormField {
  name: string
  type: 'string' | 'text' | 'number' | 'boolean' | 'date' | 'datetime' | 'time' | 'select' | 'multiselect' | 'radio' | 'checkbox' | 'array' | 'object' | 'file'
  required: boolean
  label: string
  description?: string
  placeholder?: string
  default?: any
  originalValue?: any  // 原始文档中的值
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

interface FormFieldRendererProps {
  field: FormField
  form: FormInstance
  validationErrors: Record<string, string>
  disabled?: boolean
}

// 解析嵌套路径为Form.Item的name数组
const parseFieldPath = (path: string): (string | number)[] => {
  // 处理数组索引，如 content_sections[].text
  const parts = path.split('.')
  const result: (string | number)[] = []
  
  for (const part of parts) {
    if (part.includes('[]')) {
      // 数组字段，如 content_sections[]
      const arrayName = part.replace('[]', '')
      result.push(arrayName)
      // 对于数组字段，我们使用动态索引
    } else {
      result.push(part)
    }
  }
  
  return result
}

// 判断是否为数组字段
const isArrayField = (path: string): boolean => {
  return path.includes('[]')
}

// 获取数组字段的基础路径
const getArrayBasePath = (path: string): string => {
  return path.split('[]')[0]
}

// 获取数组字段的子路径
const getArraySubPath = (path: string): string => {
  const parts = path.split('[]')
  return parts.length > 1 ? parts[1].substring(1) : '' // 去掉开头的点
}

const FormFieldRenderer: React.FC<FormFieldRendererProps> = ({
  field,
  form,
  validationErrors,
  disabled = false
}) => {
  const hasError = validationErrors[field.name]
  const commonProps = {
    placeholder: field.placeholder,
    disabled,
    status: hasError ? 'error' as const : undefined
  }

  // 检查条件显示
  if (field.conditional) {
    const conditionValue = form.getFieldValue(field.conditional.field)
    const shouldShow = (() => {
      switch (field.conditional.operator) {
        case 'eq': return conditionValue === field.conditional.value
        case 'ne': return conditionValue !== field.conditional.value
        case 'in': return Array.isArray(field.conditional.value) && field.conditional.value.includes(conditionValue)
        case 'not_in': return Array.isArray(field.conditional.value) && !field.conditional.value.includes(conditionValue)
        case 'gt': return conditionValue > field.conditional.value
        case 'lt': return conditionValue < field.conditional.value
        default: return true
      }
    })()
    
    if (!shouldShow) return null
  }

  // 处理数组字段
  if (isArrayField(field.name)) {
    const basePath = getArrayBasePath(field.name)
    const subPath = getArraySubPath(field.name)
    
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
                        {renderBasicInput()}
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

  // 处理嵌套对象字段
  if (field.name.includes('.') && !isArrayField(field.name)) {
    const fieldPath = parseFieldPath(field.name)
    return (
      <Form.Item
        name={fieldPath}
        label={field.label}
        rules={[
          { required: field.required, message: `请填写${field.label}` },
          ...(field.validation?.pattern ? [{
            pattern: new RegExp(field.validation.pattern),
            message: field.validation.message || '格式不正确'
          }] : [])
        ]}
        extra={
        <div>
          {field.description && <div style={{ marginBottom: 4 }}>{field.description}</div>}
          {field.originalValue !== undefined && (
            <div style={{ 
              fontSize: '12px', 
              color: '#666', 
              backgroundColor: '#f5f5f5', 
              padding: '4px 8px', 
              borderRadius: '4px',
              marginTop: '4px'
            }}>
              <strong>原始值:</strong> {String(field.originalValue)}
            </div>
          )}
        </div>
      }
      >
        {renderBasicInput()}
      </Form.Item>
    )
  }

  // 普通字段
  return (
    <Form.Item
      name={field.name}
      label={field.label}
      rules={[
        { required: field.required, message: `请填写${field.label}` },
        ...(field.validation?.pattern ? [{
          pattern: new RegExp(field.validation.pattern),
          message: field.validation.message || '格式不正确'
        }] : [])
      ]}
      extra={
        <div>
          {field.description && <div style={{ marginBottom: 4 }}>{field.description}</div>}
          {field.originalValue !== undefined && (
            <div style={{ 
              fontSize: '12px', 
              color: '#666', 
              backgroundColor: '#f5f5f5', 
              padding: '4px 8px', 
              borderRadius: '4px',
              marginTop: '4px'
            }}>
              <strong>原始值:</strong> {String(field.originalValue)}
            </div>
          )}
        </div>
      }
    >
      {renderBasicInput()}
    </Form.Item>
  )

  function renderBasicInput() {
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
                      {field.items ? (
                        <FormFieldRenderer
                          field={field.items}
                          form={form}
                          validationErrors={validationErrors}
                          disabled={disabled}
                        />
                      ) : (
                        <Input placeholder="请输入" />
                      )}
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
      
      case 'object':
        return (
          <Card size="small" style={{ marginBottom: 16 }}>
            {field.properties && Object.entries(field.properties).map(([key, subField]) => (
              <Form.Item
                key={key}
                name={[field.name, key]}
                label={subField.label}
                rules={[
                  { required: subField.required, message: `请输入${subField.label}` }
                ]}
              >
                <FormFieldRenderer
                  field={subField}
                  form={form}
                  validationErrors={validationErrors}
                  disabled={disabled}
                />
              </Form.Item>
            ))}
          </Card>
        )
      
      default:
        return <Input {...commonProps} />
    }
  }
}

export default FormFieldRenderer