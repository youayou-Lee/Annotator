import axios, { AxiosResponse, AxiosInstance, AxiosError } from 'axios';

const baseURL = '/api/v1';

// 扩展AxiosInstance类型
interface ApiInstance extends AxiosInstance {
  post<T = any>(url: string, data?: any, config?: any): Promise<T>;
  get<T = any>(url: string, config?: any): Promise<T>;
  put<T = any>(url: string, data?: any, config?: any): Promise<T>;
  delete<T = any>(url: string, config?: any): Promise<T>;
}

// Create axios instance
const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
}) as ApiInstance;

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // 请求调试日志
    console.debug('API请求:', config.method?.toUpperCase(), 
                 (config.baseURL || '') + (config.url || ''));
    
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('请求拦截器错误:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 响应成功调试日志
    console.debug('API响应成功:', response.config.method?.toUpperCase(), response.config.url, response.status);
    return response.data;
  },
  (error: AxiosError) => {
    // 错误响应调试
    console.error('API响应错误:', error.message);
    
    if (error.response) {
      console.error('错误状态码:', error.response.status);
      console.error('错误响应数据:', error.response.data);
      
      // 处理不同状态码
      switch (error.response.status) {
        case 400:
          console.error('请求参数错误:', error.response.data);
          break;
        case 401:
          console.warn('认证失败: 401 Unauthorized. 请先登录获取有效token。');
          console.warn('在实际项目中，这里会自动跳转到登录页面。');
          break;
        case 403:
          console.error('权限不足:', error.response.data);
          break;
        case 404:
          console.error('请求的资源不存在:', error.response.data);
          break;
        case 500:
          console.error('服务器内部错误:', error.response.data);
          break;
        default:
          console.error(`未处理的错误状态码 ${error.response.status}:`, error.response.data);
      }
    } else if (error.request) {
      // 请求已发送但未收到响应
      console.error('未收到服务器响应:', error.request);
    } else {
      // 请求设置时出错
      console.error('请求配置错误:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;