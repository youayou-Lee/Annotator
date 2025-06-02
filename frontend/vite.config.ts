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
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
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
  },
  define: {
    // 配置Monaco Editor使用本地资源
    'process.env.MONACO_EDITOR_CDN': JSON.stringify(false),
  },
  optimizeDeps: {
    include: ['@monaco-editor/react', 'monaco-editor'],
  },
}) 