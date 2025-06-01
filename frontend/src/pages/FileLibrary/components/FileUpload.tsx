import React, { useState } from 'react'
import { 
  Upload, 
  Button, 
  message, 
  Progress,
  Card,
  Typography,
  Space
} from 'antd'
import { 
  UploadOutlined, 
  InboxOutlined,
  FileTextOutlined,
  CodeOutlined
} from '@ant-design/icons'
import type { UploadProps } from 'antd'
import { fileAPI } from '../../../services/api'
import type { FileItem } from '../../../types'

const { Dragger } = Upload
const { Text } = Typography

interface FileUploadProps {
  type: 'documents' | 'templates'
  accept?: string
  onSuccess?: (file: FileItem) => void
  style?: React.CSSProperties
}

const FileUpload: React.FC<FileUploadProps> = ({
  type,
  accept,
  onSuccess,
  style
}) => {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  // 获取文件类型配置
  const getFileTypeConfig = () => {
    if (type === 'documents') {
      return {
        title: '上传文档文件',
        description: '支持 JSON、JSONL 格式文件',
        icon: <FileTextOutlined style={{ fontSize: 48, color: '#1890ff' }} />,
        acceptTypes: '.json,.jsonl',
        maxSize: 50 // MB
      }
    } else {
      return {
        title: '上传模板文件',
        description: '支持 Python 格式文件',
        icon: <CodeOutlined style={{ fontSize: 48, color: '#52c41a' }} />,
        acceptTypes: '.py',
        maxSize: 10 // MB
      }
    }
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
    const acceptedTypes = (accept || config.acceptTypes).split(',').map(t => t.trim())
    
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
    setUploadProgress(0)

    try {
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 100)

      const response = await fileAPI.uploadFile(file, type)
      
      clearInterval(progressInterval)
      setUploadProgress(100)

      if (response.success && response.data) {
        message.success(`文件 ${file.name} 上传成功`)
        uploadOnSuccess?.(response.data)
        onSuccess?.(response.data)
        
        // 重置状态
        setTimeout(() => {
          setUploading(false)
          setUploadProgress(0)
        }, 1000)
      } else {
        throw new Error(response.message || '上传失败')
      }
    } catch (error: any) {
      console.error('文件上传失败:', error)
      message.error(error.message || '文件上传失败')
      onError?.(error)
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: accept || config.acceptTypes,
    beforeUpload,
    customRequest,
    showUploadList: false,
    disabled: uploading
  }

  return (
    <Card style={style}>
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
              percent={uploadProgress} 
              status={uploadProgress === 100 ? 'success' : 'active'}
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