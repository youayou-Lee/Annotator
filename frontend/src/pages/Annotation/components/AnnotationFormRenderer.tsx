import React from 'react'
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
  InfoCircleOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'

const { TextArea } = Input
const { Option } = Select
const { Group: CheckboxGroup } = Checkbox
const { Group: RadioGroup } = Radio
const { Text } = Typography

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
  
  // 从嵌套对象中获取值
  const getNestedValue = (obj: any, path: string): any => {
    if (!obj || !path) return undefined
    return path.split('.').reduce((current, key) => current?.[key], obj)
  }

  // 渲染字段标签
  const renderFieldLabel = (field: AnnotationField) => {
    const isModified = modifiedFields.has(field.path)
    const hasError = validationErrors[field.path]?.length > 0
    
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span>
          {field.path}
          {field.required && <span style={{ color: 'red' }}> *</span>}
        </span>
        
        {isModified && (
          <Tag color="orange" icon={<EditOutlined />}>
            已修改
          </Tag>
        )}
        
        {hasError && (
          <Tag color="red" icon={<ExclamationCircleOutlined />}>
            有错误
          </Tag>
        )}
        
        <Tooltip title={`字段描述: ${field.description}`}>
          <InfoCircleOutlined style={{ color: '#8c8c8c', fontSize: 12 }} />
        </Tooltip>
        
        {(isModified || field.originalValue !== undefined) && (
          <Tooltip title="重置到原始值">
            <Button
              type="text"
              size="small"
              icon={<ReloadOutlined />}
              onClick={() => onResetField(field.path)}
              style={{ padding: 0, height: 16, width: 16 }}
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
    
    // 显示验证错误
    if (errors.length > 0) {
      helpElements.push(
        <div key="errors" style={{ color: '#ff4d4f' }}>
          {errors.map((error, index) => (
            <div key={index}>• {error}</div>
          ))}
        </div>
      )
    }
    
    // 显示约束信息
    const constraints = []
    if (field.type === 'str') {
      if (field.constraints.min_length) {
        constraints.push(`最少${field.constraints.min_length}个字符`)
      }
      if (field.constraints.max_length) {
        constraints.push(`最多${field.constraints.max_length}个字符`)
      }
    }
    if (field.type === 'int' || field.type === 'float') {
      if (field.constraints.ge !== undefined) {
        constraints.push(`≥ ${field.constraints.ge}`)
      }
      if (field.constraints.le !== undefined) {
        constraints.push(`≤ ${field.constraints.le}`)
      }
    }
    
    if (constraints.length > 0) {
      helpElements.push(
        <div key="constraints" style={{ color: '#8c8c8c', fontSize: 12 }}>
          约束: {constraints.join(', ')}
        </div>
      )
    }
    
    // 显示原始值
    if (originalValue !== undefined && originalValue !== currentValue) {
      helpElements.push(
        <div key="original" style={{ color: '#1890ff', fontSize: 12 }}>
          原始值: {String(originalValue)}
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
    const currentValue = getNestedValue(formData, field.path)
    const isTextArea = field.type === 'str' && (
      field.constraints?.max_length > 100 || 
      field.description?.includes('文本') || 
      field.description?.includes('内容')
    )

    switch (field.type) {
      case 'str':
        if (isTextArea) {
          return (
            <TextArea
              placeholder={field.description || `请输入${field.path}`}
              rows={4}
              showCount={field.constraints?.max_length ? true : false}
              maxLength={field.constraints?.max_length}
            />
          )
        } else {
          return (
            <Input
              placeholder={field.description || `请输入${field.path}`}
              maxLength={field.constraints?.max_length}
            />
          )
        }

      case 'int':
        return (
          <InputNumber
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
            checkedChildren="是"
            unCheckedChildren="否"
          />
        )

      case 'date':
        return (
          <DatePicker
            style={{ width: '100%' }}
            placeholder={field.description || `请选择${field.path}`}
          />
        )

      case 'datetime':
        return (
          <DatePicker
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
        
        // 默认使用文本输入
        return (
          <Input
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
                {renderInputControl(field)}
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
          message="表单验证错误"
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
        onValuesChange={(changedValues, allValues) => {
          // 处理值变化 - 对每个变化的字段调用onFieldChange
          Object.keys(changedValues).forEach(fieldPath => {
            onFieldChange(fieldPath, changedValues[fieldPath])
          })
        }}
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