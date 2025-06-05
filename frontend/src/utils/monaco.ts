import { loader } from '@monaco-editor/react'
import * as monaco from 'monaco-editor'

// Monaco Editor 配置 - 最简化版本，禁用 Worker
export const configureMonaco = () => {
  // 配置 loader 使用本地的 monaco-editor
  loader.config({ monaco })
  
  // 设置全局 Monaco Environment - 禁用所有 Worker
  if (typeof window !== 'undefined') {
    (window as any).MonacoEnvironment = {
      getWorkerUrl: () => {
        // 返回一个空的 worker，实际上禁用了 worker 功能
        return `data:text/javascript;charset=utf-8,${encodeURIComponent(`
          // Empty worker - no background processing
          self.addEventListener('message', function(e) {
            // 简单回应，不做任何处理
            self.postMessage({ id: e.data.id, result: null });
          });
        `)}`
      }
    }
    
    // 抑制所有 Monaco Editor 和 Worker 相关的错误
    const originalConsoleError = console.error
    const originalConsoleWarn = console.warn
    
    console.error = (...args) => {
      const message = String(args[0] || '')
      if (
        message.includes('monaco') ||
        message.includes('worker') ||
        message.includes('Worker') ||
        message.includes('simpleWorker') ||
        message.includes('defaultWorkerFactory') ||
        message.includes('errors.js')
      ) {
        return // 静默处理
      }
      originalConsoleError.apply(console, args)
    }
    
    console.warn = (...args) => {
      const message = String(args[0] || '')
      if (
        message.includes('monaco') ||
        message.includes('worker') ||
        message.includes('Worker')
      ) {
        return // 静默处理
      }
      originalConsoleWarn.apply(console, args)
    }
    
    // 全局错误处理 - 完全静默 Monaco 和 Worker 错误
    window.addEventListener('error', (event) => {
      const error = String(event.error || event.message || '')
      const filename = event.filename || ''
      const source = event.target?.toString() || ''
      
      if (
        filename.includes('monaco') ||
        filename.includes('worker') ||
        filename.includes('errors.js') ||
        filename.includes('simpleWorker.js') ||
        filename.includes('defaultWorkerFactory.js') ||
        error.includes('monaco') ||
        error.includes('worker') ||
        error.includes('Worker') ||
        source.includes('Worker')
      ) {
        event.stopPropagation()
        event.preventDefault()
        return false
      }
    }, true)
    
    window.addEventListener('unhandledrejection', (event) => {
      const reason = String(event.reason || '')
      if (
        reason.includes('monaco') ||
        reason.includes('worker') ||
        reason.includes('Worker') ||
        reason.includes('simpleWorker')
      ) {
        event.stopPropagation()
        event.preventDefault()
      }
    }, true)
  }

  console.log('Monaco Editor configured without workers')
}

export default configureMonaco 