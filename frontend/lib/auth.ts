import { api } from './api'

export interface User {
  id: string
  username: string
  email: string
  is_active: boolean
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

class AuthService {
  private static TOKEN_KEY = 'pl_auth_token'
  private static USER_KEY = 'pl_user'

  static getToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(this.TOKEN_KEY)
  }

  static setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.TOKEN_KEY, token)
      // Also set as cookie for middleware
      document.cookie = `pl_auth_token=${token}; path=/; max-age=${60 * 60 * 24 * 7}` // 7 days
    }
  }

  static removeToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.TOKEN_KEY)
      localStorage.removeItem(this.USER_KEY)
      // Also remove cookie
      document.cookie = 'pl_auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    }
  }

  static getUser(): User | null {
    if (typeof window === 'undefined') return null
    const userStr = localStorage.getItem(this.USER_KEY)
    return userStr ? JSON.parse(userStr) : null
  }

  static setUser(user: User): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.USER_KEY, JSON.stringify(user))
    }
  }

  static async login(credentials: LoginCredentials): Promise<User> {
    try {
      const response = await fetch(`${api.baseURL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }

      const data = await response.json()
      this.setToken(data.access_token)

      // Get user info
      const user = await this.getCurrentUser()
      return user
    } catch (error) {
      throw error
    }
  }

  static async register(data: RegisterData): Promise<User> {
    try {
      const response = await fetch(`${api.baseURL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
      }

      return await response.json()
    } catch (error) {
      throw error
    }
  }

  static async getCurrentUser(): Promise<User> {
    const token = this.getToken()
    if (!token) {
      throw new Error('No authentication token')
    }

    try {
      const response = await fetch(`${api.baseURL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          this.removeToken()
        }
        throw new Error('Failed to get user info')
      }

      const user = await response.json()
      this.setUser(user)
      return user
    } catch (error) {
      throw error
    }
  }

  static async logout(): Promise<void> {
    const token = this.getToken()
    if (token) {
      try {
        await fetch(`${api.baseURL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      } catch (error) {
        console.error('Logout error:', error)
      }
    }
    this.removeToken()
  }

  static isAuthenticated(): boolean {
    return !!this.getToken()
  }
}

export default AuthService