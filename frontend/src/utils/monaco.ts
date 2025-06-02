import { loader } from '@monaco-editor/react'

// Monaco Editor 配置 - 避免 CDN 加载
export const configureMonaco = () => {
  // 设置全局 Monaco Environment，完全避免网络请求
  if (typeof window !== 'undefined') {
    (window as any).MonacoEnvironment = {
      getWorker: () => {
        // 返回一个简单的 worker，避免网络请求
        return new Worker(
          URL.createObjectURL(
            new Blob([`
              self.onmessage = function() {
                // 简单的 worker，不做任何操作
                self.postMessage({});
              };
            `], { type: 'application/javascript' })
          )
        )
      }
    }
  }

  console.log('Monaco Editor configured to use local workers only')
}

export default configureMonaco 