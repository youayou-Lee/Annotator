import axios, { AxiosResponse, AxiosInstance, AxiosError } from 'axios';

const baseURL = '/api/v1';

// 为开发环境设置临时令牌
const DEV_TOKEN = 'dev_temp_token';

// 扩展AxiosInstance类型
interface ApiInstance extends AxiosInstance {
  post<T = any>(url: string, data?: any, config?: any): Promise<T>;
  get<T = any>(url: string, config?: any): Promise<T>;
  put<T = any>(url: string, data?: any, config?: any): Promise<T>;
  delete<T = any>(url: string, config?: any): Promise<T>;
}

// 确保URL以斜杠结尾
const ensureTrailingSlash = (url: string): string => {
  return url.endsWith('/') ? url : `${url}/`;
};

// Create axios instance
const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  maxRedirects: 5,
  withCredentials: true
}) as ApiInstance;

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // 确保URL以斜杠结尾，除非是blob请求
    if (config.url && config.responseType !== 'blob') {
      config.url = ensureTrailingSlash(config.url);
    }
    
    // 获取token
    const token = localStorage.getItem('token');
    
    // 请求调试日志
    console.debug('API请求:', config.method?.toUpperCase(), 
                 (config.baseURL || '') + (config.url || ''));
    console.debug('当前token:', token);
    
    if (config.headers) {
      if (token) {
        // 确保Authorization头使用Bearer方式
        config.headers.Authorization = `Bearer ${token}`;
        console.debug('设置Authorization头:', config.headers.Authorization);
      } else {
        console.warn('请求无token，可能导致认证失败:', config.url);
      }
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
    
    // 确保返回data，不管它是什么类型
    return response.data;
  },
  (error: AxiosError) => {
    // 错误响应调试
    console.error('API响应错误:', error.message);
    
    if (error.response) {
      console.error('错误状态码:', error.response.status);
      
      // 如果响应中包含详细错误信息，则打印出来
      const errorData = error.response.data;
      console.error('错误响应数据:', errorData);
      
      // 处理不同状态码
      switch (error.response.status) {
        case 400:
          console.error('请求参数错误:', errorData);
          break;
        case 401:
          console.warn('认证失败: 401 Unauthorized. 请先登录获取有效token。');
          console.warn('在实际项目中，这里会自动跳转到登录页面。');
          
          // 清除无效token
          if (localStorage.getItem('token')) {
            console.warn('检测到过期或无效的token，正在清除...');
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
          }
          break;
        case 403:
          console.error('权限不足:', errorData);
          break;
        case 404:
          console.error('请求的资源不存在:', errorData);
          break;
        case 500:
          console.error('服务器内部错误:', errorData);
          // 对于500错误，我们可以尝试获取更详细的错误信息
          if (typeof errorData === 'object' && errorData !== null) {
            // 使用类型断言访问动态属性
            const detail = (errorData as any).detail;
            const message = (errorData as any).message;
            const errorMessage = detail || message || JSON.stringify(errorData);
            console.error('服务器错误详情:', errorMessage);
          }
          break;
        default:
          console.error(`未处理的错误状态码 ${error.response.status}:`, errorData);
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

// 任务相关API封装
const taskApi = {
  // 获取任务列表
  getTasks: () => api.get('/tasks/'),
  
  // 获取单个任务
  getTask: (id: number) => api.get(`/tasks/${id}/`),
  
  // 创建任务
  createTask: (taskData: any) => api.post('/tasks/', taskData),
  
  // 创建带模式的任务
  createTaskWithSchema: (formData: FormData) => {
    return api.post('/tasks/with-schema/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 更新任务
  updateTask: (id: number, taskData: any) => api.put(`/tasks/${id}/`, taskData),
  
  // 删除任务
  deleteTask: (id: number) => api.delete(`/tasks/${id}/`),
  
  // 验证标注数据
  validateAnnotation: (taskId: number, annotationData: any) => 
    api.post(`/tasks/${taskId}/validate-annotation/`, annotationData),
  
  // 验证文档格式
  validateDocumentFormat: (taskId: number, documentData: any) =>
    api.post(`/tasks/${taskId}/format-validation/`, documentData),
  
  // 存储标注数据
  storeAnnotation: (taskId: number, annotationData: any) =>
    api.post(`/tasks/${taskId}/store-annotation/`, annotationData),
};

// 标注相关API封装
const annotationApi = {
  // 获取任务的标注数据
  getAnnotations: (taskId: number) => api.get(`/annotations/task/${taskId}/`),
  
  // 获取单个标注
  getAnnotation: (id: number) => api.get(`/annotations/${id}/`),
  
  // 创建或更新标注
  createOrUpdateAnnotation: (taskId: number, data: any) => 
    api.post(`/annotations/task/${taskId}/`, data),
};

// 文档相关API封装
const documentApi = {
  // 获取文档列表
  getDocuments: () => api.get('/documents/'),
  
  // 获取单个文档
  getDocument: (id: number) => api.get(`/documents/${id}/`),
};

// 公共文件相关API封装
const publicFileApi = {
  // 获取所有公共文件
  getAllFiles: () => api.get('/public/files/'),
  
  // 上传文件
  uploadFile: (fileType: string, file: File, description?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }
    
    return api.post(`/public/upload/${fileType}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 下载文件
  downloadFile: (fileType: string, fileName: string) => 
    api.get(`/public/download/${fileType}/${fileName}/`, {
      responseType: 'blob'
    }),
  
  // 删除文件
  deleteFile: (fileType: string, fileName: string) => 
    api.delete(`/public/delete/${fileType}/${fileName}/`),
  
  // 预览文件
  previewFile: (fileType: string, fileName: string) => 
    api.get(`/public/preview/${fileType}/${fileName}/`),
};

export { taskApi, annotationApi, documentApi, publicFileApi };
export default api;