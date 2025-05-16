import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import TaskManagement from '../pages/TaskManagement';

// 模拟react-router-dom的useNavigate hook
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

// 模拟API服务
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('TaskManagement组件', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('渲染任务管理页面', () => {
    render(
      <MemoryRouter>
        <TaskManagement />
      </MemoryRouter>
    );

    // 检查标题和描述是否渲染
    expect(screen.getByText('任务管理')).toBeInTheDocument();
    expect(screen.getByText('创建、管理和追踪文档标注任务的进度和状态。')).toBeInTheDocument();

    // 检查筛选组件是否渲染
    expect(screen.getByPlaceholderText('搜索任务名称或描述')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('状态筛选')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('优先级筛选')).toBeInTheDocument();

    // 检查创建任务按钮是否渲染
    expect(screen.getByText('创建任务')).toBeInTheDocument();

    // 检查任务表格是否渲染，应该包含几个列标题
    expect(screen.getByText('任务名称')).toBeInTheDocument();
    expect(screen.getByText('状态')).toBeInTheDocument();
    expect(screen.getByText('优先级')).toBeInTheDocument();
    expect(screen.getByText('进度')).toBeInTheDocument();
    expect(screen.getByText('截止日期')).toBeInTheDocument();
    expect(screen.getByText('负责人')).toBeInTheDocument();
    expect(screen.getByText('文档数量')).toBeInTheDocument();
    expect(screen.getByText('操作')).toBeInTheDocument();

    // 检查是否显示模拟任务数据
    expect(screen.getByText('住院病案首页标注')).toBeInTheDocument();
    expect(screen.getByText('门诊病历标注')).toBeInTheDocument();
    expect(screen.getByText('检验报告审核')).toBeInTheDocument();
  });

  it('通过文本搜索过滤任务', () => {
    render(
      <MemoryRouter>
        <TaskManagement />
      </MemoryRouter>
    );

    // 获取搜索输入框并输入搜索文本
    const searchInput = screen.getByPlaceholderText('搜索任务名称或描述');
    fireEvent.change(searchInput, { target: { value: '门诊' } });

    // 检查过滤后的结果
    expect(screen.getByText('门诊病历标注')).toBeInTheDocument();
    expect(screen.queryByText('住院病案首页标注')).not.toBeInTheDocument();
    expect(screen.queryByText('检验报告审核')).not.toBeInTheDocument();
  });

  it('通过状态筛选任务', async () => {
    render(
      <MemoryRouter>
        <TaskManagement />
      </MemoryRouter>
    );

    // 点击状态筛选下拉框
    const statusFilter = screen.getByPlaceholderText('状态筛选');
    fireEvent.mouseDown(statusFilter);

    // 等待下拉选项出现并选择"进行中"
    await waitFor(() => {
      expect(screen.getByText('进行中')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('进行中'));

    // 检查过滤后的结果
    expect(screen.getByText('住院病案首页标注')).toBeInTheDocument();
    expect(screen.queryByText('门诊病历标注')).not.toBeInTheDocument();
    expect(screen.queryByText('检验报告审核')).not.toBeInTheDocument();
  });

  it('通过优先级筛选任务', async () => {
    render(
      <MemoryRouter>
        <TaskManagement />
      </MemoryRouter>
    );

    // 点击优先级筛选下拉框
    const priorityFilter = screen.getByPlaceholderText('优先级筛选');
    fireEvent.mouseDown(priorityFilter);

    // 等待下拉选项出现并选择"高"
    await waitFor(() => {
      expect(screen.getByText('高')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('高'));

    // 检查过滤后的结果
    expect(screen.getByText('住院病案首页标注')).toBeInTheDocument();
    expect(screen.queryByText('门诊病历标注')).not.toBeInTheDocument();
    expect(screen.queryByText('检验报告审核')).not.toBeInTheDocument();
  });

  it('打开创建任务模态框', async () => {
    render(
      <MemoryRouter>
        <TaskManagement />
      </MemoryRouter>
    );

    // 点击创建任务按钮
    fireEvent.click(screen.getByText('创建任务'));

    // 检查模态框是否打开
    await waitFor(() => {
      expect(screen.getByText('创建新任务')).toBeInTheDocument();
    });

    // 检查表单字段是否存在
    expect(screen.getByLabelText('任务名称')).toBeInTheDocument();
    expect(screen.getByLabelText('任务描述')).toBeInTheDocument();
    expect(screen.getByLabelText('文档类型')).toBeInTheDocument();
    expect(screen.getByLabelText('文档数量')).toBeInTheDocument();
    expect(screen.getByLabelText('优先级')).toBeInTheDocument();
    expect(screen.getByLabelText('状态')).toBeInTheDocument();
    expect(screen.getByLabelText('截止日期')).toBeInTheDocument();
    expect(screen.getByLabelText('负责人')).toBeInTheDocument();
  });

  it('提交创建任务表单', async () => {
    render(
      <MemoryRouter>
        <TaskManagement />
      </MemoryRouter>
    );

    // 点击创建任务按钮
    fireEvent.click(screen.getByText('创建任务'));

    // 等待模态框打开
    await waitFor(() => {
      expect(screen.getByText('创建新任务')).toBeInTheDocument();
    });

    // 填写表单
    fireEvent.change(screen.getByLabelText('任务名称'), {
      target: { value: '测试任务' },
    });
    fireEvent.change(screen.getByLabelText('任务描述'), {
      target: { value: '这是一个测试任务描述' },
    });
    fireEvent.change(screen.getByLabelText('文档数量'), {
      target: { value: '10' },
    });

    // 选择文档类型
    fireEvent.mouseDown(screen.getByLabelText('文档类型'));
    await waitFor(() => {
      expect(screen.getByText('住院病案')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('住院病案'));

    // 选择优先级
    fireEvent.mouseDown(screen.getByLabelText('优先级'));
    await waitFor(() => {
      expect(screen.getByText('中')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('中'));

    // 选择负责人
    fireEvent.mouseDown(screen.getByLabelText('负责人'));
    await waitFor(() => {
      expect(screen.getByText('张医生')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('张医生'));

    // 点击确定按钮提交表单
    const okButton = screen.getAllByText('确 定')[0];
    fireEvent.click(okButton);

    // 模拟表单实际提交会创建新任务
    // 由于我们没有实际提交API调用，这里只检查在UI上已经显示了新任务
    await waitFor(() => {
      expect(screen.getByText('测试任务')).toBeInTheDocument();
    });
  });
}); 