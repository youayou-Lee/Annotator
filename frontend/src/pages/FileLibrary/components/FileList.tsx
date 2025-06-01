import React from 'react'
import {
  Table,
  Button,
  Space,
  Tag,
  Tooltip,
  Popconfirm,
  Typography,
  Empty
} from 'antd'
import {
  EyeOutlined,
  DownloadOutlined,
  DeleteOutlined,
  FileTextOutlined,
  CodeOutlined,
  ExportOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import type { FileItem, User } from '../../../types'

const { Text } = Typography

interface FileListProps {
  files: FileItem[]
  loading: boolean
  selectedFiles: string[]
  onSelectionChange: (selectedRowKeys: string[]) => void
  onPreview: (file: FileItem) => void
  onDownload: (file: FileItem) => void
  onDelete: (fileId: string) => void
  canDelete: (file: FileItem) => boolean
  user: User | null
  readonly?: boolean
}

const FileList: React.FC<FileListProps> = ({
  files,
  loading,
  selectedFiles,
  onSelectionChange,
  onPreview,
  onDownload,
  onDelete,
  canDelete,
  readonly = false
}) => {
  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 获取文件类型图标
  const getFileIcon = (fileType: string, filename: string) => {
    if (fileType === 'documents') {
      return <FileTextOutlined style={{ color: '#1890ff' }} />
    } else if (fileType === 'templates') {
      return <CodeOutlined style={{ color: '#52c41a' }} />
    } else if (fileType === 'exports') {
      return <ExportOutlined style={{ color: '#fa8c16' }} />
    }
    
    // 根据文件扩展名判断
    const ext = filename.split('.').pop()?.toLowerCase()
    if (ext === 'json' || ext === 'jsonl') {
      return <FileTextOutlined style={{ color: '#1890ff' }} />
    } else if (ext === 'py') {
      return <CodeOutlined style={{ color: '#52c41a' }} />
    }
    
    return <FileTextOutlined />
  }

  // 获取文件类型标签
  const getFileTypeTag = (fileType: string) => {
    const typeConfig = {
      documents: { color: 'blue', text: '文档' },
      templates: { color: 'green', text: '模板' },
      exports: { color: 'orange', text: '导出' }
    }
    
    const config = typeConfig[fileType as keyof typeof typeConfig]
    return config ? (
      <Tag color={config.color}>{config.text}</Tag>
    ) : (
      <Tag>{fileType}</Tag>
    )
  }

  // 表格列定义
  const columns: ColumnsType<FileItem> = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      ellipsis: true,
      render: (filename: string, record: FileItem) => (
        <Space>
          {getFileIcon(record.file_type, filename)}
          <Tooltip title={filename}>
            <Text strong>{filename}</Text>
          </Tooltip>
        </Space>
      )
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
      width: 80,
      render: (fileType: string) => getFileTypeTag(fileType)
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => (
        <Text type="secondary">{formatFileSize(size)}</Text>
      ),
      sorter: (a, b) => a.file_size - b.file_size
    },
    {
      title: '上传时间',
      dataIndex: 'uploaded_at',
      key: 'uploaded_at',
      width: 160,
      render: (uploadedAt: string) => (
        <Tooltip title={dayjs(uploadedAt).format('YYYY-MM-DD HH:mm:ss')}>
          <Text type="secondary">
            {dayjs(uploadedAt).format('MM-DD HH:mm')}
          </Text>
        </Tooltip>
      ),
      sorter: (a, b) => dayjs(a.uploaded_at).unix() - dayjs(b.uploaded_at).unix()
    },
    {
      title: '操作',
      key: 'actions',
      width: 160,
      render: (_, record: FileItem) => (
        <Space size="small">
          <Tooltip title="预览">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => onPreview(record)}
            />
          </Tooltip>
          
          <Tooltip title="下载">
            <Button
              type="text"
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => onDownload(record)}
            />
          </Tooltip>
          
          {!readonly && canDelete(record) && (
            <Tooltip title="删除">
              <Popconfirm
                title="确认删除"
                description={`确定要删除文件 "${record.filename}" 吗？`}
                onConfirm={() => onDelete(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button
                  type="text"
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                />
              </Popconfirm>
            </Tooltip>
          )}
        </Space>
      )
    }
  ]

  // 行选择配置
  const rowSelection = {
    selectedRowKeys: selectedFiles,
    onChange: (selectedRowKeys: React.Key[]) => {
      onSelectionChange(selectedRowKeys as string[])
    },
    getCheckboxProps: (record: FileItem) => ({
      disabled: false,
      name: record.filename,
    }),
  }

  return (
    <div>
      <Table<FileItem>
        columns={columns}
        dataSource={files}
        rowKey="id"
        loading={loading}
        rowSelection={rowSelection}
        pagination={{
          total: files.length,
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) =>
            `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
        }}
        locale={{
          emptyText: (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="暂无文件"
            />
          )
        }}
        size="middle"
        scroll={{ x: 800 }}
      />
    </div>
  )
}

export default FileList 