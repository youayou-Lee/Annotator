import React, { useState } from 'react'
import {
  Layout,
  Card,
  Typography,
  Button,
  Space,
  Tag,
  Timeline,
  Modal,
  Form,
  Input,
  message,
  Badge,
  Spin,
  Alert,
  Breadcrumb,
  Radio,
  Descriptions,
  Row,
  Col
} from 'antd'
import {
  CheckOutlined,
  CloseOutlined,
  HistoryOutlined,
  DiffOutlined,
  ArrowLeftOutlined,
  EditOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import MonacoEditor from '@monaco-editor/react'
import { taskAPI, annotationAPI, reviewAPI } from '../../services/api'
import { ReviewData, ReviewRequest } from '../../types'

const { Content, Sider } = Layout
const { Title, Text } = Typography
const { TextArea } = Input

interface DiffItem {
  path: string
  original: any
  annotated: any
  type: 'added' | 'modified' | 'deleted' | 'unchanged'
}

const Review: React.FC = () => {
  const { taskId, documentId } = useParams<{ taskId: string; documentId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form] = Form.useForm()
  
  const [viewMode, setViewMode] = useState<'side-by-side' | 'unified'>('side-by-side')
  const [reviewModalVisible, setReviewModalVisible] = useState(false)
  const [historyModalVisible, setHistoryModalVisible] = useState(false)
  const [selectedDiff, setSelectedDiff] = useState<DiffItem | null>(null)

  // 获取任务详情
  const { data: taskResponse, isLoading: taskLoading } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => taskAPI.getTask(taskId!),
    enabled: !!taskId
  })

  const task = taskResponse?.data

  // 获取标注数据
  const { data: annotationResponse, isLoading: annotationLoading } = useQuery({
    queryKey: ['annotation', taskId, documentId],
    queryFn: () => annotationAPI.getAnnotation(taskId!, documentId!),
    enabled: !!taskId && !!documentId
  })

  const annotation = annotationResponse?.data

  // 获取复审数据
  const { data: reviewResponse, isLoading: reviewLoading } = useQuery({
    queryKey: ['review', taskId, documentId],
    queryFn: () => reviewAPI.getReview(taskId!, documentId!),
    enabled: !!taskId && !!documentId
  })

  const review = reviewResponse?.data as ReviewData | undefined

  // 提交复审
  const submitReviewMutation = useMutation({
    mutationFn: (data: ReviewRequest) => reviewAPI.submitReview(taskId!, documentId!, data),
    onSuccess: () => {
      message.success('复审提交成功')
      setReviewModalVisible(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['review', taskId, documentId] })
      queryClient.invalidateQueries({ queryKey: ['task', taskId] })
    },
    onError: () => {
      message.error('复审提交失败')
    }
  })

  // 获取当前文档
  const currentDocument = task?.documents.find(doc => doc.id === documentId)

  // 计算差异
  const calculateDiffs = (original: any, annotated: any, path = ''): DiffItem[] => {
    const diffs: DiffItem[] = []
    
    const originalKeys = Object.keys(original || {})
    const annotatedKeys = Object.keys(annotated || {})
    const allKeys = [...new Set([...originalKeys, ...annotatedKeys])]

    allKeys.forEach(key => {
      const currentPath = path ? `${path}.${key}` : key
      const originalValue = original?.[key]
      const annotatedValue = annotated?.[key]

      if (originalValue === undefined && annotatedValue !== undefined) {
        diffs.push({
          path: currentPath,
          original: undefined,
          annotated: annotatedValue,
          type: 'added'
        })
      } else if (originalValue !== undefined && annotatedValue === undefined) {
        diffs.push({
          path: currentPath,
          original: originalValue,
          annotated: undefined,
          type: 'deleted'
        })
      } else if (JSON.stringify(originalValue) !== JSON.stringify(annotatedValue)) {
        if (typeof originalValue === 'object' && typeof annotatedValue === 'object') {
          diffs.push(...calculateDiffs(originalValue, annotatedValue, currentPath))
        } else {
          diffs.push({
            path: currentPath,
            original: originalValue,
            annotated: annotatedValue,
            type: 'modified'
          })
        }
      } else {
        diffs.push({
          path: currentPath,
          original: originalValue,
          annotated: annotatedValue,
          type: 'unchanged'
        })
      }
    })

    return diffs
  }

  const diffs = annotation ? calculateDiffs(annotation.original_data, annotation.annotated_data) : []
  const changedDiffs = diffs.filter(diff => diff.type !== 'unchanged')

  // 处理复审提交
  const handleReviewSubmit = async (values: any) => {
    const reviewData: ReviewRequest = {
      status: values.status,
      comments: values.comments
    }
    submitReviewMutation.mutate(reviewData)
  }

  // 获取差异类型的颜色和图标
  const getDiffTypeConfig = (type: string) => {
    switch (type) {
      case 'added':
        return { color: 'green', icon: '+', bgColor: '#f6ffed', borderColor: '#b7eb8f' }
      case 'deleted':
        return { color: 'red', icon: '-', bgColor: '#fff2f0', borderColor: '#ffccc7' }
      case 'modified':
        return { color: 'orange', icon: '~', bgColor: '#fffbe6', borderColor: '#ffe58f' }
      default:
        return { color: 'default', icon: '=', bgColor: '#fafafa', borderColor: '#d9d9d9' }
    }
  }

  // 渲染差异值
  const renderDiffValue = (value: any) => {
    if (value === undefined) return <Text type="secondary">未定义</Text>
    if (value === null) return <Text type="secondary">null</Text>
    if (typeof value === 'object') return <Text code>{JSON.stringify(value, null, 2)}</Text>
    return <Text>{String(value)}</Text>
  }

  if (taskLoading || annotationLoading || reviewLoading) {
    return (
      <div className="page-container">
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>加载复审数据中...</Text>
          </div>
        </div>
      </div>
    )
  }

  if (!task || !currentDocument || !annotation) {
    return (
      <div className="page-container">
        <Alert
          message="加载失败"
          description="无法加载任务、文档或标注信息"
          type="error"
          showIcon
        />
      </div>
    )
  }

  // 检查是否已复审
  const isReviewed = review && (review.status === 'approved' || review.status === 'rejected')

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部导航栏 */}
      <div style={{ 
        padding: '16px 24px', 
        borderBottom: '1px solid #f0f0f0',
        background: '#fff'
      }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate(`/tasks/${taskId}`)}
              >
                返回任务
              </Button>
              <Breadcrumb>
                <Breadcrumb.Item>{task.name}</Breadcrumb.Item>
                <Breadcrumb.Item>{currentDocument.filename}</Breadcrumb.Item>
                <Breadcrumb.Item>复审</Breadcrumb.Item>
              </Breadcrumb>
            </Space>
          </Col>
          <Col>
            <Space>
              <Radio.Group value={viewMode} onChange={(e) => setViewMode(e.target.value)}>
                <Radio.Button value="side-by-side">并排对比</Radio.Button>
                <Radio.Button value="unified">统一视图</Radio.Button>
              </Radio.Group>
              <Button
                icon={<HistoryOutlined />}
                onClick={() => setHistoryModalVisible(true)}
              >
                查看历史
              </Button>
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => setReviewModalVisible(true)}
                disabled={isReviewed}
              >
                {isReviewed ? '已复审' : '开始复审'}
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 主要内容区域 */}
      <Layout style={{ flex: 1 }}>
        {/* 左侧差异列表 */}
        <Sider
          width={320}
          style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}
        >
          <div style={{ padding: '16px' }}>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={5} style={{ margin: 0 }}>
                变更列表 
                <Badge count={changedDiffs.length} style={{ marginLeft: 8 }} />
              </Title>
            </div>
            
            <div style={{ maxHeight: 'calc(100vh - 200px)', overflow: 'auto' }}>
              {changedDiffs.map((diff, index) => {
                const config = getDiffTypeConfig(diff.type)
                return (
                  <Card
                    key={index}
                    size="small"
                    style={{
                      marginBottom: 8,
                      cursor: 'pointer',
                      borderColor: selectedDiff === diff ? '#1890ff' : config.borderColor,
                      backgroundColor: selectedDiff === diff ? '#e6f7ff' : config.bgColor
                    }}
                    onClick={() => setSelectedDiff(diff)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
                      <Tag color={config.color} style={{ margin: 0, marginRight: 8 }}>
                        {config.icon}
                      </Tag>
                      <Text strong style={{ fontSize: 12 }}>{diff.path}</Text>
                    </div>
                    <div style={{ fontSize: 11, color: '#666' }}>
                      {diff.type === 'added' && '新增字段'}
                      {diff.type === 'deleted' && '删除字段'}
                      {diff.type === 'modified' && '修改字段'}
                    </div>
                  </Card>
                )
              })}
              
              {changedDiffs.length === 0 && (
                <div style={{ textAlign: 'center', padding: '20px 0', color: '#999' }}>
                  <Text type="secondary">没有发现变更</Text>
                </div>
              )}
            </div>
          </div>
        </Sider>

        {/* 右侧对比视图 */}
        <Content style={{ background: '#fff' }}>
          <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
            {viewMode === 'side-by-side' ? (
              <Row gutter={16} style={{ flex: 1 }}>
                <Col span={12}>
                  <Card title="原始数据" size="small" style={{ height: '100%' }}>
                    <div style={{ height: 'calc(100vh - 300px)' }}>
                      <MonacoEditor
                        height="100%"
                        language="json"
                        value={JSON.stringify(annotation.original_data, null, 2)}
                        options={{
                          readOnly: true,
                          minimap: { enabled: false },
                          scrollBeyondLastLine: false,
                          fontSize: 12,
                          lineNumbers: 'on',
                          folding: true,
                          wordWrap: 'on'
                        }}
                        theme="vs"
                      />
                    </div>
                  </Card>
                </Col>
                <Col span={12}>
                  <Card title="标注数据" size="small" style={{ height: '100%' }}>
                    <div style={{ height: 'calc(100vh - 300px)' }}>
                      <MonacoEditor
                        height="100%"
                        language="json"
                        value={JSON.stringify(annotation.annotated_data, null, 2)}
                        options={{
                          readOnly: true,
                          minimap: { enabled: false },
                          scrollBeyondLastLine: false,
                          fontSize: 12,
                          lineNumbers: 'on',
                          folding: true,
                          wordWrap: 'on'
                        }}
                        theme="vs"
                      />
                    </div>
                  </Card>
                </Col>
              </Row>
            ) : (
              <Card title="详细差异" size="small" style={{ flex: 1 }}>
                {selectedDiff ? (
                  <div>
                    <Descriptions column={1} size="small" bordered>
                      <Descriptions.Item label="字段路径">
                        <Text code>{selectedDiff.path}</Text>
                      </Descriptions.Item>
                      <Descriptions.Item label="变更类型">
                        <Tag color={getDiffTypeConfig(selectedDiff.type).color}>
                          {selectedDiff.type === 'added' && '新增'}
                          {selectedDiff.type === 'deleted' && '删除'}
                          {selectedDiff.type === 'modified' && '修改'}
                        </Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="原始值">
                        {renderDiffValue(selectedDiff.original)}
                      </Descriptions.Item>
                      <Descriptions.Item label="标注值">
                        {renderDiffValue(selectedDiff.annotated)}
                      </Descriptions.Item>
                    </Descriptions>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '50px 0', color: '#999' }}>
                    <DiffOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                    <div>请从左侧选择一个变更项查看详情</div>
                  </div>
                )}
              </Card>
            )}
          </div>
        </Content>
      </Layout>

      {/* 复审状态栏 */}
      {review && (
        <div style={{
          padding: '12px 24px',
          borderTop: '1px solid #f0f0f0',
          background: review.status === 'approved' ? '#f6ffed' : review.status === 'rejected' ? '#fff2f0' : '#fff'
        }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Space>
                <Text strong>复审状态:</Text>
                <Tag color={review.status === 'approved' ? 'green' : review.status === 'rejected' ? 'red' : 'orange'}>
                  {review.status === 'approved' && '已通过'}
                  {review.status === 'rejected' && '已拒绝'}
                </Tag>
                {review.comments && (
                  <Text type="secondary">备注: {review.comments}</Text>
                )}
              </Space>
            </Col>
            <Col>
              <Text type="secondary">
                复审时间: {review.reviewed_at ? new Date(review.reviewed_at).toLocaleString() : '未复审'}
              </Text>
            </Col>
          </Row>
        </div>
      )}

      {/* 复审模态框 */}
      <Modal
        title="提交复审"
        open={reviewModalVisible}
        onCancel={() => setReviewModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleReviewSubmit}
        >
          <Form.Item
            name="status"
            label="复审结果"
            rules={[{ required: true, message: '请选择复审结果' }]}
          >
            <Radio.Group>
              <Radio value="approved">
                <Space>
                  <CheckOutlined style={{ color: '#52c41a' }} />
                  通过
                </Space>
              </Radio>
              <Radio value="rejected">
                <Space>
                  <CloseOutlined style={{ color: '#ff4d4f' }} />
                  拒绝
                </Space>
              </Radio>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="comments"
            label="复审备注"
            rules={[{ required: true, message: '请输入复审备注' }]}
          >
            <TextArea
              rows={4}
              placeholder="请输入复审意见和建议..."
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={submitReviewMutation.isPending}
              >
                提交复审
              </Button>
              <Button onClick={() => setReviewModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 历史记录模态框 */}
      <Modal
        title="标注历史"
        open={historyModalVisible}
        onCancel={() => setHistoryModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setHistoryModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        <Timeline>
          <Timeline.Item color="blue">
            <Text strong>文档创建</Text>
            <br />
            <Text type="secondary">{new Date(annotation.updated_at).toLocaleString()}</Text>
          </Timeline.Item>
          <Timeline.Item color="green">
            <Text strong>开始标注</Text>
            <br />
            <Text type="secondary">标注员: {annotation.annotator_id}</Text>
          </Timeline.Item>
          {annotation.status === 'completed' && (
            <Timeline.Item color="green">
              <Text strong>标注完成</Text>
              <br />
              <Text type="secondary">{new Date(annotation.updated_at).toLocaleString()}</Text>
            </Timeline.Item>
          )}
          {review && (
            <Timeline.Item color={review.status === 'approved' ? 'green' : 'red'}>
              <Text strong>复审{review.status === 'approved' ? '通过' : '拒绝'}</Text>
              <br />
              <Text type="secondary">
                复审员: {review.reviewer_id} | {review.reviewed_at ? new Date(review.reviewed_at).toLocaleString() : ''}
              </Text>
              {review.comments && (
                <>
                  <br />
                  <Text>备注: {review.comments}</Text>
                </>
              )}
            </Timeline.Item>
          )}
        </Timeline>
      </Modal>
    </div>
  )
}

export default Review 