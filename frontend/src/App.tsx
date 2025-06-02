import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import { App as AntdApp, ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import AuthInitializer from './components/AuthInitializer'
import AppRouter from './router'
import './App.css'

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <AntdApp>
        <div className="App">
          <BrowserRouter>
            <AuthInitializer>
              <AppRouter />
            </AuthInitializer>
          </BrowserRouter>
        </div>
      </AntdApp>
    </ConfigProvider>
  )
}

export default App 