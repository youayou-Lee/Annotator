import { loader } from '@monaco-editor/react'
import * as monaco from 'monaco-editor'

// Monaco Editor 配置 - 使用本地资源，避免 CDN 加载
export const configureMonaco = () => {
  // 配置 loader 使用本地的 monaco-editor
  loader.config({ monaco })
  
  // 设置全局 Monaco Environment
  if (typeof window !== 'undefined') {
    (window as any).MonacoEnvironment = {
      getWorker: (workerId: string, label: string) => {
        // 根据语言类型返回对应的 worker
        const getWorkerUrl = (moduleId: string, label: string) => {
          switch (label) {
            case 'json':
              return new URL('monaco-editor/esm/vs/language/json/json.worker', import.meta.url)
            case 'css':
            case 'scss':
            case 'less':
              return new URL('monaco-editor/esm/vs/language/css/css.worker', import.meta.url)
            case 'html':
            case 'handlebars':
            case 'razor':
              return new URL('monaco-editor/esm/vs/language/html/html.worker', import.meta.url)
            case 'typescript':
            case 'javascript':
              return new URL('monaco-editor/esm/vs/language/typescript/ts.worker', import.meta.url)
            default:
              return new URL('monaco-editor/esm/vs/editor/editor.worker', import.meta.url)
          }
        }
        
        return new Worker(getWorkerUrl(workerId, label), {
          type: 'module'
        })
      }
    }
  }

  console.log('Monaco Editor configured to use local resources')
}

export default configureMonaco 