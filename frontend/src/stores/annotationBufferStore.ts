import { create } from 'zustand'
import { annotationAPI } from '../services/api'

// 文档数据接口
interface DocumentData {
  id: string
  filename: string
  originalContent: any
  annotatedContent: any
  status: 'pending' | 'in_progress' | 'completed'
}

// 标注缓存状态接口
interface AnnotationBufferState {
  // 数据状态
  taskId: string | null
  documents: Map<string, DocumentData>
  template: any
  currentDocumentId: string | null
  isDirty: boolean
  isLoading: boolean
  
  // 操作方法
  loadTaskData: (taskId: string) => Promise<void>
  setCurrentDocument: (documentId: string) => void
  updateAnnotation: (documentId: string, annotatedData: any) => void
  saveToBackend: () => Promise<void>
  clearBuffer: () => void
  
  // 获取器
  getCurrentDocument: () => DocumentData | null
  getAllDocuments: () => DocumentData[]
}

export const useAnnotationBufferStore = create<AnnotationBufferState>((set, get) => ({
  // 初始状态
  taskId: null,
  documents: new Map(),
  template: null,
  currentDocumentId: null,
  isDirty: false,
  isLoading: false,

  // 加载任务数据到缓存
  loadTaskData: async (taskId: string) => {
    set({ isLoading: true })
    try {
      // 获取任务文档列表
      const documentsResponse = await annotationAPI.getDocuments(taskId)
      if (!documentsResponse.success) {
        throw new Error(documentsResponse.message)
      }

      const documents = new Map<string, DocumentData>()
      
      // 逐个加载文档内容和标注数据
      for (const doc of documentsResponse.data.documents) {
        const documentId = doc.document_id || doc.id
        
        // 获取原始文档内容
        const contentResponse = await annotationAPI.getDocumentContent(taskId, documentId)
        const originalContent = contentResponse.success ? contentResponse.data.content : {}
        
        // 获取已有标注数据
        const annotationResponse = await annotationAPI.getAnnotation(taskId, documentId)
        const annotatedContent = annotationResponse.success ? annotationResponse.data.annotated_data : {}
        
        documents.set(documentId, {
          id: documentId,
          filename: doc.document_name || doc.filename,
          originalContent,
          annotatedContent,
          status: doc.status || 'pending'
        })
      }

      // 获取模板配置（使用第一个文档的配置）
      let template = null
      if (documents.size > 0) {
        const firstDocId = Array.from(documents.keys())[0]
        const templateResponse = await annotationAPI.getFormConfig(taskId, firstDocId)
        template = templateResponse.success ? templateResponse.data : null
      }

      set({
        taskId,
        documents,
        template,
        currentDocumentId: documents.size > 0 ? Array.from(documents.keys())[0] : null,
        isDirty: false,
        isLoading: false
      })
    } catch (error) {
      console.error('加载任务数据失败:', error)
      set({ isLoading: false })
      throw error
    }
  },

  // 设置当前文档
  setCurrentDocument: (documentId: string) => {
    set({ currentDocumentId: documentId })
  },

  // 更新标注数据
  updateAnnotation: (documentId: string, annotatedData: any) => {
    const { documents } = get()
    const document = documents.get(documentId)
    if (document) {
      const updatedDocument = {
        ...document,
        annotatedContent: annotatedData,
        status: 'in_progress' as const
      }
      const newDocuments = new Map(documents)
      newDocuments.set(documentId, updatedDocument)
      
      set({
        documents: newDocuments,
        isDirty: true
      })
    }
  },

  // 保存到后端
  saveToBackend: async () => {
    const { taskId, documents } = get()
    if (!taskId) return

    try {
      // 逐个保存文档的标注数据
      for (const [documentId, document] of documents) {
        if (document.status === 'in_progress' || document.status === 'completed') {
          await annotationAPI.saveAnnotation(taskId, documentId, {
            annotated_data: document.annotatedContent,
            is_auto_save: false
          })
        }
      }
      
      set({ isDirty: false })
    } catch (error) {
      console.error('保存到后端失败:', error)
      throw error
    }
  },

  // 清空缓存
  clearBuffer: () => {
    set({
      taskId: null,
      documents: new Map(),
      template: null,
      currentDocumentId: null,
      isDirty: false,
      isLoading: false
    })
  },

  // 获取当前文档
  getCurrentDocument: () => {
    const { documents, currentDocumentId } = get()
    return currentDocumentId ? documents.get(currentDocumentId) || null : null
  },

  // 获取所有文档
  getAllDocuments: () => {
    const { documents } = get()
    return Array.from(documents.values())
  }
}))