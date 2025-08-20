'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { UploadCloud, TrendingUp, Receipt, BookOpen, LogOut, User } from 'lucide-react'
import { useEffect, useState } from 'react'
import AuthService from '@/lib/auth'

const navigation = [
  { name: 'Upload', href: '/upload', icon: UploadCloud },
  { name: 'P&L Dashboard', href: '/pl', icon: TrendingUp },
  { name: 'Transactions', href: '/transactions', icon: Receipt },
  { name: 'Journal', href: '/journal', icon: BookOpen },
]

export default function Navigation() {
  const pathname = usePathname()
  const [user, setUser] = useState<any>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check authentication status
    const checkAuth = () => {
      const authStatus = AuthService.isAuthenticated()
      setIsAuthenticated(authStatus)
      if (authStatus) {
        const currentUser = AuthService.getUser()
        setUser(currentUser)
      }
    }
    
    checkAuth()
    // Check on focus to catch login/logout from other tabs
    window.addEventListener('focus', checkAuth)
    return () => window.removeEventListener('focus', checkAuth)
  }, [pathname]) // Re-check when route changes

  const handleLogout = async () => {
    await AuthService.logout()
    window.location.href = '/login'
  }

  return (
    <nav className="bg-white shadow">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/" className="text-xl font-bold text-gray-900">
                Personal P&L
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium',
                      isActive
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    )}
                  >
                    <Icon className="mr-2 h-4 w-4" />
                    {item.name}
                  </Link>
                )
              })}
            </div>
          </div>
          
          {/* User menu */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && user ? (
              <div className="flex items-center space-x-3">
                <div className="flex items-center text-sm text-gray-700">
                  <User className="h-5 w-5 mr-1 text-gray-400" />
                  <span className="hidden sm:block">{user.username}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <LogOut className="h-4 w-4 mr-1" />
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  href="/login"
                  className="text-sm font-medium text-gray-700 hover:text-gray-900"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="inline-flex items-center px-3 py-1.5 border border-blue-600 text-sm font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div className="sm:hidden">
        <div className="pt-2 pb-3 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center pl-3 pr-4 py-2 border-l-4 text-base font-medium',
                  isActive
                    ? 'bg-blue-50 border-blue-500 text-blue-700'
                    : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700'
                )}
              >
                <Icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
          
          {/* Mobile user section */}
          {isAuthenticated && user && (
            <div className="border-t border-gray-200 pt-3 pb-3">
              <div className="flex items-center px-4">
                <User className="h-5 w-5 mr-2 text-gray-400" />
                <span className="text-base font-medium text-gray-700">{user.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="mt-2 flex items-center w-full pl-3 pr-4 py-2 text-base font-medium text-gray-700 hover:bg-gray-50"
              >
                <LogOut className="mr-3 h-5 w-5 text-gray-400" />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}