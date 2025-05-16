import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Tabs, 
  Table, 
  Button, 
  Upload, 
  message, 
  Space, 
  Tooltip, 
  Modal, 
  Spin, 
  Empty, 
  Typography,
  Input
} from 'antd';
import { 
  UploadOutlined, 
  DownloadOutlined, 
  DeleteOutlined, 
  EyeOutlined, 
  FileOutlined,
  FileTextOutlined,
  FileMarkdownOutlined,
  FilePdfOutlined,
  FileExcelOutlined,
  FileUnknownOutlined,
  InboxOutlined,
  FileWordOutlined
} from '@ant-design/icons';
import api from '../../services/api';
import { formatBytes, formatDate } from '../../utils/formatters';

const { TabPane } = Tabs;
const { Dragger } = Upload;
const { Title, Text } = Typography;

// 文件类型定义
interface FileItem {
  name: string;
  path: string;
  size: number;
  modified: number;
}

// 文件分类
interface FileCategories {
  documents: FileItem[];
  templates: FileItem[];
  schemas: FileItem[];
  exports: FileItem[];
}

const FILE_TYPES = [
  { key: 'documents', label: '文档文件', description: '存放标注用的原始文档文件' },
  { key: 'templates', label: '模板文件', description: '存放验证标注数据的Python模板文件' },
  { key: 'schemas', label: 'Schema文件', description: '存放验证标注数据的JSON Schema文件' },
  { key: 'exports', label: '导出文件', description: '存放标注数据的导出文件' },
];

