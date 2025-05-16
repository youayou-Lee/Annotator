import React, { useState } from 'react';
import { Card, Typography, Divider, Row, Col, Alert, Tag, Space } from 'antd';
import FileUpload from '../components/FileUpload/FileUpload';

const { Title, Paragraph } = Typography;

const DocumentUpload: React.FC = () => {
  const [uploadResults, setUploadResults] = useState<any[]>([]);
  const [hasUploaded, setHasUploaded] = useState(false);

  const handleUploadSuccess = (results: any[]) => {
    setUploadResults(results);
    setHasUploaded(true);
  };

  return (
    <div>
      <Title level={2}>文档上传与校验</Title>
      <Paragraph>
        上传您的文档文件，系统将自动进行格式校验并提供反馈。
      </Paragraph>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="上传文件" variant="borderless">
            <FileUpload 
              onSuccess={handleUploadSuccess}
              supportedFormats={['json', 'csv', 'xlsx', 'py']}
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card title="上传说明" variant="borderless">
            <Space direction="vertical">
              <Paragraph>
                <strong>支持的文件格式：</strong>
              </Paragraph>
              <div>
                <Tag color="blue">JSON</Tag>
                <Tag color="green">CSV</Tag>
                <Tag color="orange">XLSX</Tag>
                <Tag color="purple">PY (Python)</Tag>
              </div>
              
              <Divider />
              
              <Paragraph>
                <strong>文件要求：</strong>
              </Paragraph>
              <ul>
                <li>JSON 文件必须是有效的 JSON 格式</li>
                <li>CSV 文件需包含标题行</li>
                <li>XLSX 文件应包含至少一个工作表</li>
                <li>PY 文件应包含 Pydantic 模型定义</li>
              </ul>
              
              <Divider />
              
              <Paragraph>
                <strong>校验规则：</strong>
              </Paragraph>
              <ul>
                <li>数据格式将根据定义的模式进行验证</li>
                <li>必填字段不能为空</li>
                <li>数据类型必须匹配</li>
                <li>数据范围必须在允许范围内</li>
              </ul>
            </Space>
          </Card>
        </Col>
      </Row>
      
      {hasUploaded && uploadResults.some(result => result.success) && (
        <Alert
          message="上传成功"
          description="文件已成功上传并通过校验。您现在可以继续进行标注任务。"
          type="success"
          showIcon
          style={{ marginTop: 16 }}
          action={
            <a href="/tasks">前往任务管理</a>
          }
        />
      )}
    </div>
  );
};

export default DocumentUpload;