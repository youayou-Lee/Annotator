import { create } from 'zustand'
import type { Task, AnnotationData } from '../types'

interface TaskState {
  tasks: Task[]
  currentTask: Task | null
  currentAnnotation: AnnotationData | null
  isLoading: boolean
  error: string | null
}

interface TaskActions {
  setTasks: (tasks: Task[]) => void
  addTask: (task: Task) => void
  updateTask: (taskId: string, updates: Partial<Task>) => void
  deleteTask: (taskId: string) => void
  setCurrentTask: (task: Task | null) => void
  setCurrentAnnotation: (annotation: AnnotationData | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useTaskStore = create<TaskState & TaskActions>((set) => ({
  // 状态
  tasks: [],
  currentTask: null,
  currentAnnotation: null,
  isLoading: false,
  error: null,

  // 操作
  setTasks: (tasks) => set({ tasks }),
  
  addTask: (task) => set((state) => ({ 
    tasks: [...state.tasks, task] 
  })),
  
  updateTask: (taskId, updates) => set((state) => ({
    tasks: state.tasks.map(task => 
      task.id === taskId ? { ...task, ...updates } : task
    ),
    currentTask: state.currentTask?.id === taskId 
      ? { ...state.currentTask, ...updates } 
      : state.currentTask
  })),
  
  deleteTask: (taskId) => set((state) => ({
    tasks: state.tasks.filter(task => task.id !== taskId),
    currentTask: state.currentTask?.id === taskId ? null : state.currentTask
  })),
  
  setCurrentTask: (currentTask) => set({ currentTask }),
  
  setCurrentAnnotation: (currentAnnotation) => set({ currentAnnotation }),
  
  setLoading: (isLoading) => set({ isLoading }),
  
  setError: (error) => set({ error }),
  
  clearError: () => set({ error: null }),
})) 