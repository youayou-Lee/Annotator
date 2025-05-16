import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';

// 模拟react-router-dom的useNavigate
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

describe('Dashboard组件', () => {
  it('渲染系统概况页面', () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    // 检查标题和描述是否渲染
    expect(screen.getByText('系统概况')).toBeInTheDocument();
    expect(screen.getByText('文书标注系统的整体运行状态和关键指标')).toBeInTheDocument();

    // 检查统计卡片是否渲染
    expect(screen.getByText('文档总数')).toBeInTheDocument();
    expect(screen.getByText('已处理文档')).toBeInTheDocument();
    expect(screen.getByText('待处理任务')).toBeInTheDocument();
    expect(screen.getByText('完成任务')).toBeInTheDocument();
    expect(screen.getByText('活跃用户')).toBeInTheDocument();
    expect(screen.getByText('错误率')).toBeInTheDocument();

    // 检查统计数据是否正确
    expect(screen.getByText('485')).toBeInTheDocument(); // 文档总数
    expect(screen.getByText('312')).toBeInTheDocument(); // 已处理文档
    expect(screen.getByText('15')).toBeInTheDocument(); // 待处理任务
    expect(screen.getByText('42')).toBeInTheDocument(); // 完成任务
    expect(screen.getByText('24')).toBeInTheDocument(); // 活跃用户
    expect(screen.getByText('3.2%')).toBeInTheDocument(); // 错误率
  });

  it('渲染最近任务和最近活动列表', () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    // 检查最近任务卡片是否渲染
    expect(screen.getByText('最近任务')).toBeInTheDocument();
    expect(screen.getByText('查看全部')).toBeInTheDocument();

    // 检查最近任务列表项是否渲染
    expect(screen.getByText('住院病案首页标注')).toBeInTheDocument();
    expect(screen.getByText('门诊病历标注')).toBeInTheDocument();
    expect(screen.getByText('检验报告审核')).toBeInTheDocument();
    expect(screen.getByText('影像检查报告标注')).toBeInTheDocument();

    // 检查任务项中的信息
    expect(screen.getByText('张医生 · 2小时前')).toBeInTheDocument();
    expect(screen.getByText('李护士 · 4小时前')).toBeInTheDocument();
    expect(screen.getByText('王主任 · 昨天')).toBeInTheDocument();
    expect(screen.getByText('张医生 · 2天前')).toBeInTheDocument();

    // 检查最近活动卡片是否渲染
    expect(screen.getByText('最近活动')).toBeInTheDocument();

    // 检查最近活动列表项是否渲染
    expect(screen.getByText('张医生 完成了标注任务')).toBeInTheDocument();
    expect(screen.getByText('系统管理员 创建了新任务')).toBeInTheDocument();
    expect(screen.getByText('李护士 上传了新文件')).toBeInTheDocument();
    expect(screen.getByText('王主任 审核并通过了')).toBeInTheDocument();
    expect(screen.getByText('系统 自动验证失败')).toBeInTheDocument();

    // 检查活动详情
    expect(screen.getByText('影像检查报告标注 · 1小时前')).toBeInTheDocument();
    expect(screen.getByText('住院病案首页标注 · 2小时前')).toBeInTheDocument();
    expect(screen.getByText('住院病案首页.xlsx · 3小时前')).toBeInTheDocument();
    expect(screen.getByText('检验报告标注结果 · 昨天')).toBeInTheDocument();
    expect(screen.getByText('门诊病历.json · 昨天')).toBeInTheDocument();
  });

  it('点击任务项可以导航到任务详情', () => {
    // 创建一个模拟的navigate函数
    const mockNavigate = vi.fn();
    vi.mocked(require('react-router-dom')).useNavigate.mockReturnValue(mockNavigate);

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    // 点击第一个任务项
    fireEvent.click(screen.getByText('住院病案首页标注'));

    // 验证导航是否被调用并且参数正确
    expect(mockNavigate).toHaveBeenCalledWith('/tasks/1');

    // 重置mockNavigate
    mockNavigate.mockClear();

    // 点击第二个任务项
    fireEvent.click(screen.getByText('门诊病历标注'));

    // 验证导航是否被调用并且参数正确
    expect(mockNavigate).toHaveBeenCalledWith('/tasks/2');
  });

  it('查看全部链接指向正确的路径', () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    // 检查"查看全部"链接是否指向正确的路径
    const viewAllLink = screen.getByText('查看全部');
    expect(viewAllLink.getAttribute('href')).toBe('/tasks');
  });
}); 