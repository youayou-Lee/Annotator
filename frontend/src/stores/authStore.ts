import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '../types'
import { authAPI } from '../services/api'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  isInitialized: boolean
}

interface AuthActions {
  setUser: (user: User) => void
  setToken: (token: string) => void
  login: (user: User, token: string) => void
  logout: () => void
  setLoading: (loading: boolean) => void
  initializeAuth: () => Promise<void>
  refreshUserInfo: () => Promise<void>
  hasPermission: (permission: string) => boolean
  hasRole: (role: string | string[]) => boolean
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // 状态
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      isInitialized: false,

      // 操作
      setUser: (user) => set({ user }),
      
      setToken: (token) => set({ token }),
      
      login: (user, token) => set({ 
        user, 
        token, 
        isAuthenticated: true,
        isLoading: false,
        isInitialized: true
      }),
      
      logout: () => {
        // 清除localStorage中的token
        localStorage.removeItem('auth-storage')
        set({ 
          user: null, 
          token: null, 
          isAuthenticated: false,
          isLoading: false,
          isInitialized: true
        })
      },
      
      setLoading: (isLoading) => set({ isLoading }),

      // 初始化认证状态
      initializeAuth: async () => {
        const state = get()
        if (state.token && !state.isInitialized) {
          set({ isLoading: true })
          try {
            const response = await authAPI.getMe()
            if (response.success && response.data) {
              set({
                user: response.data,
                isAuthenticated: true,
                isInitialized: true,
                isLoading: false
              })
            } else {
              // Token无效，清除状态
              get().logout()
            }
          } catch (error) {
            console.error('初始化认证失败:', error)
            get().logout()
          }
        } else {
          set({ isInitialized: true, isLoading: false })
        }
      },

      // 刷新用户信息
      refreshUserInfo: async () => {
        const state = get()
        if (state.token && state.isAuthenticated) {
          try {
            const response = await authAPI.getMe()
            if (response.success && response.data) {
              set({ user: response.data })
            }
          } catch (error) {
            console.error('刷新用户信息失败:', error)
            // 如果是401错误，说明token过期，执行登出
            if ((error as any)?.response?.status === 401) {
              get().logout()
            }
          }
        }
      },

      // 权限检查
      hasPermission: (permission: string) => {
        const state = get()
        if (!state.user || !state.isAuthenticated) return false
        
        const { role } = state.user
        
        // 权限映射
        const permissions: Record<string, string[]> = {
          'user.manage': ['super_admin', 'admin'],
          'file.upload': ['super_admin', 'admin', 'annotator'],
          'file.delete.all': ['super_admin', 'admin'],
          'file.delete.own': ['super_admin', 'admin', 'annotator'],
          'task.create': ['super_admin', 'admin'],
          'task.assign': ['super_admin', 'admin'],
          'task.annotate': ['super_admin', 'admin', 'annotator'],
          'task.review': ['super_admin', 'admin'],
          'task.export': ['super_admin', 'admin'],
        }
        
        return permissions[permission]?.includes(role) || false
      },

      // 角色检查
      hasRole: (role: string | string[]) => {
        const state = get()
        if (!state.user || !state.isAuthenticated) return false
        
        const userRole = state.user.role
        if (Array.isArray(role)) {
          return role.includes(userRole)
        }
        return userRole === role
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
) 