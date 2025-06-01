// 用户相关类型
export interface User {
  id: string
  username: string
  role: 'admin' | 'super_admin' | 'annotator'
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  role?: 'admin' | 'annotator'
}

// 文件相关类型
export interface FileItem {
  id: string
  filename: string
  file_path: string
  file_type: 'documents' | 'templates' | 'exports'
  file_size: number
  uploader_id: string
  uploaded_at: string
}

export interface UploadResponse {
  success: boolean
  file_id: string
  filename: string
  message?: string
}

// 任务相关类型
export interface Task {
  id: string
  name: string
  description: string
  creator_id: string
  assignee_id: string
  status: 'pending' | 'in_progress' | 'completed'
  created_at: string
  documents: TaskDocument[]
  template: TaskTemplate
}

export interface TaskDocument {
  id: string
  filename: string
  file_path: string
  status: 'pending' | 'completed'
}

export interface TaskTemplate {
  filename: string
  file_path: string
}

export interface CreateTaskRequest {
  name: string
  description: string
  assignee_id: string
  document_ids: string[]
  template_id: string
}

// 标注相关类型
export interface AnnotationData {
  document_id: string
  task_id: string
  original_data: Record<string, any>
  annotated_data: Record<string, any>
  status: 'pending' | 'completed'
  annotator_id: string
  updated_at: string
}

export interface AnnotationRequest {
  annotated_data: Record<string, any>
}

// 复审相关类型
export interface ReviewData {
  annotation_id: string
  reviewer_id: string
  status: 'approved' | 'rejected'
  comments: string
  reviewed_at: string
}

export interface ReviewRequest {
  status: 'approved' | 'rejected'
  comments: string
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

// 表单字段类型
export interface FormField {
  name: string
  type: 'string' | 'number' | 'boolean' | 'array' | 'object'
  required: boolean
  description?: string
  options?: string[]
  validation?: {
    min?: number
    max?: number
    pattern?: string
  }
}

// 导出相关类型
export interface ExportRequest {
  task_id: string
  format: 'json' | 'csv' | 'excel'
  include_original: boolean
}

export interface ExportResponse {
  export_id: string
  download_url: string
  created_at: string
} 