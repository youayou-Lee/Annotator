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
  Tooltip
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
  CommentOutlined
} from '@ant-design/icons';
import api from '../services/api';

const { Title, Paragraph, Text } = Typography;
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
    assigneeName: '张医生',
    documentType: '住院病案',
    documentsCount: 120,
    createdBy: '系统管理员',
    updatedAt: '2023-10-05',
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

const TaskDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [documents, setDocuments] = useState(mockDocuments);
  const [history, setHistory] = useState(mockHistory);
  const [comments, setComments] = useState(mockComments);
  const [newComment, setNewComment] = useState('');
  const [selectedTab, setSelectedTab] = useState('info');
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);

  useEffect(() => {
    // 在实际应用中，这里应该从API获取任务详情
    const taskId = Number(id);
    const found = mockTasks.find(t => t.id === taskId);
    
    if (found) {
      setTask(found);
    }
    setLoading(false);
  }, [id]);

  // 返回任务列表页
  const handleBack = () => {
    navigate('/tasks');
  };

  // 编辑任务
  const handleEdit = () => {
    message.info(`编辑任务 ${id}`);
  };

  // 确认删除任务
  const confirmDelete = () => {
    message.success(`已删除任务 ${id}`);
    setDeleteModalVisible(false);
    navigate('/tasks');
  };

  // 添加评论
  const handleAddComment = () => {
    if (!newComment.trim()) return;
    
    const newCommentObj = {
      id: comments.length + 1,
      user: '当前用户',
      content: newComment,
      time: new Date().toLocaleString(),
    };
    
    setComments([...comments, newCommentObj]);
    setNewComment('');
    message.success('评论已添加');
  };

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusObj = taskStatuses.find(s => s.value === status);
    return (
      <Tag color={statusObj?.color || 'default'}>
        {statusObj?.label || status}
      </Tag>
    );
  };

  // 获取优先级标签
  const getPriorityTag = (priority: string) => {
    const priorityObj = priorities.find(p => p.value === priority);
    return (
      <Tag color={priorityObj?.color || 'default'}>
        {priorityObj?.label || priority}
      </Tag>
    );
  };

  // 获取文档状态标签
  const getDocumentStatusTag = (status: string) => {
    switch (status) {
      case 'completed':
        return <Tag color="success">已完成</Tag>;
      case 'in_progress':
        return <Tag color="processing">进行中</Tag>;
      case 'pending':
        return <Tag color="default">待处理</Tag>;
      default:
        return <Tag>{status}</Tag>;
    }
  };

  // 获取审核状态标签
  const getReviewStatusTag = (status: string | null) => {
    if (!status) return '-';
    
    switch (status) {
      case 'approved':
        return <Tag color="success">已通过</Tag>;
      case 'rejected':
        return <Tag color="error">已拒绝</Tag>;
      default:
        return <Tag>{status}</Tag>;
    }
  };

  // 文档列表列定义
  const documentsColumns = [
    {
      title: '文档名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <a>{text}</a>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getDocumentStatusTag(status),
    },
    {
      title: '标注人',
      dataIndex: 'annotatedBy',
      key: 'annotatedBy',
      render: (text: string | null) => text || '-',
    },
    {
      title: '标注时间',
      dataIndex: 'annotatedAt',
      key: 'annotatedAt',
      render: (text: string | null) => text || '-',
    },
    {
      title: '审核状态',
      dataIndex: 'reviewStatus',
      key: 'reviewStatus',
      render: (status: string | null) => getReviewStatusTag(status),
    },
    {
      title: '审核人',
      dataIndex: 'reviewedBy',
      key: 'reviewedBy',
      render: (text: string | null) => text || '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          {record.status === 'pending' || record.status === 'in_progress' ? (
            <Button type="link" size="small">
              标注
            </Button>
          ) : null}
          
          {record.status === 'completed' && record.reviewStatus !== 'approved' ? (
            <Button type="link" size="small">
              审核
            </Button>
          ) : null}
          
          <Button type="link" size="small">
            查看
          </Button>
        </Space>
      ),
    },
  ];

  if (loading) {
    return <div>加载中...</div>;
  }

  if (!task) {
    return <div>未找到任务</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={handleBack}
        >
          返回任务列表
        </Button>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={16}>
          <Title level={2} style={{ margin: 0 }}>
            {task.name}
          </Title>
        </Col>
        <Col span={8} style={{ textAlign: 'right' }}>
          <Space>
            <Button
              icon={<EditOutlined />}
              onClick={handleEdit}
              disabled={task.status === 'approved'}
            >
              编辑
            </Button>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={() => setDeleteModalVisible(true)}
              disabled={task.status === 'in_progress' || task.status === 'approved'}
            >
              删除
            </Button>
          </Space>
        </Col>
      </Row>

      <Tabs 
        activeKey={selectedTab} 
        onChange={setSelectedTab}
        style={{ marginBottom: 16 }}
      >
        <TabPane tab="基本信息" key="info" />
        <TabPane tab="文档列表" key="documents" />
        <TabPane tab="历史记录" key="history" />
        <TabPane tab="讨论" key="comments" />
      </Tabs>

      {selectedTab === 'info' && (
        <Card>
          <Row gutter={[16, 16]}>
            <Col span={16}>
              <Descriptions 
                title="任务详情" 
                bordered 
                column={{ xxl: 3, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }}
              >
                <Descriptions.Item label="任务ID">{task.id}</Descriptions.Item>
                <Descriptions.Item label="状态">{getStatusTag(task.status)}</Descriptions.Item>
                <Descriptions.Item label="优先级">{getPriorityTag(task.priority)}</Descriptions.Item>
                <Descriptions.Item label="文档类型">{task.documentType}</Descriptions.Item>
                <Descriptions.Item label="文档数量">{task.documentsCount}</Descriptions.Item>
                <Descriptions.Item label="负责人">{task.assigneeName}</Descriptions.Item>
                <Descriptions.Item label="创建日期">{task.createdAt}</Descriptions.Item>
                <Descriptions.Item label="截止日期">{task.deadline}</Descriptions.Item>
                <Descriptions.Item label="最后更新">{task.updatedAt}</Descriptions.Item>
                <Descriptions.Item label="创建人">{task.createdBy}</Descriptions.Item>
                <Descriptions.Item label="描述" span={3}>
                  {task.description}
                </Descriptions.Item>
              </Descriptions>
            </Col>
            <Col span={8}>
              <Card title="任务进度" variant="borderless">
                <Progress
                  type="circle"
                  percent={task.progress}
                  width={120}
                  format={percent => `${percent}%`}
                  status={task.status === 'rejected' ? 'exception' : undefined}
                />
                <Divider />
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="已完成文档">
                    {Math.round(task.documentsCount * task.progress / 100)} / {task.documentsCount}
                  </Descriptions.Item>
                  <Descriptions.Item label="剩余时间">
                    {(() => {
                      const deadline = new Date(task.deadline);
                      const today = new Date();
                      const diffTime = deadline.getTime() - today.getTime();
                      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                      
                      return diffDays > 0 
                        ? `${diffDays}天` 
                        : <Text type="danger">已过期</Text>;
                    })()}
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>
          </Row>
        </Card>
      )}

      {selectedTab === 'documents' && (
        <Card title={`文档列表 (${documents.length})`}>
          <Table
            columns={documentsColumns}
            dataSource={documents}
            rowKey="id"
            pagination={{ pageSize: 10 }}
          />
        </Card>
      )}

      {selectedTab === 'history' && (
        <Card title="任务历史">
          <Timeline mode="left">
            {history.map(item => (
              <Timeline.Item 
                key={item.id}
                label={item.time}
              >
                <p><strong>{item.action}</strong> - {item.operator}</p>
                <p>{item.details}</p>
              </Timeline.Item>
            ))}
          </Timeline>
        </Card>
      )}

      {selectedTab === 'comments' && (
        <Card title="讨论">
          <div style={{ maxHeight: '400px', overflowY: 'auto', marginBottom: 16 }}>
            {comments.map(comment => (
              <div 
                key={comment.id} 
                style={{ 
                  marginBottom: 16, 
                  background: '#f5f5f5', 
                  padding: 12, 
                  borderRadius: 8 
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                  <Avatar icon={<UserOutlined />} size="small" />
                  <span style={{ fontWeight: 'bold', marginLeft: 8 }}>{comment.user}</span>
                  <span style={{ marginLeft: 16, fontSize: 12, color: '#888' }}>{comment.time}</span>
                </div>
                <div>{comment.content}</div>
              </div>
            ))}
          </div>
          
          <div style={{ display: 'flex', marginBottom: 8 }}>
            <input
              style={{ 
                flex: 1, 
                marginRight: 8, 
                padding: '8px 12px',
                borderRadius: 4,
                border: '1px solid #d9d9d9'
              }}
              placeholder="添加评论..."
              value={newComment}
              onChange={e => setNewComment(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleAddComment()}
            />
            <Button 
              type="primary" 
              icon={<SendOutlined />}
              onClick={handleAddComment}
            >
              发送
            </Button>
          </div>
        </Card>
      )}

      <Modal
        title="确认删除"
        open={deleteModalVisible}
        onOk={confirmDelete}
        onCancel={() => setDeleteModalVisible(false)}
      >
        <p>确定要删除任务"{task.name}"吗？此操作无法撤销。</p>
      </Modal>
    </div>
  );
};

export default TaskDetail;