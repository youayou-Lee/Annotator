import React, { useState } from 'react'
import { 
  Upload, 
  Button, 
  message, 
  Progress,
  Card,
  Typography,
  Space,
  Alert,
  List,
  Tag,
  App
} from 'antd'
import { 
  UploadOutlined, 
  InboxOutlined,
  FileTextOutlined,
  CodeOutlined,
  DeleteOutlined,
  CheckCircleOutlined
} from '@ant-design/icons'
import type { UploadProps } from 'antd'
import { fileAPI } from '../../../services/api'
import type { FileItem } from '../../../types'

const { Dragger } = Upload
const { Text } = Typography

interface FileUploadProps {
  visible: boolean
  type: 'documents' | 'templates' | 'exports'
  onCancel: () => void
  onSuccess: (file: FileItem) => void
}

interface UploadFile {
  uid: string
  name: string
  size: number
  status: 'uploading' | 'done' | 'error'
  progress: number
  response?: any
  error?: string
}

const FileUpload: React.FC<FileUploadProps> = ({
  visible,
  type,
  onCancel,
  onSuccess
}) => {
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)
  const { message } = App.useApp()

  // 获取文件类型配置
  const getFileTypeConfig = () => {
    const configs = {
      documents: {
        title: '上传文档文件',
        description: '支持 JSON、JSONL、TXT、CSV 格式，单个文件不超过 50MB',
        icon: <FileTextOutlined style={{ fontSize: 48, color: '#1890ff' }} />,
        acceptTypes: '.json,.jsonl,.txt,.csv',
        maxSize: 50 // MB
      },
      templates: {
        title: '上传模板文件',
        description: '支持 Python、JSON 格式，单个文件不超过 10MB',
        icon: <CodeOutlined style={{ fontSize: 48, color: '#52c41a' }} />,
        acceptTypes: '.py,.json',
        maxSize: 10 // MB
      },
      exports: {
        title: '上传导出文件',
        description: '支持 JSON、CSV、Excel、ZIP 格式，单个文件不超过 100MB',
        icon: <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />,
        acceptTypes: '.json,.csv,.xlsx,.zip',
        maxSize: 100 // MB
      }
    }
    return configs[type as keyof typeof configs] || configs.documents
  }

  const config = getFileTypeConfig()

  // 文件上传前的校验
  const beforeUpload = (file: File) => {
    // 检查文件大小
    const isLtMaxSize = file.size / 1024 / 1024 < config.maxSize
    if (!isLtMaxSize) {
      message.error(`文件大小不能超过 ${config.maxSize}MB`)
      return false
    }

    // 检查文件类型
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    const acceptedTypes = (config.acceptTypes).split(',').map(t => t.trim())
    
    if (!acceptedTypes.includes(fileExtension)) {
      message.error(`只支持 ${acceptedTypes.join(', ')} 格式的文件`)
      return false
    }

    return true
  }

  // 自定义上传请求
  const customRequest = async (options: any) => {
    const { file, onSuccess: uploadOnSuccess, onError } = options
    
    setUploading(true)
    setUploadFiles([{ uid: '', name: file.name, size: file.size, status: 'uploading', progress: 0 }])

    try {
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadFiles(prev => prev.map(f => ({
          ...f,
          progress: prev.find(ff => ff.name === f.name)?.progress ? 90 : 0
        })))
      }, 100)

      const response = await fileAPI.uploadFile(file, type as 'documents' | 'templates')
      
      clearInterval(progressInterval)
      setUploadFiles(prev => prev.map(f => ({
        ...f,
        status: response.success ? 'done' : 'error',
        response: response.data,
        error: response.message
      })))

      if (response.success && response.data) {
        message.success(`文件 ${file.name} 上传成功`)
        uploadOnSuccess?.(response.data)
        onSuccess?.(response.data)
        
        // 重置状态
        setTimeout(() => {
          setUploading(false)
          setUploadFiles([])
        }, 1000)
      } else {
        throw new Error(response.message || '上传失败')
      }
    } catch (error: any) {
      console.error('文件上传失败:', error)
      message.error(error.message || '文件上传失败')
      onError?.(error)
      setUploading(false)
      setUploadFiles([])
    }
  }

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: config.acceptTypes,
    beforeUpload,
    customRequest,
    showUploadList: false,
    disabled: uploading
  }

  return (
    <Card style={{ display: visible ? 'block' : 'none' }}>
      <div style={{ textAlign: 'center', padding: '20px 0' }}>
        {config.icon}
        <div style={{ marginTop: 16, marginBottom: 16 }}>
          <Text strong style={{ fontSize: 16 }}>
            {config.title}
          </Text>
          <br />
          <Text type="secondary">
            {config.description}
          </Text>
        </div>

        {uploading ? (
          <div style={{ margin: '20px 0' }}>
            <Progress 
              percent={uploadFiles.find(f => f.name === uploadProps.name)?.progress || 0} 
              status={uploadFiles.find(f => f.name === uploadProps.name)?.status === 'done' ? 'success' : 'active'}
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
            />
            <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
              正在上传文件...
            </Text>
          </div>
        ) : (
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Dragger {...uploadProps} style={{ padding: '20px' }}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
              </p>
              <p className="ant-upload-text">
                点击或拖拽文件到此区域上传
              </p>
              <p className="ant-upload-hint">
                支持单个文件上传，文件大小不超过 {config.maxSize}MB
              </p>
            </Dragger>
            
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">或者</Text>
            </div>
            
            <Upload {...uploadProps}>
              <Button icon={<UploadOutlined />} size="large">
                选择文件上传
              </Button>
            </Upload>
          </Space>
        )}
      </div>
    </Card>
  )
}

export default FileUpload 