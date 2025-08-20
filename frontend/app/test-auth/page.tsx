'use client'

import { useState } from 'react'
import AuthService from '@/lib/auth'

export default function TestAuthPage() {
  const [status, setStatus] = useState('')
  const [token, setToken] = useState('')
  const [error, setError] = useState('')

  const testLogin = async () => {
    setStatus('Testing login...')
    setError('')
    try {
      const result = await AuthService.login({
        username: 'testuser',
        password: 'testpass123'
      })
      setStatus('Login successful!')
      const tokenValue = AuthService.getToken()
      setToken(tokenValue || 'No token found')
      console.log('Login result:', result)
      console.log('Token:', tokenValue)
      console.log('Cookies:', document.cookie)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
      console.error('Login error:', err)
    }
  }

  const checkAuth = () => {
    const tokenValue = AuthService.getToken()
    const user = AuthService.getUser()
    const isAuth = AuthService.isAuthenticated()
    setStatus(`Token: ${tokenValue ? 'Present' : 'Missing'}\nUser: ${user ? user.username : 'None'}\nAuthenticated: ${isAuth}`)
    console.log('Token:', tokenValue)
    console.log('User:', user)
    console.log('Cookies:', document.cookie)
  }

  const clearAuth = () => {
    AuthService.removeToken()
    setStatus('Auth cleared')
    setToken('')
    setError('')
  }

  const navigateToPL = () => {
    window.location.href = '/pl'
  }

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Authentication Test Page</h1>
      
      <div className="space-y-4">
        <div className="flex gap-2">
          <button 
            onClick={testLogin}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Test Login (testuser/testpass123)
          </button>
          
          <button 
            onClick={checkAuth}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Check Auth Status
          </button>
          
          <button 
            onClick={clearAuth}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Clear Auth
          </button>
          
          <button 
            onClick={navigateToPL}
            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
          >
            Navigate to /pl
          </button>
        </div>

        {status && (
          <div className="p-4 bg-gray-100 rounded">
            <pre className="whitespace-pre-wrap">{status}</pre>
          </div>
        )}

        {token && (
          <div className="p-4 bg-blue-100 rounded">
            <p className="font-semibold">Token:</p>
            <p className="text-xs break-all">{token}</p>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-100 rounded text-red-700">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </div>
        )}

        <div className="mt-8 p-4 bg-yellow-50 rounded">
          <p className="font-semibold mb-2">Instructions:</p>
          <ol className="list-decimal list-inside space-y-1 text-sm">
            <li>Click "Test Login" to authenticate</li>
            <li>Check browser console for detailed logs</li>
            <li>Click "Check Auth Status" to verify token/user storage</li>
            <li>Click "Navigate to /pl" to test protected route access</li>
          </ol>
        </div>
      </div>
    </div>
  )
}