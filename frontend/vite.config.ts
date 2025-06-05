import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://192.168.103.164:8000',
        changeOrigin: true,
        secure: false,
      },
    },
    fs: {
      // 允许访问 node_modules 中的 monaco-editor 文件
      allow: ['..']
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          antd: ['antd'],
          router: ['react-router-dom'],
          monaco: ['@monaco-editor/react', 'monaco-editor'],
        },
      },
    },
    // 复制 monaco-editor 静态资源
    copyPublicDir: true,
  },
  define: {
    // 确保 Monaco Editor 使用正确的路径
    global: 'globalThis',
  },
  optimizeDeps: {
    include: ['@monaco-editor/react', 'monaco-editor'],
    exclude: []
  },
  worker: {
    format: 'es',
    plugins: [react()]
  },
  assetsInclude: ['**/*.wasm'],
  // 静态资源处理
  publicDir: 'public',
  // 改善 Monaco Editor 的错误处理
  esbuild: {
    // 忽略某些警告
    logOverride: {
      'this-is-undefined-in-esm': 'silent'
    }
  }
}) 