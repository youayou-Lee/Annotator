import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect } from 'vitest';
import DocumentUpload from '../pages/DocumentUpload';

// Mock 文件上传组件
vi.mock('../components/FileUpload/FileUpload', () => ({
  default: ({ onSuccess }: { onSuccess: (results: any) => void }) => {
    return (
      <div data-testid="mock-file-upload">
        <button 
          data-testid="mock-success-button" 
          onClick={() => onSuccess([{success: true}])}
        >
          模拟成功上传
        </button>
      </div>
    );
  },
}));

describe('DocumentUpload Page', () => {
  it('renders document upload page correctly', () => {
    render(
      <MemoryRouter>
        <DocumentUpload />
      </MemoryRouter>
    );
    
    // 标题和说明
    expect(screen.getByText('文档上传与校验')).toBeInTheDocument();
    expect(screen.getByText('上传您的文档文件，系统将自动进行格式校验并提供反馈。')).toBeInTheDocument();
    
    // 卡片标题
    expect(screen.getByText('上传文件')).toBeInTheDocument();
    expect(screen.getByText('上传说明')).toBeInTheDocument();
    
    // 文件要求
    expect(screen.getByText('支持的文件格式：')).toBeInTheDocument();
    expect(screen.getByText('JSON')).toBeInTheDocument();
    expect(screen.getByText('CSV')).toBeInTheDocument();
    expect(screen.getByText('XLSX')).toBeInTheDocument();
    expect(screen.getByText('PY (Python)')).toBeInTheDocument();
    
    // 确认文件上传组件存在
    expect(screen.getByTestId('mock-file-upload')).toBeInTheDocument();
  });
  
  it('shows success alert after successful upload', async () => {
    render(
      <MemoryRouter>
        <DocumentUpload />
      </MemoryRouter>
    );
    
    // 模拟成功上传
    const successButton = screen.getByTestId('mock-success-button');
    successButton.click();
    
    // 检查是否显示成功信息
    expect(screen.getByText('上传成功')).toBeInTheDocument();
    expect(screen.getByText('文件已成功上传并通过校验。您现在可以继续进行标注任务。')).toBeInTheDocument();
    
    // 检查是否显示导航链接
    const taskLink = screen.getByText('前往任务管理');
    expect(taskLink).toBeInTheDocument();
    expect(taskLink.getAttribute('href')).toBe('/tasks');
  });
}); 