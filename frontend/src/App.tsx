import { useState, useEffect } from 'react'
import { LoginPage } from './components/LoginPage'
import { RegisterPage } from './components/RegisterPage'
import { Dashboard } from './components/Dashboard'
import { authService } from './services/auth'
import './App.css'

type AuthState = 'login' | 'register' | 'dashboard'

function App() {
  const [authState, setAuthState] = useState<AuthState>('login')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already authenticated
    if (authService.isAuthenticated()) {
      setAuthState('dashboard')
    }
    setLoading(false)
  }, [])

  const handleLoginSuccess = () => {
    setAuthState('dashboard')
  }

  const handleRegisterSuccess = () => {
    setAuthState('dashboard')
  }

  const handleLogout = () => {
    setAuthState('login')
  }

  const switchToLogin = () => {
    setAuthState('login')
  }

  const switchToRegister = () => {
    setAuthState('register')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  switch (authState) {
    case 'login':
      return (
        <LoginPage
          onLoginSuccess={handleLoginSuccess}
          onSwitchToRegister={switchToRegister}
        />
      )
    case 'register':
      return (
        <RegisterPage
          onRegisterSuccess={handleRegisterSuccess}
          onSwitchToLogin={switchToLogin}
        />
      )
    case 'dashboard':
      return (
        <Dashboard onLogout={handleLogout} />
      )
    default:
      return null
  }
}

export default App
