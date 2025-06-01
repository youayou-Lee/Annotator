import axios, { AxiosInstance, AxiosResponse } from 'axios'
import type {
  User,
  LoginRequest,
  RegisterRequest,
  Task,
  CreateTaskRequest,
  FileItem,
  AnnotationData,
  AnnotationRequest,
  ReviewRequest,
  ExportRequest,
  ApiResponse,
} from '../types'

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 获取token的辅助函数
const getToken = (): string | null => {
  try {
    const authData = localStorage.getItem('auth-storage')
    if (authData) {
      const parsed = JSON.parse(authData)
      return parsed.state?.token || null
    }
  } catch (error) {
    console.error('解析token失败:', error)
  }
  return null
}

// 清除认证信息的辅助函数
const clearAuth = () => {
  localStorage.removeItem('auth-storage')
  // 触发自定义事件，通知其他组件token已失效
  window.dispatchEvent(new CustomEvent('auth-cleared'))
}

// 请求拦截器 - 添加token
api.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误和token刷新
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // 如果是401错误且不是登录请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // 如果是登录或注册请求，直接返回错误
      if (originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/auth/register')) {
        return Promise.reject(error)
      }

      // 清除认证信息并跳转到登录页
      clearAuth()
      
      // 如果当前不在登录页，则跳转到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    // 处理网络错误
    if (!error.response) {
      console.error('网络错误:', error.message)
    }

    return Promise.reject(error)
  }
)

// 认证相关API
export const authAPI = {
  login: async (data: LoginRequest): Promise<ApiResponse<{ user: User; token: string }>> => {
    try {
      const response = await api.post('/auth/login', data)
      // 后端直接返回数据，需要包装成ApiResponse格式
      return {
        success: true,
        data: {
          user: response.data.user,
          token: response.data.access_token
        }
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '登录失败'
      }
    }
  },
    
  register: async (data: RegisterRequest): Promise<ApiResponse<{ user: User; token: string }>> => {
    try {
      await api.post('/auth/register', data)
      // 注册成功后自动登录
      const loginResponse = await api.post('/auth/login', {
        username: data.username,
        password: data.password
      })
      return {
        success: true,
        data: {
          user: loginResponse.data.user,
          token: loginResponse.data.access_token
        }
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '注册失败'
      }
    }
  },
    
  getMe: async (): Promise<ApiResponse<User>> => {
    try {
      const response = await api.get('/auth/me')
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '获取用户信息失败'
      }
    }
  },
}

// 用户管理API
export const userAPI = {
  getUsers: async (): Promise<ApiResponse<User[]>> => {
    try {
      const response = await api.get('/users')
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '获取用户列表失败'
      }
    }
  },
    
  updateUser: async (userId: string, data: Partial<User>): Promise<ApiResponse<User>> => {
    try {
      const response = await api.put(`/users/${userId}`, data)
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '更新用户失败'
      }
    }
  },
}

// 文件管理API
export const fileAPI = {
  getFiles: async (type?: 'documents' | 'templates' | 'exports'): Promise<ApiResponse<FileItem[]>> => {
    try {
      const response = await api.get('/files', { params: { type } })
      // 后端返回格式: { files: FileItem[], total: number, file_type: string }
      return {
        success: true,
        data: response.data.files || []
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '获取文件列表失败'
      }
    }
  },
    
  uploadFile: async (file: File, type: 'documents' | 'templates'): Promise<ApiResponse<FileItem>> => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_type', type)
      const response = await api.post('/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '文件上传失败'
      }
    }
  },
  
  deleteFile: async (fileId: string): Promise<ApiResponse> => {
    try {
      await api.delete(`/files/${fileId}`)
      return {
        success: true
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '删除文件失败'
      }
    }
  },
    
  downloadFile: (fileId: string): Promise<Blob> =>
    api.get(`/files/${fileId}/download`, { responseType: 'blob' }).then(res => res.data),
    
  previewFile: async (fileId: string): Promise<ApiResponse<any>> => {
    try {
      const response = await api.get(`/files/${fileId}/preview`)
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '预览文件失败'
      }
    }
  },
}

// 任务管理API
export const taskAPI = {
  getTasks: async (params?: {
    status?: string
    assignee_id?: string
    creator_id?: string
    search?: string
    page?: number
    page_size?: number
  }): Promise<ApiResponse<Task[]>> => {
    try {
      const response = await api.get('/tasks', { params })
      // 后端返回的是TaskListResponse格式: { tasks: Task[], total: number, page: number, page_size: number, total_pages: number }
      return {
        success: true,
        data: response.data.tasks || []
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '获取任务列表失败'
      }
    }
  },
    
  createTask: async (data: CreateTaskRequest): Promise<ApiResponse<Task>> => {
    try {
      const response = await api.post('/tasks', data)
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '创建任务失败'
      }
    }
  },
    
  getTask: async (taskId: string): Promise<ApiResponse<Task>> => {
    try {
      const response = await api.get(`/tasks/${taskId}`)
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '获取任务详情失败'
      }
    }
  },
    
  updateTask: async (taskId: string, data: Partial<CreateTaskRequest>): Promise<ApiResponse<Task>> => {
    try {
      const response = await api.put(`/tasks/${taskId}`, data)
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '更新任务失败'
      }
    }
  },
    
  deleteTask: async (taskId: string): Promise<ApiResponse> => {
    try {
      await api.delete(`/tasks/${taskId}`)
      return {
        success: true
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '删除任务失败'
      }
    }
  },

  assignTask: async (taskId: string, assigneeId: string): Promise<ApiResponse<Task>> => {
    try {
      const response = await api.put(`/tasks/${taskId}/assign`, { assignee_id: assigneeId })
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '分配任务失败'
      }
    }
  },

  getTaskProgress: async (taskId: string): Promise<ApiResponse<{
    total_documents: number
    completed_documents: number
    progress_percentage: number
  }>> => {
    try {
      const response = await api.get(`/tasks/${taskId}/progress`)
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || '获取任务进度失败'
      }
    }
  }
}

// 标注功能API
export const annotationAPI = {
  getAnnotation: (taskId: string, documentId: string): Promise<ApiResponse<AnnotationData>> =>
    api.get(`/tasks/${taskId}/documents/${documentId}/annotation`).then(res => res.data),
    
  saveAnnotation: (taskId: string, documentId: string, data: AnnotationRequest): Promise<ApiResponse<AnnotationData>> =>
    api.post(`/tasks/${taskId}/documents/${documentId}/annotation`, data).then(res => res.data),
    
  submitAnnotation: (taskId: string, documentId: string): Promise<ApiResponse> =>
    api.post(`/tasks/${taskId}/documents/${documentId}/submit`).then(res => res.data),
}

// 复审功能API
export const reviewAPI = {
  getReview: (taskId: string, documentId: string): Promise<ApiResponse<AnnotationData>> =>
    api.get(`/tasks/${taskId}/documents/${documentId}/review`).then(res => res.data),
    
  submitReview: (taskId: string, documentId: string, data: ReviewRequest): Promise<ApiResponse> =>
    api.post(`/tasks/${taskId}/documents/${documentId}/review`, data).then(res => res.data),
}

// 导出功能API
export const exportAPI = {
  exportTask: (data: ExportRequest): Promise<ApiResponse<{ export_id: string; download_url: string }>> =>
    api.post(`/tasks/${data.task_id}/export`, data).then(res => res.data),
    
  downloadExport: (exportId: string): Promise<Blob> =>
    api.get(`/exports/${exportId}/download`, { responseType: 'blob' }).then(res => res.data),
}

export default api 