import React, { useEffect } from 'react'
import { Spin } from 'antd'
import { useAuthStore } from '../stores/authStore'

interface AuthInitializerProps {
  children: React.ReactNode
}

const AuthInitializer: React.FC<AuthInitializerProps> = ({ children }) => {
  const { isInitialized, isLoading, initializeAuth, logout } = useAuthStore()

  useEffect(() => {
    if (!isInitialized) {
      initializeAuth()
    }
  }, [isInitialized, initializeAuth])

  // 监听token失效事件
  useEffect(() => {
    const handleAuthCleared = () => {
      logout()
    }

    window.addEventListener('auth-cleared', handleAuthCleared)
    
    return () => {
      window.removeEventListener('auth-cleared', handleAuthCleared)
    }
  }, [logout])

  // 如果还在初始化中，显示加载状态
  if (!isInitialized || isLoading) {
    return (
      <div 
        style={{ 
          height: '100vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          flexDirection: 'column',
          gap: '16px'
        }}
      >
        <Spin size="large" />
        <div style={{ color: '#666', fontSize: '14px' }}>
          正在初始化系统...
        </div>
      </div>
    )
  }

  return <>{children}</>
}

export default AuthInitializer 