const PublicFileManager: React.FC = () => {
  const [files, setFiles] = useState<FileCategories>({
    documents: [],
    templates: [],
    schemas: [],
    exports: []
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [activeKey, setActiveKey] = useState<string>('documents');
  const [previewVisible, setPreviewVisible] = useState<boolean>(false);
  const [previewContent, setPreviewContent] = useState<any>(null);
  const [previewTitle, setPreviewTitle] = useState<string>('');
  const [previewLoading, setPreviewLoading] = useState<boolean>(false);

  // 加载文件列表
  const loadFiles = async () => {
    setLoading(true);
    try {
      const response = await api.get('/public/files');
      console.log('文件列表加载成功，返回数据:', response);
      if (response && typeof response === 'object') {
        setFiles(response);
      } else {
        console.error('API返回格式错误:', response);
        message.error('加载文件列表失败：数据格式错误');
      }
    } catch (error) {
      console.error('加载文件失败:', error);
      message.error('加载文件列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  // 获取文件类型图标
  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    
    switch(extension) {
      case 'txt':
        return <FileTextOutlined />;
      case 'md':
        return <FileMarkdownOutlined />;
      case 'json':
        return <FileTextOutlined />;
      case 'pdf':
        return <FilePdfOutlined />;
      case 'xlsx':
      case 'xls':
      case 'csv':
        return <FileExcelOutlined />;
      case 'doc':
      case 'docx':
        return <FileWordOutlined />;
      case 'py':
        return <FileOutlined />;
      default:
        return <FileUnknownOutlined />;
    }
  };

  // 上传文件
  const handleUpload = async (options: any) => {
    const { file, onSuccess, onError } = options;
    
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('开始上传文件:', file.name, '类型:', activeKey);
    
    try {
      const response = await api.post(`/public/upload/${activeKey}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('文件上传响应:', response);
      
      if (response && response.success) {
        message.success(`文件 ${file.name} 上传成功`);
        onSuccess();
        
        // 刷新文件列表
        console.log('上传成功，刷新文件列表');
        await loadFiles();
        console.log('文件列表刷新完成');
      } else {
        const errorMsg = response?.message || '未知错误';
        console.error('上传失败:', errorMsg);
        message.error(`文件 ${file.name} 上传失败: ${errorMsg}`);
        onError(new Error(errorMsg));
      }
    } catch (error: any) {
      console.error('上传失败:', error);
      message.error(`文件 ${file.name} 上传失败: ${error.message || '未知错误'}`);
      onError(error);
    }
  };

  // 删除文件
  const handleDelete = async (file: FileItem) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文件 ${file.name} 吗？此操作不可恢复。`,
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        try {
          await api.delete(`/public/delete/${activeKey}/${file.name}`);
          message.success(`文件 ${file.name} 已删除`);
          
          // 刷新文件列表
          loadFiles();
        } catch (error) {
          console.error('删除失败:', error);
          message.error(`删除文件 ${file.name} 失败`);
        }
      }
    });
  };

  // 下载文件
  const handleDownload = (file: FileItem) => {
    const downloadUrl = `${api.defaults.baseURL}/public/download/${activeKey}/${file.name}`;
    console.log('下载文件:', file.name, '链接:', downloadUrl);
    
    // 创建一个隐藏的a标签并模拟点击它来下载文件
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', file.name);
    link.setAttribute('target', '_blank');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    message.success(`开始下载文件: ${file.name}`);
  };

  // 预览文件
  const handlePreview = async (file: FileItem) => {
    setPreviewLoading(true);
    setPreviewVisible(true);
    setPreviewTitle(file.name);
    
    try {
      const response = await api.get(`/public/preview/${activeKey}/${file.name}`);
      setPreviewContent(response.data);
    } catch (error) {
      console.error('预览失败:', error);
      message.error('文件预览失败');
      setPreviewContent(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '文件名',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          {getFileIcon(text)}
          <Text>{text}</Text>
        </Space>
      )
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      render: (size: number) => formatBytes(size)
    },
    {
      title: '修改时间',
      dataIndex: 'modified',
      key: 'modified',
      render: (time: number) => formatDate(new Date(time * 1000))
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: FileItem) => (
        <Space>
          <Tooltip title="下载">
            <Button 
              icon={<DownloadOutlined />} 
              size="small" 
              onClick={() => handleDownload(record)}
            />
          </Tooltip>
          <Tooltip title="预览">
            <Button 
              icon={<EyeOutlined />} 
              size="small" 
              onClick={() => handlePreview(record)}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button 
              icon={<DeleteOutlined />} 
              size="small" 
              danger
              onClick={() => handleDelete(record)}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  // 渲染JSON预览内容
  const renderPreviewContent = () => {
    if (previewLoading) {
      return <Spin tip="加载中..." />;
    }
    
    if (!previewContent) {
      return <Empty description="无法预览此文件" />;
    }
    
    if (typeof previewContent === 'object') {
      return (
        <pre style={{ maxHeight: '500px', overflow: 'auto' }}>
          {JSON.stringify(previewContent, null, 2)}
        </pre>
      );
    }
    
    if (typeof previewContent === 'string') {
      return (
        <pre style={{ maxHeight: '500px', overflow: 'auto' }}>
          {previewContent}
        </pre>
      );
    }
    
    if (previewContent.content) {
      return (
        <pre style={{ maxHeight: '500px', overflow: 'auto' }}>
          {previewContent.content}
        </pre>
      );
    }
    
    return <Empty description="不支持的文件格式" />;
  };

  return (
    <Card title="公共文件管理">
      {process.env.NODE_ENV === 'development' && (
        <Card title="调试信息" style={{ marginBottom: 16 }}>
          <pre style={{ maxHeight: '200px', overflow: 'auto' }}>
            当前活动标签: {activeKey}
            {'\n'}
            加载状态: {loading ? '加载中' : '已加载'}
            {'\n'}
            文件数量: {files && files[activeKey as keyof FileCategories] ? files[activeKey as keyof FileCategories].length : 0}
            {'\n\n'}
            文件数据:
            {'\n'}
            {JSON.stringify(files, null, 2)}
          </pre>
        </Card>
      )}
      
      <Tabs activeKey={activeKey} onChange={setActiveKey}>
        {FILE_TYPES.map(type => (
          <TabPane 
            tab={type.label} 
            key={type.key}
          >
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary">{type.description}</Text>
            </div>
            
            <Card 
              size="small" 
              title="上传文件" 
              style={{ marginBottom: 16 }}
            >
              <Dragger
                name="file"
                multiple={false}
                customRequest={handleUpload}
                showUploadList={false}
              >
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持单个或批量上传，严禁上传公司数据或其他违禁文件
                </p>
              </Dragger>
            </Card>
            
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text type="secondary">
                {files && files[type.key as keyof FileCategories] 
                  ? `共 ${files[type.key as keyof FileCategories].length} 个文件` 
                  : '暂无文件'}
              </Text>
              
              {files && files[type.key as keyof FileCategories] && files[type.key as keyof FileCategories].length > 0 && (
                <Button 
                  type="primary" 
                  icon={<DownloadOutlined />}
                  onClick={() => message.info('请点击文件操作栏中的下载按钮下载单个文件')}
                >
                  下载文件
                </Button>
              )}
            </div>
            
            <Table
              rowKey="name"
              dataSource={files && files[type.key as keyof FileCategories] ? files[type.key as keyof FileCategories] : []}
              columns={columns}
              loading={loading}
              pagination={{ pageSize: 10 }}
              locale={{ emptyText: '暂无文件' }}
            />
          </TabPane>
        ))}
      </Tabs>
      
      <Modal
        title={`预览: ${previewTitle}`}
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>,
          <Button 
            key="download" 
            type="primary" 
            icon={<DownloadOutlined />}
            onClick={() => {
              setPreviewVisible(false);
              const file = { name: previewTitle, path: '', size: 0, modified: 0 };
              handleDownload(file);
            }}
          >
            下载
          </Button>
        ]}
        width={800}
      >
        {renderPreviewContent()}
      </Modal>
    </Card>
  );
};

export default PublicFileManager; 