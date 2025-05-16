import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Descriptions,
  Button,
  Space,
  Progress,
  Tabs,
  Table,
  Tag,
  Timeline,
  Row,
  Col,
  Divider,
  Modal,
  message,
  Badge,
  Avatar,
  Tooltip,
  Form,
  Input,
  Select,
  DatePicker,
  Checkbox,
  Radio,
  InputNumber,
  Alert,
  List
} from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  UserOutlined,
  FileTextOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  ArrowLeftOutlined,
  SendOutlined,
  FileSearchOutlined,
  CommentOutlined,
  FieldBinaryOutlined,
  CheckOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import api, { taskApi } from '../services/api';
import { FieldType } from '../components/AnnotationFieldEditor/AnnotationFieldEditor';

const { Title, Paragraph, Text } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;
const { TextArea } = Input;

// 任务状态类型
const taskStatuses = [
  { value: 'pending', label: '待处理', color: 'default' },
  { value: 'in_progress', label: '进行中', color: 'processing' },
  { value: 'completed', label: '已完成', color: 'success' },
  { value: 'review', label: '待审核', color: 'warning' },
  { value: 'approved', label: '已通过', color: 'success' },
  { value: 'rejected', label: '已拒绝', color: 'error' },
];

// 任务优先级
const priorities = [
  { value: 'low', label: '低', color: 'default' },
  { value: 'medium', label: '中', color: 'warning' },
  { value: 'high', label: '高', color: 'error' },
];

// 模拟任务数据
const mockTasks = [
  {
    id: 1,
    name: '住院病案首页标注',
    description: '对上传的住院病案首页进行结构化标注',
    status: 'in_progress',
    priority: 'high',
    progress: 45,
    createdAt: '2023-10-01',
    deadline: '2023-10-15',
    assignee: 'user1',
    assigneeName: '张医生',
    documentType: '住院病案',
    documentsCount: 120,
    createdBy: '系统管理员',
    updatedAt: '2023-10-05',
    // 新增字段定义
    annotation_fields: [
      {
        name: 'patient_name',
        label: '患者姓名',
        type: 'string',
        required: true,
        description: '患者的真实姓名'
      },
      {
        name: 'patient_age',
        label: '患者年龄',
        type: 'integer',
        required: true,
        min: 0,
        max: 120,
        description: '患者年龄，0-120之间的整数'
      },
      {
        name: 'gender',
        label: '性别',
        type: 'enum',
        required: true,
        enum_values: ['男', '女', '未知'],
        description: '患者性别'
      },
      {
        name: 'admission_date',
        label: '入院日期',
        type: 'date',
        required: true,
        description: '患者入院日期'
      },
      {
        name: 'discharge_date',
        label: '出院日期',
        type: 'date',
        required: false,
        description: '患者出院日期'
      },
      {
        name: 'diagnosis',
        label: '诊断结果',
        type: 'string',
        required: true,
        description: '患者的诊断结果'
      },
      {
        name: 'is_emergency',
        label: '是否急诊',
        type: 'boolean',
        required: true,
        description: '是否为急诊病例'
      }
    ]
  },
  {
    id: 2,
    name: '门诊病历标注',
    description: '标注门诊病历中的关键信息',
    status: 'pending',
    priority: 'medium',
    progress: 0,
    createdAt: '2023-10-03',
    deadline: '2023-10-20',
    assignee: 'user2',
    assigneeName: '李护士',
    documentType: '门诊病历',
    documentsCount: 85,
    createdBy: '系统管理员',
    updatedAt: '2023-10-03',
  },
  {
    id: 3,
    name: '检验报告审核',
    description: '审核已标注的检验报告数据',
    status: 'review',
    priority: 'medium',
    progress: 78,
    createdAt: '2023-09-25',
    deadline: '2023-10-10',
    assignee: 'user3',
    assigneeName: '王主任',
    documentType: '检验报告',
    documentsCount: 64,
    createdBy: '系统管理员',
    updatedAt: '2023-10-03',
  },
];

