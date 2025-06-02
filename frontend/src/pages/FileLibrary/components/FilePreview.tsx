import React, { useState, useEffect } from 'react'
import {
  Modal,
  Spin,
  Typography,
  Space,
  Button,
  Tag,
  Descriptions,
  Alert,
  App
} from 'antd'
import {
  DownloadOutlined,
  FileTextOutlined,
  CodeOutlined,
  EyeOutlined,
  CloseOutlined
} from '@ant-design/icons'
import MonacoEditor from '@monaco-editor/react'
import { fileAPI } from '../../../services/api'
import type { FileItem } from '../../../types'

const { Title, Text, Paragraph } = Typography

interface FilePreviewProps {
  visible: boolean
  file: FileItem | null
  onCancel: () => void
}

const FilePreview: React.FC<FilePreviewProps> = ({
  visible,
  file,
  onCancel
}) => {
  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const { message } = App.useApp()

  // 获取文件语言类型
  const getLanguage = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'json':
      case 'jsonl':
        return 'json'
      case 'py':
        return 'python'
      case 'js':
        return 'javascript'
      case 'ts':
        return 'typescript'
      case 'html':
        return 'html'
      case 'css':
        return 'css'
      case 'md':
        return 'markdown'
      case 'xml':
        return 'xml'
      case 'yaml':
      case 'yml':
        return 'yaml'
      default:
        return 'plaintext'
    }
  }

  // 获取文件类型图标
  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'documents':
        return <FileTextOutlined style={{ color: '#1890ff' }} />
      case 'templates':
        return <CodeOutlined style={{ color: '#52c41a' }} />
      case 'exports':
        return <CodeOutlined style={{ color: '#fa8c16' }} />
      default:
        return <FileTextOutlined />
    }
  }

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 格式化JSON内容
  const formatJsonContent = (content: string): string => {
    try {
      // 如果是JSONL格式，逐行格式化
      if (file?.filename.endsWith('.jsonl')) {
        const lines = content.split('\n').filter(line => line.trim())
        const formattedLines = lines.map(line => {
          try {
            return JSON.stringify(JSON.parse(line), null, 2)
          } catch {
            return line
          }
        })
        return formattedLines.join('\n\n')
      } else {
        // 普通JSON格式化
        return JSON.stringify(JSON.parse(content), null, 2)
      }
    } catch {
      return content
    }
  }

  // 加载文件内容
  const loadFileContent = async () => {
    if (!file) return

    setLoading(true)
    setError('')
    setContent('')

    try {
      const response = await fileAPI.previewFile(file.id)
      if (response.success && response.data) {
        let fileContent = response.data.content || ''
        
        // 如果是JSON文件，尝试格式化
        if (file.filename.endsWith('.json') || file.filename.endsWith('.jsonl')) {
          fileContent = formatJsonContent(fileContent)
        }
        
        setContent(fileContent)
      } else {
        setError(response.message || '加载文件内容失败')
      }
    } catch (error: any) {
      console.error('加载文件内容失败:', error)
      setError('加载文件内容失败')
    } finally {
      setLoading(false)
    }
  }

  // 处理文件下载
  const handleDownload = async () => {
    if (!file) return

    try {
      const blob = await fileAPI.downloadFile(file.id)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = file.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      message.success(`文件 ${file.filename} 下载成功`)
    } catch (error) {
      console.error('下载文件失败:', error)
      message.error('下载文件失败')
    }
  }

  // 当文件变化时加载内容
  useEffect(() => {
    if (visible && file) {
      loadFileContent()
    }
  }, [visible, file])

  // 当模态框关闭时清理状态
  useEffect(() => {
    if (!visible) {
      setContent('')
      setError('')
      setLoading(false)
    }
  }, [visible])

  if (!file) return null

  return (
    <Modal
      title={
        <Space>
          {getFileIcon(file.file_type)}
          <span>文件预览</span>
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      width="80%"
      style={{ top: 20 }}
      footer={[
        <Button key="download" icon={<DownloadOutlined />} onClick={handleDownload}>
          下载文件
        </Button>,
        <Button key="close" onClick={onCancel}>
          关闭
        </Button>
      ]}
    >
      <div style={{ marginBottom: 16 }}>
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <div>
            <Text strong>{file.filename}</Text>
            <Tag color="blue" style={{ marginLeft: 8 }}>
              {formatFileSize(file.file_size)}
            </Tag>
          </div>
          
          <Text type="secondary">
            文件路径: {file.file_path}
          </Text>
        </Space>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text type="secondary">正在加载文件内容...</Text>
          </div>
        </div>
      ) : error ? (
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" onClick={loadFileContent}>
              重试
            </Button>
          }
        />
      ) : (
        <div style={{ border: '1px solid #d9d9d9', borderRadius: 6 }}>
          <MonacoEditor
            height="500px"
            language={getLanguage(file.filename)}
            value={content}
            options={{
              readOnly: true,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              fontSize: 14,
              lineNumbers: 'on',
              wordWrap: 'on',
              automaticLayout: true,
              theme: 'vs-light',
              // 禁用所有可能触发网络请求的功能
              quickSuggestions: false,
              suggestOnTriggerCharacters: false,
              acceptSuggestionOnEnter: 'off',
              tabCompletion: 'off',
              wordBasedSuggestions: 'off',
              parameterHints: { enabled: false },
              hover: { enabled: false },
              links: false,
              colorDecorators: false,
              codeLens: false,
              contextmenu: false
            }}
          />
        </div>
      )}
    </Modal>
  )
}

export default FilePreview 