import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import FileUpload from '../components/FileUpload/FileUpload';
import api from '../services/api';

// Mock API 服务
vi.mock('../services/api', () => ({
  default: {
    post: vi.fn(() => Promise.resolve({
      success: true,
      results: [{ fileName: 'test.json', success: true }]
    })),
  },
}));

describe('FileUpload Component', () => {
  const mockOnSuccess = vi.fn();
  const mockFile = new File(['test content'], 'test.json', { type: 'application/json' });
  
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('renders file upload component correctly', () => {
    render(<FileUpload onSuccess={mockOnSuccess} />);
    
    expect(screen.getByText('选择文件格式:')).toBeInTheDocument();
    expect(screen.getByText('点击或拖拽文件到此区域上传')).toBeInTheDocument();
    expect(screen.getByText(/支持单个或批量上传/)).toBeInTheDocument();
  });
  
  it('validates file format', async () => {
    render(<FileUpload onSuccess={mockOnSuccess} supportedFormats={['json']} />);
    
    const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });
    const fileInput = screen.getByRole('button', { name: /点击或拖拽文件到此区域上传/ });
    
    // 模拟文件上传 - 修改直接调用customRequest
    const dataTransfer = {
      files: [invalidFile],
    };
    
    fireEvent.drop(fileInput, { dataTransfer });
    
    // 等待出现错误提示
    await waitFor(() => {
      const errorText = screen.getByText((content) => {
        return content.includes('只支持 json 格式的文件');
      });
      expect(errorText).toBeInTheDocument();
    });
  });
  
  it('uploads file successfully', async () => {
    // 模拟 API 成功响应
    const successResponse = {
      success: true,
      results: [
        {
          fileName: 'test.json',
          success: true,
        },
      ],
    };
    
    (api.post as any).mockResolvedValueOnce(successResponse);
    
    render(<FileUpload onSuccess={mockOnSuccess} />);
    
    const fileInput = screen.getByRole('button', { name: /点击或拖拽文件到此区域上传/ });
    
    // 模拟拖放上传文件
    const dataTransfer = {
      files: [mockFile],
    };
    
    fireEvent.drop(fileInput, { dataTransfer });
    
    // 验证API被调用
    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
    });
    
    // 验证回调函数被调用
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });
  
  it('handles upload error correctly', async () => {
    // 模拟 API 失败响应
    const errorResponse = {
      success: false,
      message: '文件格式错误',
    };
    
    (api.post as any).mockResolvedValueOnce(errorResponse);
    
    render(<FileUpload onSuccess={mockOnSuccess} />);
    
    const fileInput = screen.getByRole('button', { name: /点击或拖拽文件到此区域上传/ });
    
    // 模拟拖放上传文件
    const dataTransfer = {
      files: [mockFile],
    };
    
    fireEvent.drop(fileInput, { dataTransfer });
    
    // 验证API被调用
    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
    });
    
    // 验证错误信息显示
    await waitFor(() => {
      const errorTitle = screen.getByText('错误');
      expect(errorTitle).toBeInTheDocument();
      const errorMessage = screen.getByText('文件格式错误');
      expect(errorMessage).toBeInTheDocument();
    });
  });
  
  it('displays validation errors correctly', async () => {
    // 模拟 API 返回验证错误
    const validationErrorResponse = {
      success: true,
      results: [
        {
          fileName: 'test.json',
          success: false,
          errors: [
            { line: 5, message: '缺少必填字段' },
            { line: 10, message: '数据类型错误' },
          ],
        },
      ],
    };
    
    (api.post as any).mockResolvedValueOnce(validationErrorResponse);
    
    render(<FileUpload onSuccess={mockOnSuccess} />);
    
    const fileInput = screen.getByRole('button', { name: /点击或拖拽文件到此区域上传/ });
    
    // 模拟拖放上传文件
    const dataTransfer = {
      files: [mockFile],
    };
    
    fireEvent.drop(fileInput, { dataTransfer });
    
    // 验证API被调用
    await waitFor(() => {
      expect(api.post).toHaveBeenCalled();
    });
    
    // 验证显示校验错误信息
    await waitFor(() => {
      expect(screen.getByText('校验结果')).toBeInTheDocument();
      expect(screen.getByText('校验失败')).toBeInTheDocument();
      expect(screen.getByText((content) => content.includes('缺少必填字段'))).toBeInTheDocument();
      expect(screen.getByText((content) => content.includes('数据类型错误'))).toBeInTheDocument();
    });
  });
}); 