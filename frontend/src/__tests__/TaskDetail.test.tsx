import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import TaskDetail from '../pages/TaskDetail';

// 模拟useParams返回任务ID
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ id: '1' }),
    useNavigate: () => vi.fn(),
  };
});

// 模拟API服务
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('TaskDetail组件', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('渲染任务详情页面', async () => {
    render(
      <MemoryRouter initialEntries={['/tasks/1']}>
        <Routes>
          <Route path="/tasks/:id" element={<TaskDetail />} />
        </Routes>
      </MemoryRouter>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).not.toBeInTheDocument();
    });

    // 检查标题是否正确渲染
    expect(screen.getByText('住院病案首页标注')).toBeInTheDocument();

    // 检查返回按钮是否存在
    expect(screen.getByText('返回任务列表')).toBeInTheDocument();

    // 检查操作按钮是否存在
    expect(screen.getByText('编辑')).toBeInTheDocument();
    expect(screen.getByText('删除')).toBeInTheDocument();

    // 检查标签页是否存在
    expect(screen.getByRole('tab', { name: '基本信息' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '文档列表' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '历史记录' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '讨论' })).toBeInTheDocument();

    // 默认应该显示基本信息标签页
    expect(screen.getByText('任务详情')).toBeInTheDocument();
    expect(screen.getByText('任务进度')).toBeInTheDocument();
  });

  it('切换到文档列表标签页', async () => {
    render(
      <MemoryRouter initialEntries={['/tasks/1']}>
        <Routes>
          <Route path="/tasks/:id" element={<TaskDetail />} />
        </Routes>
      </MemoryRouter>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).not.toBeInTheDocument();
    });

    // 点击文档列表标签
    fireEvent.click(screen.getByRole('tab', { name: '文档列表' }));

    // 检查文档列表是否显示
    expect(screen.getByText('文档列表 (5)')).toBeInTheDocument();
    
    // 检查表格列标题
    expect(screen.getByText('文档名称')).toBeInTheDocument();
    expect(screen.getByText('状态')).toBeInTheDocument();
    expect(screen.getByText('标注人')).toBeInTheDocument();
    expect(screen.getByText('标注时间')).toBeInTheDocument();
    expect(screen.getByText('审核状态')).toBeInTheDocument();
    expect(screen.getByText('审核人')).toBeInTheDocument();
    expect(screen.getByText('操作')).toBeInTheDocument();

    // 检查是否显示文档数据
    expect(screen.getByText('住院病案首页001.xlsx')).toBeInTheDocument();
    expect(screen.getByText('住院病案首页002.xlsx')).toBeInTheDocument();
    expect(screen.getByText('住院病案首页003.xlsx')).toBeInTheDocument();
  });

  it('切换到历史记录标签页', async () => {
    render(
      <MemoryRouter initialEntries={['/tasks/1']}>
        <Routes>
          <Route path="/tasks/:id" element={<TaskDetail />} />
        </Routes>
      </MemoryRouter>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).not.toBeInTheDocument();
    });

    // 点击历史记录标签
    fireEvent.click(screen.getByRole('tab', { name: '历史记录' }));

    // 检查历史记录是否显示
    expect(screen.getByText('任务历史')).toBeInTheDocument();
    
    // 检查时间线中的历史记录
    expect(screen.getByText('创建任务')).toBeInTheDocument();
    expect(screen.getByText('上传文档')).toBeInTheDocument();
    expect(screen.getByText('分配任务')).toBeInTheDocument();
    expect(screen.getByText('标注进行中')).toBeInTheDocument();
    expect(screen.getByText('完成标注')).toBeInTheDocument();
    expect(screen.getByText('审核')).toBeInTheDocument();
  });

  it('切换到讨论标签页并添加评论', async () => {
    render(
      <MemoryRouter initialEntries={['/tasks/1']}>
        <Routes>
          <Route path="/tasks/:id" element={<TaskDetail />} />
        </Routes>
      </MemoryRouter>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).not.toBeInTheDocument();
    });

    // 点击讨论标签
    fireEvent.click(screen.getByRole('tab', { name: '讨论' }));

    // 检查讨论区是否显示
    expect(screen.getByText('讨论')).toBeInTheDocument();
    
    // 检查现有评论
    expect(screen.getByText('已开始处理该任务')).toBeInTheDocument();
    expect(screen.getByText('请注意截止日期是10月15日')).toBeInTheDocument();
    expect(screen.getByText('有一些文档格式不统一，需要花更多时间处理')).toBeInTheDocument();
    expect(screen.getByText('已开始审核，部分字段需要修正')).toBeInTheDocument();

    // 添加新评论
    const commentInput = screen.getByPlaceholderText('添加评论...');
    fireEvent.change(commentInput, { target: { value: '这是一条测试评论' } });
    
    // 点击发送按钮
    fireEvent.click(screen.getByText('发送'));

    // 检查新评论是否添加
    expect(screen.getByText('这是一条测试评论')).toBeInTheDocument();
  });

  it('尝试删除任务', async () => {
    // 模拟window.confirm返回true
    vi.spyOn(window, 'confirm').mockImplementation(() => true);
    
    const mockNavigate = vi.fn();
    vi.mocked(require('react-router-dom')).useNavigate.mockReturnValue(mockNavigate);
    
    render(
      <MemoryRouter initialEntries={['/tasks/1']}>
        <Routes>
          <Route path="/tasks/:id" element={<TaskDetail />} />
        </Routes>
      </MemoryRouter>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).not.toBeInTheDocument();
    });

    // 点击删除按钮
    fireEvent.click(screen.getByText('删除'));

    // 检查确认对话框是否显示
    await waitFor(() => {
      expect(screen.getByText('确认删除')).toBeInTheDocument();
      expect(screen.getByText(/确定要删除任务"住院病案首页标注"吗？此操作无法撤销。/)).toBeInTheDocument();
    });

    // 点击确认按钮
    fireEvent.click(screen.getByText('确 定'));

    // 模拟返回任务列表
    await waitFor(() => {
      expect(vi.mocked(require('react-router-dom')).useNavigate()).toHaveBeenCalledWith('/tasks');
    });
  });

  it('返回任务列表', async () => {
    const mockNavigate = vi.fn();
    vi.mocked(require('react-router-dom')).useNavigate.mockReturnValue(mockNavigate);
    
    render(
      <MemoryRouter initialEntries={['/tasks/1']}>
        <Routes>
          <Route path="/tasks/:id" element={<TaskDetail />} />
        </Routes>
      </MemoryRouter>
    );

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载中...')).not.toBeInTheDocument();
    });

    // 点击返回按钮
    fireEvent.click(screen.getByText('返回任务列表'));

    // 验证navigation被调用
    expect(mockNavigate).toHaveBeenCalledWith('/tasks');
  });
}); 