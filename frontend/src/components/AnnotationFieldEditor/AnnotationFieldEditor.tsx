import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Input, 
  Button, 
  Space, 
  Select, 
  Checkbox, 
  InputNumber, 
  Divider,
  Card,
  Row, 
  Col,
  Typography
} from 'antd';
import { PlusOutlined, DeleteOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

const { Title } = Typography;
const { Option } = Select;

// 字段类型定义
export enum FieldType {
  STRING = "string",
  INTEGER = "integer",
  FLOAT = "float",
  BOOLEAN = "boolean",
  DATE = "date",
  DATETIME = "datetime",
  EMAIL = "email",
  PHONE = "phone",
  ENUM = "enum",
  OBJECT = "object",
  ARRAY = "array"
}

// 表示一个标注字段的定义
export interface AnnotationField {
  name: string;
  label: string;
  type: FieldType;
  required: boolean;
  description?: string;
  enum_values?: string[];
  default?: any;
  min?: number;
  max?: number;
  regex?: string;
}

// 组件属性
interface AnnotationFieldEditorProps {
  value?: AnnotationField[];
  onChange?: (fields: AnnotationField[]) => void;
}

const AnnotationFieldEditor: React.FC<AnnotationFieldEditorProps> = ({ 
  value = [], 
  onChange 
}) => {
  const [fields, setFields] = useState<AnnotationField[]>(value);

  // 当外部value变化时更新内部状态
  useEffect(() => {
    setFields(value);
  }, [value]);

  // 添加新字段
  const handleAddField = () => {
    const newField: AnnotationField = {
      name: `field_${fields.length + 1}`,
      label: `字段 ${fields.length + 1}`,
      type: FieldType.STRING,
      required: true
    };
    
    const newFields = [...fields, newField];
    setFields(newFields);
    onChange?.(newFields);
  };

  // 更新字段
  const handleFieldChange = (index: number, fieldKey: keyof AnnotationField, fieldValue: any) => {
    const newFields = [...fields];
    newFields[index] = {
      ...newFields[index],
      [fieldKey]: fieldValue
    };
    
    // 如果类型变更，需要清除与特定类型相关的属性
    if (fieldKey === 'type') {
      const field = newFields[index];
      
      // 清除不再适用的属性
      if (fieldValue !== FieldType.ENUM) {
        delete field.enum_values;
      }
      
      if (![FieldType.INTEGER, FieldType.FLOAT].includes(fieldValue)) {
        delete field.min;
        delete field.max;
      }
      
      if (fieldValue !== FieldType.STRING) {
        delete field.regex;
      }
    }
    
    setFields(newFields);
    onChange?.(newFields);
  };

  // 删除字段
  const handleDeleteField = (index: number) => {
    const newFields = [...fields];
    newFields.splice(index, 1);
    setFields(newFields);
    onChange?.(newFields);
  };

  // 移动字段（上移或下移）
  const handleMoveField = (index: number, direction: 'up' | 'down') => {
    if (
      (direction === 'up' && index === 0) || 
      (direction === 'down' && index === fields.length - 1)
    ) {
      return; // 已经在最顶部或最底部
    }
    
    const newFields = [...fields];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    
    // 交换位置
    [newFields[index], newFields[newIndex]] = [newFields[newIndex], newFields[index]];
    
    setFields(newFields);
    onChange?.(newFields);
  };

  // 处理枚举值变化
  const handleEnumValuesChange = (index: number, values: string[]) => {
    const newFields = [...fields];
    newFields[index].enum_values = values;
    setFields(newFields);
    onChange?.(newFields);
  };

  // 渲染添加/删除枚举值的输入框
  const renderEnumValuesInput = (field: AnnotationField, index: number) => {
    const enumValues = field.enum_values || [];
    
    return (
      <Form.Item label="枚举值">
        <Space direction="vertical" style={{ width: '100%' }}>
          {enumValues.map((value, valueIndex) => (
            <Input
              key={valueIndex}
              value={value}
              onChange={(e) => {
                const newEnumValues = [...enumValues];
                newEnumValues[valueIndex] = e.target.value;
                handleEnumValuesChange(index, newEnumValues);
              }}
              suffix={
                <Button 
                  type="text" 
                  danger 
                  icon={<DeleteOutlined />} 
                  onClick={() => {
                    const newEnumValues = [...enumValues];
                    newEnumValues.splice(valueIndex, 1);
                    handleEnumValuesChange(index, newEnumValues);
                  }}
                />
              }
            />
          ))}
          <Button 
            type="dashed" 
            block 
            icon={<PlusOutlined />} 
            onClick={() => {
              handleEnumValuesChange(index, [...enumValues, `选项${enumValues.length + 1}`]);
            }}
          >
            添加选项值
          </Button>
        </Space>
      </Form.Item>
    );
  };

  // 渲染数值范围输入
  const renderNumberRangeInputs = (field: AnnotationField, index: number) => {
    return (
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item label="最小值">
            <InputNumber
              style={{ width: '100%' }}
              value={field.min}
              onChange={(value) => handleFieldChange(index, 'min', value)}
            />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item label="最大值">
            <InputNumber
              style={{ width: '100%' }}
              value={field.max}
              onChange={(value) => handleFieldChange(index, 'max', value)}
            />
          </Form.Item>
        </Col>
      </Row>
    );
  };

  // 渲染正则表达式输入
  const renderRegexInput = (field: AnnotationField, index: number) => {
    return (
      <Form.Item label="正则表达式验证">
        <Input
          value={field.regex}
          onChange={(e) => handleFieldChange(index, 'regex', e.target.value)}
          placeholder="例如: ^[a-zA-Z0-9_]+$"
        />
      </Form.Item>
    );
  };

  // 渲染字段编辑表单
  const renderFieldForm = (field: AnnotationField, index: number) => {
    return (
      <Card 
        key={index}
        title={`字段 ${index + 1}: ${field.label || field.name}`}
        style={{ marginBottom: 16 }}
        extra={
          <Space>
            <Button 
              icon={<ArrowUpOutlined />} 
              disabled={index === 0}
              onClick={() => handleMoveField(index, 'up')}
            />
            <Button 
              icon={<ArrowDownOutlined />}
              disabled={index === fields.length - 1}
              onClick={() => handleMoveField(index, 'down')}
            />
            <Button 
              danger 
              icon={<DeleteOutlined />} 
              onClick={() => handleDeleteField(index)}
            />
          </Space>
        }
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item label="字段名" required tooltip="内部使用的字段标识符，不含空格和特殊字符">
              <Input
                value={field.name}
                onChange={(e) => handleFieldChange(index, 'name', e.target.value)}
                placeholder="field_name"
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label="显示名称" required tooltip="用于界面显示的字段名称">
              <Input
                value={field.label}
                onChange={(e) => handleFieldChange(index, 'label', e.target.value)}
                placeholder="字段名称"
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item label="字段类型" required>
              <Select
                value={field.type}
                onChange={(value) => handleFieldChange(index, 'type', value)}
                style={{ width: '100%' }}
              >
                <Option value={FieldType.STRING}>字符串</Option>
                <Option value={FieldType.INTEGER}>整数</Option>
                <Option value={FieldType.FLOAT}>浮点数</Option>
                <Option value={FieldType.BOOLEAN}>布尔值</Option>
                <Option value={FieldType.DATE}>日期</Option>
                <Option value={FieldType.DATETIME}>日期时间</Option>
                <Option value={FieldType.EMAIL}>电子邮件</Option>
                <Option value={FieldType.PHONE}>电话号码</Option>
                <Option value={FieldType.ENUM}>枚举</Option>
                <Option value={FieldType.OBJECT}>对象</Option>
                <Option value={FieldType.ARRAY}>数组</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label=" " colon={false}>
              <Checkbox
                checked={field.required}
                onChange={(e) => handleFieldChange(index, 'required', e.target.checked)}
              >
                必填字段
              </Checkbox>
            </Form.Item>
          </Col>
        </Row>

        <Form.Item label="描述">
          <Input.TextArea
            value={field.description}
            onChange={(e) => handleFieldChange(index, 'description', e.target.value)}
            placeholder="字段说明"
            rows={2}
          />
        </Form.Item>

        {/* 根据字段类型渲染不同的配置项 */}
        {field.type === FieldType.ENUM && renderEnumValuesInput(field, index)}
        
        {(field.type === FieldType.INTEGER || field.type === FieldType.FLOAT) && 
          renderNumberRangeInputs(field, index)}
          
        {field.type === FieldType.STRING && renderRegexInput(field, index)}

        <Form.Item label="默认值">
          {field.type === FieldType.BOOLEAN ? (
            <Select
              value={field.default !== undefined ? field.default : null}
              onChange={(value) => handleFieldChange(index, 'default', value)}
              allowClear
              style={{ width: '100%' }}
            >
              <Option value={true}>是</Option>
              <Option value={false}>否</Option>
            </Select>
          ) : field.type === FieldType.ENUM && field.enum_values?.length ? (
            <Select
              value={field.default}
              onChange={(value) => handleFieldChange(index, 'default', value)}
              allowClear
              style={{ width: '100%' }}
            >
              {field.enum_values.map((value, i) => (
                <Option key={i} value={value}>{value}</Option>
              ))}
            </Select>
          ) : (
            <Input
              value={field.default !== undefined ? String(field.default) : ''}
              onChange={(e) => handleFieldChange(index, 'default', e.target.value)}
              placeholder="默认值"
            />
          )}
        </Form.Item>
      </Card>
    );
  };

  return (
    <div>
      <Title level={4}>标注字段定义</Title>
      
      {/* 字段列表 */}
      {fields.map((field, index) => renderFieldForm(field, index))}
      
      {/* 添加字段按钮 */}
      <Button 
        type="dashed" 
        block 
        icon={<PlusOutlined />} 
        onClick={handleAddField}
        style={{ marginBottom: 16 }}
      >
        添加字段
      </Button>
      
      {fields.length === 0 && (
        <div style={{ textAlign: 'center', padding: '20px 0', color: '#999' }}>
          尚未定义任何字段，请点击"添加字段"按钮创建
        </div>
      )}
    </div>
  );
};

export default AnnotationFieldEditor; 