// 模拟文档数据
const mockDocuments = [
  {
    id: 1,
    name: '住院病案首页001.xlsx',
    status: 'completed',
    annotatedBy: '张医生',
    annotatedAt: '2023-10-04',
    reviewStatus: 'approved',
    reviewedBy: '王主任',
    reviewedAt: '2023-10-05',
  },
  {
    id: 2,
    name: '住院病案首页002.xlsx',
    status: 'completed',
    annotatedBy: '张医生',
    annotatedAt: '2023-10-04',
    reviewStatus: 'rejected',
    reviewedBy: '王主任',
    reviewedAt: '2023-10-05',
  },
  {
    id: 3,
    name: '住院病案首页003.xlsx',
    status: 'in_progress',
    annotatedBy: '张医生',
    annotatedAt: null,
    reviewStatus: null,
    reviewedBy: null,
    reviewedAt: null,
  },
  {
    id: 4,
    name: '住院病案首页004.xlsx',
    status: 'pending',
    annotatedBy: null,
    annotatedAt: null,
    reviewStatus: null,
    reviewedBy: null,
    reviewedAt: null,
  },
  {
    id: 5,
    name: '住院病案首页005.xlsx',
    status: 'pending',
    annotatedBy: null,
    annotatedAt: null,
    reviewStatus: null,
    reviewedBy: null,
    reviewedAt: null,
  },
];

// 模拟任务历史记录
const mockHistory = [
  {
    id: 1,
    action: '创建任务',
    operator: '系统管理员',
    time: '2023-10-01 09:15:00',
    details: '创建了任务"住院病案首页标注"',
  },
  {
    id: 2,
    action: '上传文档',
    operator: '系统管理员',
    time: '2023-10-01 09:30:00',
    details: '上传了120份文档',
  },
  {
    id: 3,
    action: '分配任务',
    operator: '系统管理员',
    time: '2023-10-01 10:00:00',
    details: '将任务分配给了张医生',
  },
  {
    id: 4,
    action: '标注进行中',
    operator: '张医生',
    time: '2023-10-02 14:30:00',
    details: '开始标注文档',
  },
  {
    id: 5,
    action: '完成标注',
    operator: '张医生',
    time: '2023-10-04 16:45:00',
    details: '完成了2份文档的标注',
  },
  {
    id: 6,
    action: '审核',
    operator: '王主任',
    time: '2023-10-05 11:20:00',
    details: '审核了2份已标注文档，通过1份，拒绝1份',
  },
];

// 模拟评论数据
const mockComments = [
  {
    id: 1,
    user: '张医生',
    content: '已开始处理该任务',
    time: '2023-10-02 14:30:00',
  },
  {
    id: 2,
    user: '系统管理员',
    content: '请注意截止日期是10月15日',
    time: '2023-10-03 09:15:00',
  },
  {
    id: 3,
    user: '张医生',
    content: '有一些文档格式不统一，需要花更多时间处理',
    time: '2023-10-04 10:30:00',
  },
  {
    id: 4,
    user: '王主任',
    content: '已开始审核，部分字段需要修正',
    time: '2023-10-05 11:20:00',
  },
];

// 界面显示的字段类型映射
const fieldTypeMap: Record<string, string> = {
  [FieldType.STRING]: '字符串',
  [FieldType.INTEGER]: '整数',
  [FieldType.FLOAT]: '浮点数',
  [FieldType.BOOLEAN]: '布尔值',
  [FieldType.DATE]: '日期',
  [FieldType.DATETIME]: '日期时间',
  [FieldType.EMAIL]: '电子邮件',
  [FieldType.PHONE]: '电话号码',
  [FieldType.ENUM]: '枚举',
  [FieldType.OBJECT]: '对象',
  [FieldType.ARRAY]: '数组'
};

// 根据字段类型渲染不同的表单控件
const renderFieldControl = (field: any, value: any, onChange: (value: any) => void) => {
  switch (field.type) {
    case FieldType.STRING:
    case FieldType.EMAIL:
    case FieldType.PHONE:
      return (
        <Input
          value={value}
          onChange={e => onChange(e.target.value)}
          placeholder={`请输入${field.label}`}
        />
      );
      
    case FieldType.INTEGER:
    case FieldType.FLOAT:
      return (
        <InputNumber
          style={{ width: '100%' }}
          value={value}
          onChange={value => onChange(value)}
          min={field.min}
          max={field.max}
          placeholder={`请输入${field.label}`}
        />
      );
      
    case FieldType.BOOLEAN:
      return (
        <Radio.Group
          value={value}
          onChange={e => onChange(e.target.value)}
        >
          <Radio value={true}>是</Radio>
          <Radio value={false}>否</Radio>
        </Radio.Group>
      );
      
    case FieldType.DATE:
      return (
        <DatePicker
          style={{ width: '100%' }}
          value={value ? moment(value) : null}
          onChange={date => onChange(date ? date.format('YYYY-MM-DD') : null)}
        />
      );
      
    case FieldType.DATETIME:
      return (
        <DatePicker
          showTime
          style={{ width: '100%' }}
          value={value ? moment(value) : null}
          onChange={date => onChange(date ? date.format('YYYY-MM-DD HH:mm:ss') : null)}
        />
      );
      
    case FieldType.ENUM:
      return (
        <Select
          style={{ width: '100%' }}
          value={value}
          onChange={value => onChange(value)}
          placeholder={`请选择${field.label}`}
        >
          {field.enum_values?.map((option: string) => (
            <Option key={option} value={option}>{option}</Option>
          ))}
        </Select>
      );
      
    default:
      return (
        <Input
          value={value}
          onChange={e => onChange(e.target.value)}
          placeholder={`请输入${field.label}`}
        />
      );
  }
};

const TaskDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('info');
  const [annotationData, setAnnotationData] = useState<Record<string, any>>({});
  const [validationResult, setValidationResult] = useState<any>(null);
  const [validating, setValidating] = useState(false);
  const [canSubmit, setCanSubmit] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    // 模拟加载任务数据
    setLoading(true);
    // 从API加载任务数据
    // 此处使用模拟数据
    setTimeout(() => {
      const foundTask = mockTasks.find(t => t.id === Number(id));
      if (foundTask) {
        setTask(foundTask);
        
        // 初始化标注数据
        const initialData: Record<string, any> = {};
        foundTask.annotation_fields?.forEach(field => {
          initialData[field.name] = field.default || null;
        });
        setAnnotationData(initialData);
      }
      setLoading(false);
    }, 500);
  }, [id]);

  const handleBack = () => {
    navigate('/tasks');
  };

  const handleEdit = () => {
    message.info('编辑功能暂未实现');
  };

  const confirmDelete = () => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除此任务吗？此操作不可恢复。',
      okText: '确认',
      cancelText: '取消',
      onOk: () => {
        message.success('任务已删除');
        navigate('/tasks');
      }
    });
  };

  const handleAddComment = () => {
    message.info('评论功能暂未实现');
  };

  // 处理标注字段值变更
  const handleFieldChange = (fieldName: string, value: any) => {
    setAnnotationData(prev => ({
      ...prev,
      [fieldName]: value
    }));
    
    // 清除之前的验证结果
    setValidationResult(null);
  };

  // 验证标注数据
  const validateAnnotation = async () => {
    const taskId = parseInt(id || '0', 10);
    if (!taskId) {
      message.error('无效的任务ID');
      return;
    }

    // 获取所有字段的值
    const annotationData: Record<string, any> = {};
    task.annotation_fields.forEach((field: any) => {
      annotationData[field.name] = annotationData[field.name] || field.default || null;
    });

    try {
      setValidating(true);
      // 使用新的API进行验证
      const validationResult = await taskApi.validateAnnotation(taskId, annotationData);
      setValidating(false);

      if (validationResult.valid) {
        message.success('验证通过！');
        setValidationResult(null);
        setCanSubmit(true);
      } else {
        setValidationResult({
          valid: false,
          errors: validationResult.errors || []
        });
        message.error('验证失败，请检查错误信息');
        setCanSubmit(false);
      }
    } catch (error) {
      console.error('验证失败:', error);
      message.error('验证过程中发生错误');
      setValidating(false);
      setCanSubmit(false);
    }
  };

  // 验证文档格式
  const validateDocumentFormat = async (documentData: Record<string, any>) => {
    const taskId = parseInt(id || '0', 10);
    if (!taskId) {
      message.error('无效的任务ID');
      return false;
    }

    try {
      const validationResult = await taskApi.validateDocumentFormat(taskId, documentData);
      
      if (validationResult.valid) {
        message.success('文档格式验证通过');
        return true;
      } else {
        Modal.error({
          title: '文档格式验证失败',
          content: (
            <div>
              <p>请检查以下错误：</p>
              <ul>
                {Array.isArray(validationResult.errors) ? (
                  validationResult.errors.map((err: any, index: number) => (
                    <li key={index}>{typeof err === 'string' ? err : JSON.stringify(err)}</li>
                  ))
                ) : (
                  <li>{String(validationResult.errors)}</li>
                )}
              </ul>
            </div>
          )
        });
        return false;
      }
    } catch (error) {
      console.error('文档格式验证失败:', error);
      message.error('文档格式验证过程中发生错误');
      return false;
    }
  };

  // 提交标注数据
  const submitAnnotation = async () => {
    const taskId = parseInt(id || '0', 10);
    if (!taskId) {
      message.error('无效的任务ID');
      return;
    }

    // 获取所有字段的值
    const annotationData: Record<string, any> = {};
    task.annotation_fields.forEach((field: any) => {
      annotationData[field.name] = annotationData[field.name] || field.default || null;
    });

    try {
      setSubmitting(true);
      // 使用新的API存储标注数据
      const result = await taskApi.storeAnnotation(taskId, annotationData);
      setSubmitting(false);

      if (result.success) {
        message.success('标注数据已保存');
        // 刷新任务状态
        fetchTaskDetail();
      } else {
        message.error(result.message || '保存标注数据失败');
      }
    } catch (error) {
      console.error('提交标注失败:', error);
      message.error('提交过程中发生错误');
      setSubmitting(false);
    }
  };

  const getStatusTag = (status: string) => {
    const statusObj = taskStatuses.find(s => s.value === status);
    return (
      <Tag color={statusObj?.color || 'default'}>
        {statusObj?.label || status}
      </Tag>
    );
  };

  const getPriorityTag = (priority: string) => {
    const priorityObj = priorities.find(p => p.value === priority);
    return (
      <Tag color={priorityObj?.color || 'default'}>
        {priorityObj?.label || priority}
      </Tag>
    );
  };

  const getDocumentStatusTag = (status: string) => {
    if (status === 'completed') {
      return <Tag color="success">已标注</Tag>;
    } else if (status === 'in_progress') {
      return <Tag color="processing">标注中</Tag>;
    } else {
      return <Tag>未标注</Tag>;
    }
  };

  const getReviewStatusTag = (status: string | null) => {
    if (!status) {
      return <Tag>未审核</Tag>;
    }
    
    if (status === 'approved') {
      return <Tag color="success">已通过</Tag>;
    } else if (status === 'rejected') {
      return <Tag color="error">已拒绝</Tag>;
    } else {
      return <Tag>未知状态</Tag>;
    }
  };

  if (loading) {
    return <div>加载中...</div>;
  }

  if (!task) {
    return <div>任务不存在</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={handleBack}
        >
          返回列表
        </Button>
      </div>
      
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <Title level={2}>{task.name}</Title>
            <Space>
              {getStatusTag(task.status)}
              {getPriorityTag(task.priority)}
              <Text type="secondary">
                <CalendarOutlined /> 截止日期: {task.deadline}
              </Text>
            </Space>
          </div>
          <Space>
            <Button 
              icon={<EditOutlined />}
              onClick={handleEdit}
            >
              编辑
            </Button>
            <Button 
              danger
              icon={<DeleteOutlined />}
              onClick={confirmDelete}
            >
              删除
            </Button>
          </Space>
        </div>
        
        <Divider />
        
        <Row gutter={16}>
          <Col span={16}>
            <Paragraph>{task.description}</Paragraph>
          </Col>
          <Col span={8}>
            <Card size="small" title="任务进度">
              <Progress percent={task.progress} status="active" />
              <div style={{ textAlign: 'center', marginTop: 8 }}>
                {task.progress < 100 ? (
                  <Text type="secondary">
                    <ClockCircleOutlined /> 进行中
                  </Text>
                ) : (
                  <Text type="success">
                    <CheckCircleOutlined /> 已完成
                  </Text>
                )}
              </div>
            </Card>
          </Col>
        </Row>
      </Card>
      
      <Tabs activeKey={activeTab} onChange={setActiveTab} style={{ marginTop: 16 }}>
        <TabPane tab="任务信息" key="info">
          <Card>
            <Descriptions title="基本信息" bordered column={2}>
              <Descriptions.Item label="任务ID">{task.id}</Descriptions.Item>
              <Descriptions.Item label="状态">{getStatusTag(task.status)}</Descriptions.Item>
              <Descriptions.Item label="创建时间">{task.createdAt}</Descriptions.Item>
              <Descriptions.Item label="截止日期">{task.deadline}</Descriptions.Item>
              <Descriptions.Item label="任务创建者">{task.createdBy}</Descriptions.Item>
              <Descriptions.Item label="最后更新">{task.updatedAt}</Descriptions.Item>
              <Descriptions.Item label="标注人员" span={2}>
                <Avatar icon={<UserOutlined />} size="small" /> {task.assigneeName}
              </Descriptions.Item>
              <Descriptions.Item label="文档类型">{task.documentType}</Descriptions.Item>
              <Descriptions.Item label="文档数量">{task.documentsCount}</Descriptions.Item>
              <Descriptions.Item label="任务描述" span={2}>
                {task.description}
              </Descriptions.Item>
            </Descriptions>
            
            <Divider />
            
            <Title level={4}>标注字段定义</Title>
            <Table 
              dataSource={task.annotation_fields}
              rowKey="name"
              pagination={false}
              columns={[
                {
                  title: '字段名',
                  dataIndex: 'name',
                  key: 'name',
                },
                {
                  title: '显示名称',
                  dataIndex: 'label',
                  key: 'label',
                },
                {
                  title: '类型',
                  dataIndex: 'type',
                  key: 'type',
                  render: (type) => fieldTypeMap[type] || type
                },
                {
                  title: '必填',
                  dataIndex: 'required',
                  key: 'required',
                  render: (required) => required ? 
                    <Badge status="success" text="是" /> : 
                    <Badge status="default" text="否" />
                },
                {
                  title: '描述',
                  dataIndex: 'description',
                  key: 'description',
                }
              ]}
            />
          </Card>
        </TabPane>
        
        <TabPane tab="标注工作区" key="annotate">
          <Card title="标注表单">
            <Form layout="vertical">
              {task.annotation_fields?.map((field: any) => (
                <Form.Item 
                  key={field.name}
                  label={
                    <Space>
                      {field.label}
                      {field.required && <Text type="danger">*</Text>}
                    </Space>
                  }
                  help={field.description}
                  validateStatus={
                    validationResult?.errors?.some((err: any) => err.field === field.name) ? 'error' : undefined
                  }
                  extra={
                    validationResult?.errors?.find((err: any) => err.field === field.name)?.message
                  }
                >
                  {renderFieldControl(
                    field, 
                    annotationData[field.name], 
                    (value) => handleFieldChange(field.name, value)
                  )}
                </Form.Item>
              ))}
              
              <Divider />
              
              <Form.Item>
                <Space>
                  <Button type="primary" onClick={validateAnnotation}>
                    验证数据
                  </Button>
                  <Button type="primary" onClick={submitAnnotation}>
                    提交标注
                  </Button>
                </Space>
              </Form.Item>
              
              {validationResult && (
                <Alert
                  message={validationResult.valid ? "数据验证通过" : "数据验证失败"}
                  description={
                    validationResult.valid ? 
                      "所有字段都符合要求" : 
                      <List
                        size="small"
                        dataSource={validationResult.errors}
                        renderItem={(error: any) => (
                          <List.Item>
                            <Text type="danger">
                              {`${task.annotation_fields.find((f: any) => f.name === error.field)?.label || error.field}: ${error.message}`}
                            </Text>
                          </List.Item>
                        )}
                      />
                  }
                  type={validationResult.valid ? "success" : "error"}
                  showIcon
                  style={{ marginBottom: 16 }}
                />
              )}
            </Form>
          </Card>
        </TabPane>
        
        <TabPane tab="文档列表" key="documents">
          <Card>
            <Table
              dataSource={mockDocuments}
              rowKey="id"
              columns={[
                {
                  title: '文件名',
                  dataIndex: 'name',
                  key: 'name',
                  render: (text) => (
                    <Space>
                      <FileTextOutlined />
                      <Text>{text}</Text>
                    </Space>
                  )
                },
                {
                  title: '标注状态',
                  dataIndex: 'status',
                  key: 'status',
                  render: (status) => getDocumentStatusTag(status)
                },
                {
                  title: '标注人员',
                  dataIndex: 'annotatedBy',
                  key: 'annotatedBy',
                },
                {
                  title: '标注时间',
                  dataIndex: 'annotatedAt',
                  key: 'annotatedAt',
                },
                {
                  title: '审核状态',
                  dataIndex: 'reviewStatus',
                  key: 'reviewStatus',
                  render: (status) => getReviewStatusTag(status)
                },
                {
                  title: '审核人员',
                  dataIndex: 'reviewedBy',
                  key: 'reviewedBy',
                },
                {
                  title: '审核时间',
                  dataIndex: 'reviewedAt',
                  key: 'reviewedAt',
                },
                {
                  title: '操作',
                  key: 'action',
                  render: (_, record) => (
                    <Space>
                      <Button 
                        type="link" 
                        size="small"
                        icon={<FileSearchOutlined />}
                      >
                        查看
                      </Button>
                      {record.status !== 'completed' && (
                        <Button 
                          type="link" 
                          size="small"
                          icon={<EditOutlined />}
                        >
                          标注
                        </Button>
                      )}
                      {record.status === 'completed' && record.reviewStatus !== 'approved' && (
                        <Button 
                          type="link" 
                          size="small"
                          icon={<CommentOutlined />}
                        >
                          审核
                        </Button>
                      )}
                    </Space>
                  )
                },
              ]}
            />
          </Card>
        </TabPane>
        
        <TabPane tab="任务历史" key="history">
          <Card>
            <Timeline mode="left">
              {mockHistory.map(record => (
                <Timeline.Item 
                  key={record.id}
                  label={record.time}
                >
                  <p><strong>{record.action}</strong> - {record.operator}</p>
                  <p>{record.details}</p>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default TaskDetail;