import React from 'react';
import { Typography, Row, Col, Card, Statistic, Progress, List, Avatar, Divider } from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  FileExclamationOutlined,
  FileSearchOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;

// 模拟统计数据
const statistics = {
  totalDocuments: 485,
  documentsProcessed: 312,
  pendingTasks: 15,
  completedTasks: 42,
  activeUsers: 24,
  errorRate: 3.2,
};

// 模拟最近任务数据
const recentTasks = [
  {
    id: 1,
    name: '住院病案首页标注',
    completionRate: 45,
    status: 'in_progress',
    updatedAt: '2小时前',
    assignee: '张医生',
  },
  {
    id: 2,
    name: '门诊病历标注',
    completionRate: 0,
    status: 'pending',
    updatedAt: '4小时前',
    assignee: '李护士',
  },
  {
    id: 3,
    name: '检验报告审核',
    completionRate: 78,
    status: 'review',
    updatedAt: '昨天',
    assignee: '王主任',
  },
  {
    id: 4,
    name: '影像检查报告标注',
    completionRate: 100,
    status: 'completed',
    updatedAt: '2天前',
    assignee: '张医生',
  },
];

// 模拟最近活动数据
const recentActivities = [
  {
    id: 1,
    user: '张医生',
    action: '完成了标注任务',
    target: '影像检查报告标注',
    time: '1小时前',
  },
  {
    id: 2,
    user: '系统管理员',
    action: '创建了新任务',
    target: '住院病案首页标注',
    time: '2小时前',
  },
  {
    id: 3,
    user: '李护士',
    action: '上传了新文件',
    target: '住院病案首页.xlsx',
    time: '3小时前',
  },
  {
    id: 4,
    user: '王主任',
    action: '审核并通过了',
    target: '检验报告标注结果',
    time: '昨天',
  },
  {
    id: 5,
    user: '系统',
    action: '自动验证失败',
    target: '门诊病历.json',
    time: '昨天',
  },
];

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // 获取状态对应的图标
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'in_progress':
        return <ClockCircleOutlined style={{ color: '#1890ff' }} />;
      case 'review':
        return <FileSearchOutlined style={{ color: '#faad14' }} />;
      default:
        return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  // 处理点击任务
  const handleTaskClick = (id: number) => {
    navigate(`/tasks/${id}`);
  };

  return (
    <div>
      <Title level={2}>系统概况</Title>
      <Paragraph>
        文书标注系统的整体运行状态和关键指标
      </Paragraph>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={8} lg={8} xl={4}>
          <Card>
            <Statistic
              title="文档总数"
              value={statistics.totalDocuments}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={8} xl={4}>
          <Card>
            <Statistic
              title="已处理文档"
              value={statistics.documentsProcessed}
              prefix={<CheckCircleOutlined />}
              suffix={`/ ${statistics.totalDocuments}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={8} xl={4}>
          <Card>
            <Statistic
              title="待处理任务"
              value={statistics.pendingTasks}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={8} xl={4}>
          <Card>
            <Statistic
              title="完成任务"
              value={statistics.completedTasks}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={8} xl={4}>
          <Card>
            <Statistic
              title="活跃用户"
              value={statistics.activeUsers}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={8} xl={4}>
          <Card>
            <Statistic
              title="错误率"
              value={statistics.errorRate}
              precision={1}
              suffix="%"
              prefix={<FileExclamationOutlined />}
              valueStyle={{ color: statistics.errorRate > 5 ? '#cf1322' : '#3f8600' }}
            />
          </Card>
        </Col>
      </Row>

      <Divider />

      {/* 任务和活动 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <Card title="最近任务" extra={<a href="/tasks">查看全部</a>}>
            <List
              itemLayout="horizontal"
              dataSource={recentTasks}
              renderItem={item => (
                <List.Item 
                  key={item.id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => handleTaskClick(item.id)}
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar icon={getStatusIcon(item.status)} />
                    }
                    title={item.name}
                    description={`${item.assignee} · ${item.updatedAt}`}
                  />
                  <div>
                    <Progress percent={item.completionRate} size="small" />
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="最近活动">
            <List
              itemLayout="horizontal"
              dataSource={recentActivities}
              renderItem={item => (
                <List.Item key={item.id}>
                  <List.Item.Meta
                    avatar={<Avatar icon={<UserOutlined />} />}
                    title={`${item.user} ${item.action}`}
                    description={
                      <span>
                        {item.target} · {item.time}
                      </span>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 