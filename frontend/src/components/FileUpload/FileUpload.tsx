import React, { useState } from 'react';
import { Upload, Button, Progress, Card, Alert, Typography, Spin, Select, Space } from 'antd';
import { UploadOutlined, InboxOutlined, FileTextOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd/es/upload/interface';
import api from '../../services/api';

const { Dragger } = Upload;
const { Title, Text } = Typography;
const { Option } = Select;

interface FileUploadProps {
  onSuccess?: (fileList: any[]) => void;
  supportedFormats?: string[];
}

const FileUpload: React.FC<FileUploadProps> = ({
  onSuccess,
  supportedFormats = ['json', 'csv', 'xlsx', 'xls'],
}) => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [validationResults, setValidationResults] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedFormat, setSelectedFormat] = useState(supportedFormats[0]);

  // 处理上传前的文件验证
  const beforeUpload = (file: File) => {
    const isValidFormat = supportedFormats.some(format => 
      file.name.toLowerCase().endsWith(`.${format}`)
    );
    
    if (!isValidFormat) {
      setError(`只支持 ${supportedFormats.join(', ')} 格式的文件`);
      return Upload.LIST_IGNORE;
    }
    
    setError(null);
    return true;
  };

  // 处理上传成功的回调
  const handleChange: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    setFileList(newFileList);
  };

  // 自定义上传行为
  const customUpload = async (options: any) => {
    const { file, onSuccess: onUploadSuccess, onError, onProgress } = options;
    
    setUploading(true);
    setProgress(0);
    setValidationResults([]);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', selectedFormat);
    
    try {
      // 模拟进度条
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev + 10;
          if (newProgress >= 99) {
            clearInterval(progressInterval);
            return 99;
          }
          return newProgress;
        });
      }, 200);
      
      // 调用API上传并验证文件
      const response = await api.post('/documents/upload-validate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (response.success) {
        setValidationResults(response.results || []);
        onUploadSuccess(response, file);
        if (onSuccess) {
          onSuccess(response.results || []);
        }
      } else {
        setError(response.message || '验证失败');
        onError(new Error(response.message || '验证失败'));
      }
    } catch (err: any) {
      setError(err.message || '上传失败');
      onError(err);
    } finally {
      setUploading(false);
    }
  };
  
  // 渲染验证结果
  const renderValidationResults = () => {
    if (validationResults.length === 0) return null;
    
    return (
      <Card title="校验结果" style={{ marginTop: 16 }}>
        {validationResults.map((result, index) => (
          <Alert
            key={index}
            message={result.success ? '校验通过' : '校验失败'}
            description={
              <div>
                {result.fileName && <div><strong>文件名:</strong> {result.fileName}</div>}
                {result.errors && result.errors.length > 0 && (
                  <div>
                    <strong>错误详情:</strong>
                    <ul>
                      {result.errors.map((err: any, i: number) => (
                        <li key={i}>
                          {err.line && <span>行 {err.line}: </span>}
                          {err.message}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            }
            type={result.success ? 'success' : 'error'}
            showIcon
          />
        ))}
      </Card>
    );
  };

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space align="center">
          <Text>选择文件格式:</Text>
          <Select 
            value={selectedFormat} 
            onChange={setSelectedFormat}
            style={{ width: 120 }}
            disabled={uploading}
          >
            {supportedFormats.map(format => (
              <Option key={format} value={format}>{format.toUpperCase()}</Option>
            ))}
          </Select>
        </Space>
        
        <Dragger
          fileList={fileList}
          beforeUpload={beforeUpload}
          onChange={handleChange}
          customRequest={customUpload}
          disabled={uploading}
          multiple={false}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单个或批量上传。仅支持 {supportedFormats.join(', ')} 格式的文件。
          </p>
        </Dragger>
        
        {uploading && (
          <div style={{ marginTop: 16 }}>
            <Spin spinning={uploading} />
            <Progress percent={progress} status="active" />
          </div>
        )}
        
        {error && (
          <Alert
            message="错误"
            description={error}
            type="error"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
        
        {renderValidationResults()}
      </Space>
    </div>
  );
};

export default FileUpload; 