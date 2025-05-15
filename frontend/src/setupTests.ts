// 为所有测试文件提供的全局配置
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// 模拟localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

// 将模拟对象分配给全局window对象
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// 模拟matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // 兼容旧版API
    removeListener: vi.fn(), // 兼容旧版API
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// 模拟IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor(private callback: IntersectionObserverCallback) {}
  
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
  takeRecords = vi.fn();
  root = null;
  rootMargin = '';
  thresholds = [];
}; 