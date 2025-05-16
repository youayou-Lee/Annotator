import React from 'react';
import { Typography } from 'antd';
import PublicFileManager from '../components/FileUpload/PublicFileManager';

const { Title, Paragraph } = Typography;

const PublicFiles: React.FC = () => {
  return (
    <div>
      <Title level={2}>公共文件库</Title>
      <Paragraph>
        此页面提供公共文件的管理功能，包括各类文档、模板、模式和导出文件。您可以上传新文件、下载或预览现有文件。
      </Paragraph>
      
      <PublicFileManager />
    </div>
  );
};

export default PublicFiles; 