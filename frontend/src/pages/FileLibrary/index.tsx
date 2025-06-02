import React, { useState, useEffect } from 'react'
import { 
  Card, 
  Tabs, 
  message, 
  Typography,
  Space,
  Button,
  Input,
  Select,
  Row,
  Col,
  Layout,
  App
} from 'antd'
import { 
  FileTextOutlined, 
  CodeOutlined, 
  DownloadOutlined,
  SearchOutlined,
  ReloadOutlined,
  UploadOutlined,
  DeleteOutlined,
  EyeOutlined,
  FolderOutlined,
  MoreOutlined,
  CloudUploadOutlined,
  FileOutlined
} from '@ant-design/icons'
import { useAuthStore } from '../../stores/authStore'
import { fileAPI } from '../../services/api'
import type { FileItem } from '../../types'
import FileUpload from './components/FileUpload'
import FileList from './components/FileList'
import FilePreview from './components/FilePreview'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

const { Title, Text } = Typography
const { Content } = Layout
const { TabPane } = Tabs
const { Search } = Input
const { Option } = Select

interface FileLibraryState {
  documents: FileItem[]
  templates: FileItem[]
  exports: FileItem[]
  loading: {
    documents: boolean
    templates: boolean
    exports: boolean
  }
  searchTerm: string
  sortBy: 'filename' | 'file_size' | 'uploaded_at'
  sortOrder: 'asc' | 'desc'
  selectedFiles: string[]
  previewFile: FileItem | null
  previewVisible: boolean
}

