import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import AuthInitializer from './components/AuthInitializer'
import AppRouter from './router'
import './App.css'

const App: React.FC = () => {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthInitializer>
          <AppRouter />
        </AuthInitializer>
      </BrowserRouter>
    </div>
  )
}

export default App 