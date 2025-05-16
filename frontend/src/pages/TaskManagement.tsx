import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Table, 
  Button, 
  Space, 
  Card, 
  Tag, 
  Input, 
  Select, 
  Modal, 
  Form, 
  DatePicker, 
  Tooltip, 
  Progress,
  Row,
  Col,
  Divider
} from 'antd';
import { 
  PlusOutlined, 
  SearchOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  EyeOutlined,
  UserOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

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
    documentType: '住院病案',
    documentsCount: 120,
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
    documentType: '门诊病历',
    documentsCount: 85,
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
    documentType: '检验报告',
    documentsCount: 64,
  },
  {
    id: 4,
    name: '影像检查报告标注',
    description: '对影像检查报告进行数据抽取和标注',
    status: 'completed',
    priority: 'low',
    progress: 100,
    createdAt: '2023-09-15',
    deadline: '2023-09-30',
    assignee: 'user1',
    documentType: '影像报告',
    documentsCount: 42,
  },
  {
    id: 5,
    name: '手术记录审核',
    description: '审核已完成的手术记录标注结果',
    status: 'approved',
    priority: 'high',
    progress: 100,
    createdAt: '2023-09-10',
    deadline: '2023-09-25',
    assignee: 'user4',
    documentType: '手术记录',
    documentsCount: 37,
  }
];

// 模拟用户数据
const users = [
  { id: 'user1', name: '张医生' },
  { id: 'user2', name: '李护士' },
  { id: 'user3', name: '王主任' },
  { id: 'user4', name: '赵技师' },
];

// 文档类型
const documentTypes = [
  '住院病案',
  '门诊病历',
  '检验报告',
  '影像报告',
  '手术记录',
  '用药记录',
];

