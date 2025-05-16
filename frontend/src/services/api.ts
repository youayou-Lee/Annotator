import axios, { AxiosResponse, AxiosInstance } from 'axios';

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
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data;
  },
  (error) => {
    // Handle 401 errors
    if (error.response && error.response.status === 401) {
      // 暂时注释掉自动跳转，改为打印警告
      console.warn('认证失败: 401 Unauthorized. 请先登录获取有效token。');
      console.warn('在实际项目中，这里会自动跳转到登录页面。');
      // localStorage.removeItem('token');
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;