const FileLibrary: React.FC = () => {
  const queryClient = useQueryClient()
  const { user, hasPermission } = useAuthStore()
  const { message: appMessage } = App.useApp()
  const [activeTab, setActiveTab] = useState<string>('documents')
  const [state, setState] = useState<FileLibraryState>({
    documents: [],
    templates: [],
    exports: [],
    loading: {
      documents: false,
      templates: false,
      exports: false
    },
    searchTerm: '',
    sortBy: 'uploaded_at',
    sortOrder: 'desc',
    selectedFiles: [],
    previewFile: null,
    previewVisible: false
  })

  // 加载文件列表
  const loadFiles = async (type: 'documents' | 'templates' | 'exports') => {
    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, [type]: true }
    }))

    try {
      const response = await fileAPI.getFiles(type)
      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          [type]: response.data,
          loading: { ...prev.loading, [type]: false }
        }))
      } else {
        appMessage.error(response.message || `加载${getTypeLabel(type)}失败`)
        setState(prev => ({
          ...prev,
          loading: { ...prev.loading, [type]: false }
        }))
      }
    } catch (error) {
      console.error(`加载${type}文件失败:`, error)
      appMessage.error(`加载${getTypeLabel(type)}失败`)
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, [type]: false }
      }))
    }
  }

  // 获取类型标签
  const getTypeLabel = (type: string) => {
    const labels = {
      documents: '文档文件',
      templates: '模板文件',
      exports: '导出文件'
    }
    return labels[type as keyof typeof labels] || type
  }

  // 刷新当前标签页的文件列表
  const refreshFiles = () => {
    loadFiles(activeTab as 'documents' | 'templates' | 'exports')
  }

  // 处理文件上传成功
  const handleUploadSuccess = (file: FileItem) => {
    appMessage.success(`文件 ${file.filename} 上传成功`)
    refreshFiles()
  }

  // 处理文件删除
  const handleFileDelete = async (fileId: string) => {
    try {
      const response = await fileAPI.deleteFile(fileId)
      if (response.success) {
        appMessage.success('文件删除成功')
        refreshFiles()
      } else {
        appMessage.error(response.message || '删除文件失败')
      }
    } catch (error) {
      console.error('删除文件失败:', error)
      appMessage.error('删除文件失败')
    }
  }

  // 处理文件下载
  const handleFileDownload = async (file: FileItem) => {
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
      appMessage.success(`文件 ${file.filename} 下载成功`)
    } catch (error) {
      console.error('下载文件失败:', error)
      appMessage.error('下载文件失败')
    }
  }

  // 处理文件预览
  const handleFilePreview = (file: FileItem) => {
    setState(prev => ({
      ...prev,
      previewFile: file,
      previewVisible: true
    }))
  }

  // 处理批量下载
  const handleBatchDownload = async () => {
    if (state.selectedFiles.length === 0) {
      appMessage.warning('请选择要下载的文件')
      return
    }

    const currentFiles = state[activeTab as keyof Pick<FileLibraryState, 'documents' | 'templates' | 'exports'>] as FileItem[]
    const filesToDownload = currentFiles.filter(file => state.selectedFiles.includes(file.id))

    for (const file of filesToDownload) {
      try {
        await handleFileDownload(file)
      } catch (error) {
        console.error(`下载文件 ${file.filename} 失败:`, error)
      }
    }
  }

  // 处理批量删除
  const handleBatchDelete = async () => {
    if (state.selectedFiles.length === 0) {
      appMessage.warning('请选择要删除的文件')
      return
    }

    for (const fileId of state.selectedFiles) {
      try {
        await handleFileDelete(fileId)
      } catch (error) {
        console.error(`删除文件失败:`, error)
      }
    }

    setState(prev => ({ ...prev, selectedFiles: [] }))
  }

  // 过滤和排序文件
  const getFilteredAndSortedFiles = (files: FileItem[]) => {
    let filtered = files

    // 搜索过滤
    if (state.searchTerm) {
      filtered = filtered.filter(file =>
        file.filename.toLowerCase().includes(state.searchTerm.toLowerCase())
      )
    }

    // 排序
    filtered = sortFiles(filtered)

    return filtered
  }

  // 排序文件
  const sortFiles = (files: FileItem[]): FileItem[] => {
    return [...files].sort((a, b) => {
      let aValue: any
      let bValue: any

      if (state.sortBy === 'filename') {
        aValue = a.filename.toLowerCase()
        bValue = b.filename.toLowerCase()
      } else if (state.sortBy === 'file_size') {
        aValue = a.file_size
        bValue = b.file_size
      } else if (state.sortBy === 'uploaded_at') {
        aValue = new Date(a.uploaded_at).getTime()
        bValue = new Date(b.uploaded_at).getTime()
      }

      if (state.sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })
  }

  // 检查用户权限
  const canUpload = (type: string) => {
    if (type === 'exports') return false // 导出文件不允许上传
    return true
  }

  // 检查删除权限
  const canDeleteFile = (file: FileItem): boolean => {
    if (!user) return false
    if (user.role === 'super_admin' || user.role === 'admin') return true
    return file.uploader_id === user.id
  }

  // 初始化加载
  useEffect(() => {
    loadFiles('documents')
    loadFiles('templates')
    loadFiles('exports')
  }, [])

  // 标签页切换时加载对应文件
  useEffect(() => {
    const type = activeTab as 'documents' | 'templates' | 'exports'
    if (state[type].length === 0) {
      loadFiles(type)
    }
  }, [activeTab])

  const tabItems = [
    {
      key: 'documents',
      label: (
        <span>
          <FileTextOutlined />
          文档文件
        </span>
      ),
      children: (
        <div>
          {canUpload('documents') && (
            <FileUpload
              type="documents"
              accept=".json,.jsonl"
              onSuccess={handleUploadSuccess}
              style={{ marginBottom: 16 }}
            />
          )}
          <FileList
            files={getFilteredAndSortedFiles(state.documents)}
            loading={state.loading.documents}
            selectedFiles={state.selectedFiles}
            onSelectionChange={(selected: string[]) => setState(prev => ({ ...prev, selectedFiles: selected }))}
            onPreview={handleFilePreview}
            onDownload={handleFileDownload}
            onDelete={handleFileDelete}
            canDelete={canDeleteFile}
            user={user}
          />
        </div>
      )
    },
    {
      key: 'templates',
      label: (
        <span>
          <CodeOutlined />
          模板文件
        </span>
      ),
      children: (
        <div>
          {canUpload('templates') && (
            <FileUpload
              type="templates"
              accept=".py"
              onSuccess={handleUploadSuccess}
              style={{ marginBottom: 16 }}
            />
          )}
          <FileList
            files={getFilteredAndSortedFiles(state.templates)}
            loading={state.loading.templates}
            selectedFiles={state.selectedFiles}
            onSelectionChange={(selected: string[]) => setState(prev => ({ ...prev, selectedFiles: selected }))}
            onPreview={handleFilePreview}
            onDownload={handleFileDownload}
            onDelete={handleFileDelete}
            canDelete={canDeleteFile}
            user={user}
          />
        </div>
      )
    },
    {
      key: 'exports',
      label: (
        <span>
          <DownloadOutlined />
          导出文件
        </span>
      ),
      children: (
        <FileList
          files={getFilteredAndSortedFiles(state.exports)}
          loading={state.loading.exports}
          selectedFiles={state.selectedFiles}
          onSelectionChange={(selected: string[]) => setState(prev => ({ ...prev, selectedFiles: selected }))}
          onPreview={handleFilePreview}
          onDownload={handleFileDownload}
          onDelete={handleFileDelete}
          canDelete={canDeleteFile}
          user={user}
          readonly={true}
        />
      )
    }
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: 24 }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={3} style={{ margin: 0 }}>
                文件库管理
              </Title>
            </Col>
            <Col>
              <Space>
                <Search
                  placeholder="搜索文件名"
                  value={state.searchTerm}
                  onChange={(e) => setState(prev => ({ ...prev, searchTerm: e.target.value }))}
                  style={{ width: 200 }}
                  prefix={<SearchOutlined />}
                />
                <Select
                  value={`${state.sortBy}-${state.sortOrder}`}
                  onChange={(value) => {
                    const [sortBy, sortOrder] = value.split('-')
                    setState(prev => ({
                      ...prev,
                      sortBy: sortBy as 'filename' | 'file_size' | 'uploaded_at',
                      sortOrder: sortOrder as 'asc' | 'desc'
                    }))
                  }}
                  style={{ width: 120 }}
                >
                  <Option value="filename-asc">名称 A-Z</Option>
                  <Option value="filename-desc">名称 Z-A</Option>
                  <Option value="file_size-asc">大小递增</Option>
                  <Option value="file_size-desc">大小递减</Option>
                  <Option value="uploaded_at-desc">最新优先</Option>
                  <Option value="uploaded_at-asc">最旧优先</Option>
                </Select>
                <Button icon={<ReloadOutlined />} onClick={refreshFiles}>
                  刷新
                </Button>
              </Space>
            </Col>
          </Row>

          {state.selectedFiles.length > 0 && (
            <Row style={{ marginTop: 16 }}>
              <Col>
                <Space>
                  <span>已选择 {state.selectedFiles.length} 个文件</span>
                  <Button size="small" onClick={handleBatchDownload}>
                    批量下载
                  </Button>
                  {(user?.role === 'admin' || user?.role === 'super_admin') && (
                    <Button size="small" danger onClick={handleBatchDelete}>
                      批量删除
                    </Button>
                  )}
                  <Button 
                    size="small" 
                    onClick={() => setState(prev => ({ ...prev, selectedFiles: [] }))}
                  >
                    取消选择
                  </Button>
                </Space>
              </Col>
            </Row>
          )}
        </div>

        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
        />

        <FilePreview
          file={state.previewFile}
          visible={state.previewVisible}
          onClose={() => setState(prev => ({ ...prev, previewVisible: false, previewFile: null }))}
        />
      </Card>
    </div>
  )
}

export default FileLibrary 