const TaskManagement: React.FC = () => {
  const [tasks, setTasks] = useState(mockTasks);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<[any, any] | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  useEffect(() => {
    // 此处可以从API获取实际任务数据
    // 目前使用mockTasks
  }, []);

  // 处理任务筛选
  const getFilteredTasks = () => {
    return tasks.filter(task => {
      // 文本搜索
      const matchesSearch = searchText === '' || 
        task.name.toLowerCase().includes(searchText.toLowerCase()) ||
        task.description.toLowerCase().includes(searchText.toLowerCase());
      
      // 状态筛选
      const matchesStatus = !statusFilter || task.status === statusFilter;
      
      // 优先级筛选
      const matchesPriority = !priorityFilter || task.priority === priorityFilter;
      
      // 日期范围筛选
      let matchesDate = true;
      if (dateRange && dateRange[0] && dateRange[1]) {
        const taskDate = new Date(task.createdAt);
        const startDate = dateRange[0].toDate();
        const endDate = dateRange[1].toDate();
        matchesDate = taskDate >= startDate && taskDate <= endDate;
      }
      
      return matchesSearch && matchesStatus && matchesPriority && matchesDate;
    });
  };

  // 打开创建任务模态框
  const showCreateModal = () => {
    form.resetFields();
    setIsModalVisible(true);
  };

  // 处理任务创建
  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      // 此处应调用API创建任务
      console.log('创建任务：', values);
      
      // 模拟创建成功
      const newTask = {
        id: tasks.length + 1,
        ...values,
        progress: 0,
        createdAt: new Date().toISOString().split('T')[0],
      };
      
      setTasks([...tasks, newTask]);
      setIsModalVisible(false);
      form.resetFields();
    } catch (error) {
      console.error('表单验证失败：', error);
    }
  };

  // 处理查看任务详情
  const handleViewTask = (id: number) => {
    navigate(`/tasks/${id}`);
  };

  // 获取状态标签颜色
  const getStatusColor = (status: string) => {
    const statusObj = taskStatuses.find(s => s.value === status);
    return statusObj ? statusObj.color : 'default';
  };

  // 获取状态标签文本
  const getStatusLabel = (status: string) => {
    const statusObj = taskStatuses.find(s => s.value === status);
    return statusObj ? statusObj.label : status;
  };

  // 获取优先级标签
  const getPriorityLabel = (priority: string) => {
    const priorityObj = priorities.find(p => p.value === priority);
    return priorityObj ? priorityObj.label : priority;
  };

  // 获取优先级颜色
  const getPriorityColor = (priority: string) => {
    const priorityObj = priorities.find(p => p.value === priority);
    return priorityObj ? priorityObj.color : 'default';
  };

  // 表格列定义
  const columns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: any, b: any) => a.name.localeCompare(b.name),
      render: (text: string, record: any) => (
        <a onClick={() => handleViewTask(record.id)}>{text}</a>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusLabel(status)}
        </Tag>
      ),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: string) => (
        <Tag color={getPriorityColor(priority)}>
          {getPriorityLabel(priority)}
        </Tag>
      ),
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number) => (
        <Progress percent={progress} size="small" />
      ),
    },
    {
      title: '截止日期',
      dataIndex: 'deadline',
      key: 'deadline',
      sorter: (a: any, b: any) => new Date(a.deadline).getTime() - new Date(b.deadline).getTime(),
    },
    {
      title: '负责人',
      dataIndex: 'assignee',
      key: 'assignee',
      render: (assignee: string) => {
        const user = users.find(u => u.id === assignee);
        return user ? user.name : assignee;
      }
    },
    {
      title: '文档数量',
      dataIndex: 'documentsCount',
      key: 'documentsCount',
      sorter: (a: any, b: any) => a.documentsCount - b.documentsCount,
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          <Tooltip title="查看">
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              onClick={() => handleViewTask(record.id)} 
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              disabled={record.status === 'approved'} 
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button 
              type="text" 
              danger 
              icon={<DeleteOutlined />} 
              disabled={record.status === 'in_progress' || record.status === 'approved'} 
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>任务管理</Title>
      <Paragraph>
        创建、管理和追踪文档标注任务的进度和状态。
      </Paragraph>

      {/* 过滤器和搜索栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={24} md={8} lg={6}>
            <Input
              placeholder="搜索任务名称或描述"
              value={searchText}
              onChange={e => setSearchText(e.target.value)}
              prefix={<SearchOutlined />}
              allowClear
            />
          </Col>
          <Col xs={12} sm={12} md={5} lg={4}>
            <Select
              placeholder="状态筛选"
              style={{ width: '100%' }}
              allowClear
              onChange={value => setStatusFilter(value)}
            >
              {taskStatuses.map(status => (
                <Option key={status.value} value={status.value}>
                  {status.label}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={12} sm={12} md={5} lg={4}>
            <Select
              placeholder="优先级筛选"
              style={{ width: '100%' }}
              allowClear
              onChange={value => setPriorityFilter(value)}
            >
              {priorities.map(priority => (
                <Option key={priority.value} value={priority.value}>
                  {priority.label}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={16} md={6} lg={6}>
            <RangePicker 
              style={{ width: '100%' }}
              onChange={value => setDateRange(value)}
            />
          </Col>
          <Col xs={24} sm={8} md={24} lg={4} style={{ textAlign: 'right' }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={showCreateModal}
            >
              创建任务
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 任务列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={getFilteredTasks()}
          rowKey="id"
          loading={loading}
          pagination={{ 
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条任务`
          }}
        />
      </Card>

      {/* 创建任务模态框 */}
      <Modal
        title="创建新任务"
        open={isModalVisible}
        onOk={handleCreate}
        onCancel={() => setIsModalVisible(false)}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="name"
            label="任务名称"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="请输入任务名称" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="任务描述"
            rules={[{ required: true, message: '请输入任务描述' }]}
          >
            <Input.TextArea rows={3} placeholder="请输入任务描述" />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="documentType"
                label="文档类型"
                rules={[{ required: true, message: '请选择文档类型' }]}
              >
                <Select placeholder="请选择文档类型">
                  {documentTypes.map(type => (
                    <Option key={type} value={type}>
                      {type}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="documentsCount"
                label="文档数量"
                rules={[{ required: true, message: '请输入文档数量' }]}
              >
                <Input type="number" min={1} placeholder="请输入文档数量" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="priority"
                label="优先级"
                rules={[{ required: true, message: '请选择优先级' }]}
              >
                <Select placeholder="请选择优先级">
                  {priorities.map(priority => (
                    <Option key={priority.value} value={priority.value}>
                      {priority.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="status"
                label="状态"
                initialValue="pending"
                rules={[{ required: true, message: '请选择状态' }]}
              >
                <Select placeholder="请选择状态">
                  {taskStatuses.map(status => (
                    <Option key={status.value} value={status.value}>
                      {status.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="deadline"
                label="截止日期"
                rules={[{ required: true, message: '请选择截止日期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="assignee"
                label="负责人"
                rules={[{ required: true, message: '请选择负责人' }]}
              >
                <Select placeholder="请选择负责人">
                  {users.map(user => (
                    <Option key={user.id} value={user.id}>
                      {user.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default TaskManagement; 