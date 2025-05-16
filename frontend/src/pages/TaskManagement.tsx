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
  Divider,
  Upload,
  message,
  Tabs,
  Alert,
  Empty,
  Popconfirm,
  Statistic,
  App
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
  ExclamationCircleOutlined,
  UploadOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileExcelOutlined,
  FileUnknownOutlined,
  LoadingOutlined,
  SyncOutlined
} from '@ant-design/icons';
import api, { taskApi } from '../services/api';
import { useNavigate } from 'react-router-dom';
import AnnotationFieldEditor, { AnnotationField } from '../components/AnnotationFieldEditor/AnnotationFieldEditor';
import { RcFile } from 'antd/lib/upload';
import { formatBytes, formatDate } from '../utils/formatters';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { TabPane } = Tabs;

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

// 模拟文档数据
const documents = [
  { id: 1, name: '住院病案首页样本.json', type: 'json', size: '24KB' },
  { id: 2, name: '门诊病历样本.xlsx', type: 'xlsx', size: '85KB' },
  { id: 3, name: '检验报告样本.csv', type: 'csv', size: '64KB' },
  { id: 4, name: '影像报告样本.json', type: 'json', size: '42KB' },
];

const TaskManagement: React.FC = () => {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<[any, any] | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [editingTask, setEditingTask] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('basic');
  const [annotationFields, setAnnotationFields] = useState<AnnotationField[]>([]);
  const [validationTemplate, setValidationTemplate] = useState<RcFile | null>(null);
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();
  const navigate = useNavigate();
  
  // 公共文件库相关状态
  const [publicFiles, setPublicFiles] = useState<{
    documents: any[];
    templates: any[];
    schemas: any[];
    exports: any[];
  }>({
    documents: [],
    templates: [],
    schemas: [],
    exports: []
  });
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [selectedDocumentFile, setSelectedDocumentFile] = useState<any>(null);
  const [selectedTemplateFile, setSelectedTemplateFile] = useState<any>(null);

  // 任务统计数据
  const [taskStats, setTaskStats] = useState({
    total: 0,
    completed: 0,
    inProgress: 0,
    pending: 0,
    review: 0,
    approved: 0,
    rejected: 0,
    overdue: 0
  });

  // 加载公共文件列表
  const loadPublicFiles = async () => {
    setLoadingFiles(true);
    try {
      const response = await api.get('/public/files');
      console.log('公共文件列表:', response);
      setPublicFiles(response);
    } catch (error) {
      console.error('加载公共文件失败:', error);
      message.error('无法加载公共文件列表');
    } finally {
      setLoadingFiles(false);
    }
  };

  // 加载任务列表
  const loadTasks = async () => {
    setLoading(true);
    try {
      const response = await taskApi.getTasks();
      console.log('任务列表:', response);
      setTasks(response);
      
      // 计算任务统计数据
      calculateTaskStats(response);
    } catch (error) {
      console.error('加载任务失败:', error);
      message.error('无法加载任务列表，已使用模拟数据');
      
      // 如果API调用失败，使用模拟数据
      setTasks(mockTasks);
      calculateTaskStats(mockTasks);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 加载任务列表
    loadTasks();
    
    // 加载公共文件列表
    loadPublicFiles();
  }, []);

  // 计算任务统计数据
  const calculateTaskStats = (taskList: any[]) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const stats = {
      total: taskList.length,
      completed: 0,
      inProgress: 0,
      pending: 0,
      review: 0,
      approved: 0,
      rejected: 0,
      overdue: 0
    };
    
    taskList.forEach(task => {
      // 统计不同状态的任务数量
      switch (task.status) {
        case 'completed':
          stats.completed++;
          break;
        case 'in_progress':
          stats.inProgress++;
          break;
        case 'pending':
          stats.pending++;
          break;
        case 'review':
          stats.review++;
          break;
        case 'approved':
          stats.approved++;
          break;
        case 'rejected':
          stats.rejected++;
          break;
      }
      
      // 统计逾期任务
      const deadlineDate = new Date(task.deadline);
      if (deadlineDate < today && task.status !== 'completed' && task.status !== 'approved') {
        stats.overdue++;
      }
    });
    
    setTaskStats(stats);
  };

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
    setAnnotationFields([]);
    setValidationTemplate(null);
    setSelectedDocumentFile(null);
    setSelectedTemplateFile(null);
    setActiveTab('basic');
    setIsModalVisible(true);
  };

  // 获取文件图标
  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    
    switch(extension) {
      case 'txt':
      case 'json':
      case 'jsonl':
        return <FileTextOutlined />;
      case 'pdf':
        return <FilePdfOutlined />;
      case 'xlsx':
      case 'xls':
      case 'csv':
        return <FileExcelOutlined />;
      default:
        return <FileUnknownOutlined />;
    }
  };

  // 处理任务创建
  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      
      if (!selectedDocumentFile) {
        message.error('请从公共文件库选择文档文件');
        return;
      }
      
      // 构建FormData对象
      const formData = new FormData();
      
      // 添加基本字段
      formData.append('document_id', selectedDocumentFile.id || '1'); // 使用文件ID或路径
      formData.append('document_path', selectedDocumentFile.path);
      formData.append('annotator_id', values.annotator_id);
      if (values.reviewer_id) {
        formData.append('reviewer_id', values.reviewer_id);
      }
      formData.append('title', values.name);
      if (values.description) {
        formData.append('description', values.description);
      }
      
      // 添加标注字段定义（JSON字符串）
      formData.append('annotation_fields_json', JSON.stringify(annotationFields));
      
      // 添加验证模板（如果从公共文件库选择了模板文件）
      if (selectedTemplateFile) {
        formData.append('validation_template_path', selectedTemplateFile.path);
      }
      // 或者如果通过上传添加了验证模板
      else if (validationTemplate) {
        formData.append('validation_template', validationTemplate);
      }
      
      try {
        // 调用API创建任务
        const response = await taskApi.createTaskWithSchema(formData);
        
        // 创建成功
        message.success('任务创建成功');
        setIsModalVisible(false);
        
        // 刷新任务列表
        loadTasks();
      } catch (error) {
        console.error('API错误：', error);
        message.error('创建任务失败，请稍后再试');
      }
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

  // 处理验证模板文件上传
  const handleTemplateUpload = (file: RcFile) => {
    // 检查文件类型
    if (file.type !== 'text/x-python' && !file.name.endsWith('.py')) {
      message.error('只支持Python (.py) 文件作为验证模板');
      return false;
    }
    
    setValidationTemplate(file);
    return false; // 阻止自动上传
  };

  // 渲染公共文件列表选择器
  const renderPublicFileSelector = (fileType: 'documents' | 'templates') => {
    const files = publicFiles[fileType] || [];
    const selectedFile = fileType === 'documents' ? selectedDocumentFile : selectedTemplateFile;
    
    return (
      <div>
        {loadingFiles ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <div>加载文件列表中...</div>
          </div>
        ) : files.length === 0 ? (
          <Empty description={`暂无${fileType === 'documents' ? '文档' : '模板'}文件`}>
            <Button 
              type="primary" 
              onClick={() => navigate('/public-files')}
            >
              前往公共文件库上传
            </Button>
          </Empty>
        ) : (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Typography.Text>选择一个{fileType === 'documents' ? '文档' : '模板'}文件:</Typography.Text>
              {selectedFile && (
                <div style={{ marginTop: 8 }}>
                  <Tag color="blue">
                    {getFileIcon(selectedFile.name)} {selectedFile.name}
                  </Tag>
                </div>
              )}
            </div>
            <Table
              dataSource={files}
              rowKey="path"
              size="small"
              pagination={{ pageSize: 5 }}
              onRow={(record) => ({
                onClick: () => {
                  if (fileType === 'documents') {
                    setSelectedDocumentFile(record);
                    form.setFieldsValue({ document_name: record.name });
                  } else {
                    setSelectedTemplateFile(record);
                    form.setFieldsValue({ template_name: record.name });
                  }
                },
                style: { 
                  cursor: 'pointer',
                  backgroundColor: selectedFile && selectedFile.path === record.path ? '#e6f7ff' : undefined 
                }
              })}
              columns={[
                {
                  title: '文件名',
                  dataIndex: 'name',
                  key: 'name',
                  render: (text) => (
                    <Space>
                      {getFileIcon(text)} {text}
                    </Space>
                  )
                },
                {
                  title: '大小',
                  dataIndex: 'size',
                  key: 'size',
                  render: (size) => formatBytes(size)
                },
                {
                  title: '修改时间',
                  dataIndex: 'modified',
                  key: 'modified',
                  render: (time) => formatDate(time)
                }
              ]}
            />
          </div>
        )}
      </div>
    );
  };

  // 处理任务编辑
  const handleEdit = (record: any) => {
    setEditingTask(record);
    editForm.setFieldsValue({
      name: record.name,
      description: record.description,
      status: record.status,
      priority: record.priority,
      deadline: record.deadline ? new Date(record.deadline) : null,
      reviewer_id: record.reviewer_id,
    });
    setIsEditModalVisible(true);
  };

  // 保存编辑后的任务
  const handleEditSave = async () => {
    try {
      const values = await editForm.validateFields();
      
      const taskData = {
        ...values,
        deadline: values.deadline ? values.deadline.format('YYYY-MM-DD') : editingTask.deadline,
      };
      
      try {
        // 调用API更新任务
        await taskApi.updateTask(editingTask.id, taskData);
        
        // 更新成功
        message.success('任务更新成功');
        setIsEditModalVisible(false);
        
        // 刷新任务列表
        loadTasks();
      } catch (error) {
        console.error('API错误：', error);
        message.error('更新任务失败，请稍后再试');
      }
    } catch (error) {
      console.error('表单验证失败：', error);
    }
  };

  // 处理删除任务
  const handleDelete = async (id: number) => {
    try {
      await taskApi.deleteTask(id);
      message.success('任务已删除');
      
      // 刷新任务列表
      loadTasks();
    } catch (error) {
      console.error('删除任务失败：', error);
      message.error('删除任务失败，请稍后再试');
    }
  };

  // 刷新任务列表
  const handleRefresh = () => {
    loadTasks();
  };

  // 渲染任务统计面板
  const renderTaskStats = () => {
    return (
      <Card variant="borderless" style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={6}>
            <Card variant="borderless" style={{ background: '#f0f2f5' }}>
              <Statistic
                title="总任务数"
                value={taskStats.total}
                prefix={<FileTextOutlined />}
              />
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card variant="borderless" style={{ background: '#e6f7ff' }}>
              <Statistic
                title="进行中"
                value={taskStats.inProgress}
                prefix={<ClockCircleOutlined style={{ color: '#1890ff' }} />}
              />
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card variant="borderless" style={{ background: '#f6ffed' }}>
              <Statistic
                title="已完成"
                value={taskStats.completed + taskStats.approved}
                prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} md={6}>
            <Card variant="borderless" style={{ background: '#fff2e8' }}>
              <Statistic
                title="逾期任务"
                value={taskStats.overdue}
                prefix={<ExclamationCircleOutlined style={{ color: '#fa8c16' }} />}
              />
            </Card>
          </Col>
        </Row>
      </Card>
    );
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
      render: (progress: number, record: any) => {
        // 根据不同的状态和进度显示不同颜色
        let strokeColor = '';
        if (record.status === 'completed' || record.status === 'approved') {
          strokeColor = '#52c41a'; // 绿色
        } else if (record.status === 'review') {
          strokeColor = '#faad14'; // 黄色
        } else if (record.status === 'rejected') {
          strokeColor = '#ff4d4f'; // 红色
        } else if (progress < 30) {
          strokeColor = '#1890ff'; // 蓝色
        } else if (progress < 70) {
          strokeColor = '#1890ff'; // 蓝色
        } else {
          strokeColor = '#52c41a'; // 绿色
        }
        
        return (
          <Tooltip title={`${progress}% 完成`}>
            <Progress 
              percent={progress} 
              size="small" 
              strokeColor={strokeColor}
              status={record.status === 'rejected' ? 'exception' : undefined}
            />
          </Tooltip>
        );
      },
      sorter: (a: any, b: any) => a.progress - b.progress
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
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Popconfirm
              title="确定要删除此任务吗?"
              description="删除后无法恢复，请确认。"
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button 
                type="text" 
                danger 
                icon={<DeleteOutlined />} 
                disabled={record.status === 'in_progress' || record.status === 'approved'} 
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <App>
      <div>
        <Title level={2}>任务管理</Title>
        <Paragraph>
          创建、管理和追踪文档标注任务的进度和状态。
        </Paragraph>

        {/* 任务统计信息 */}
        {renderTaskStats()}
        
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
            <Col xs={24} sm={16} md={6} lg={4}>
              <RangePicker 
                style={{ width: '100%' }}
                onChange={value => setDateRange(value)}
              />
            </Col>
            <Col xs={12} sm={4} md={12} lg={2} style={{ textAlign: 'right' }}>
              <Button 
                icon={<SyncOutlined />}
                onClick={handleRefresh}
                title="刷新任务列表"
              >
                刷新
              </Button>
            </Col>
            <Col xs={12} sm={4} md={12} lg={4} style={{ textAlign: 'right' }}>
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
          width={800}
          okText="创建"
          cancelText="取消"
        >
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane tab="基本信息" key="basic">
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
                
                <Divider orientation="left">文档文件</Divider>
                
                <Form.Item
                  label="文档文件选择"
                  required
                  name="document_name"
                  rules={[{ required: true, message: '请选择文档文件' }]}
                >
                  {renderPublicFileSelector('documents')}
                </Form.Item>
                
                <Divider orientation="left">任务分派</Divider>
                
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      name="annotator_id"
                      label="标注人员"
                      rules={[{ required: true, message: '请选择标注人员' }]}
                    >
                      <Select placeholder="请选择标注人员">
                        {users.map(user => (
                          <Option key={user.id} value={user.id}>
                            {user.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      name="reviewer_id"
                      label="审核人员"
                    >
                      <Select placeholder="请选择审核人员" allowClear>
                        {users.map(user => (
                          <Option key={user.id} value={user.id}>
                            {user.name}
                          </Option>
                        ))}
                      </Select>
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
                      name="deadline"
                      label="截止日期"
                      rules={[{ required: true, message: '请选择截止日期' }]}
                    >
                      <DatePicker style={{ width: '100%' }} />
                    </Form.Item>
                  </Col>
                </Row>
              </Form>
            </TabPane>
            
            <TabPane tab="标注字段" key="fields">
              <Alert
                message="设置任务的标注字段"
                description="请定义此任务需要标注的字段。包括字段名称、类型、是否必填等属性。"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />
              
              <AnnotationFieldEditor 
                value={annotationFields}
                onChange={setAnnotationFields}
              />
            </TabPane>
            
            <TabPane tab="验证模板" key="validation">
              <Alert
                message="设置数据验证模板"
                description="上传Python验证脚本，用于验证标注数据的格式和业务规则。脚本需要包含validate_format或validate_data函数。"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />
              
              <Divider orientation="left">从公共文件库选择</Divider>
              
              <Form.Item
                label="验证模板文件选择"
                name="template_name"
              >
                {renderPublicFileSelector('templates')}
              </Form.Item>
              
              <Divider orientation="left">或上传新模板</Divider>
              
              <Upload
                beforeUpload={handleTemplateUpload}
                maxCount={1}
                showUploadList={validationTemplate ? {
                  showPreviewIcon: false,
                  showRemoveIcon: true,
                  removeIcon: <DeleteOutlined onClick={() => setValidationTemplate(null)} />
                } : false}
                fileList={validationTemplate ? [validationTemplate] : []}
              >
                <Button icon={<UploadOutlined />} disabled={!!selectedTemplateFile}>
                  选择Python模板文件
                </Button>
              </Upload>
              {validationTemplate && (
                <div style={{ marginTop: 8 }}>
                  <Typography.Text type="secondary">已选择文件: {validationTemplate.name}</Typography.Text>
                </div>
              )}
            </TabPane>
          </Tabs>
        </Modal>

        {/* 编辑任务模态框 */}
        <Modal
          title="编辑任务"
          open={isEditModalVisible}
          onOk={handleEditSave}
          onCancel={() => setIsEditModalVisible(false)}
          width={600}
          okText="保存"
          cancelText="取消"
        >
          <Form
            form={editForm}
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
                  name="status"
                  label="状态"
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
                  name="reviewer_id"
                  label="审核人员"
                >
                  <Select placeholder="请选择审核人员" allowClear>
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
    </App>
  );
};

export default TaskManagement; 