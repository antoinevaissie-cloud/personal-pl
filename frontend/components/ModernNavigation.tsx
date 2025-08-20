'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import AuthService from '@/lib/auth'
import {
  LayoutDashboard,
  Upload,
  Receipt,
  BookOpen,
  TrendingUp,
  Settings,
  LogOut,
  Menu,
  X,
  User,
  ChevronRight,
  Home,
  Euro,
  PieChart,
  FileText,
  Calendar
} from 'lucide-react'
import { ThemeToggle } from '@/components/theme-toggle'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'

interface NavItem {
  name: string
  href: string
  icon: React.ElementType
  badge?: string
}

const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'P&L Analysis', href: '/pl', icon: PieChart },
  { name: 'Upload Files', href: '/upload', icon: Upload },
  { name: 'Transactions', href: '/transactions', icon: Receipt },
  { name: 'Journal', href: '/journal', icon: BookOpen },
]

export default function ModernNavigation({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [currentMonth, setCurrentMonth] = useState('')

  useEffect(() => {
    const userInfo = AuthService.getUser()
    setUser(userInfo)
    
    // Set current month
    const now = new Date()
    const monthName = now.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    setCurrentMonth(monthName)
  }, [pathname])

  const handleLogout = () => {
    AuthService.logout()
    router.push('/login')
  }

  const isAuthPage = pathname === '/login' || pathname === '/register'

  if (isAuthPage) {
    return <>{children}</>
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={cn(
        "fixed top-0 left-0 z-50 h-full w-64 transform bg-card border-r transition-transform duration-200 ease-in-out",
        "lg:relative lg:translate-x-0",
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-4 border-b">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Euro className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                FinanceHub
              </span>
            </Link>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* User info */}
          {user && (
            <div className="px-4 py-4 border-b bg-muted/50">
              <div className="flex items-center space-x-3">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.username}`} />
                  <AvatarFallback className="bg-gradient-to-br from-blue-400 to-purple-500">
                    <User className="w-6 h-6 text-white" />
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-semibold">{user.username}</p>
                  <p className="text-xs text-muted-foreground">{currentMonth}</p>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <ScrollArea className="flex-1 px-2 py-4">
            <nav className="space-y-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                const Icon = item.icon
                
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      "group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all",
                      isActive 
                        ? "bg-primary/10 text-primary border-l-4 border-primary" 
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                  >
                    <Icon className={cn(
                      "mr-3 h-5 w-5 flex-shrink-0 transition-colors",
                      isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                    )} />
                    <span className="flex-1">{item.name}</span>
                    {item.badge && (
                      <Badge variant="secondary" className="ml-auto">
                        {item.badge}
                      </Badge>
                    )}
                    {isActive && (
                      <ChevronRight className="ml-auto h-4 w-4 text-primary" />
                    )}
                  </Link>
                )
              })}
            </nav>
          </ScrollArea>

          {/* Quick Stats */}
          <div className="px-4 py-4 border-t bg-muted/50">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs text-muted-foreground">This Month</span>
                <span className="text-xs font-semibold text-green-600 dark:text-green-400">+€5,926.24</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-muted-foreground">YTD Net</span>
                <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">+€28,431.00</span>
              </div>
            </div>
          </div>

          {/* Bottom section */}
          <Separator />
          <div className="px-2 py-2">
            <Button
              variant="ghost"
              className="w-full justify-start text-muted-foreground hover:text-destructive hover:bg-destructive/10"
              onClick={handleLogout}
            >
              <LogOut className="mr-3 h-5 w-5" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-card border-b backdrop-blur">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden"
            >
              <Menu className="h-6 w-6" />
            </Button>
            
            {/* Breadcrumb */}
            <div className="flex items-center space-x-2 text-sm">
              <Link href="/" className="text-muted-foreground hover:text-foreground transition-colors">
                Home
              </Link>
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">
                {navigation.find(item => item.href === pathname)?.name || 'Page'}
              </span>
            </div>

            {/* Right side actions */}
            <div className="flex items-center space-x-4">
              <ThemeToggle />
              <Button variant="ghost" size="icon">
                <Settings className="h-5 w-5" />
              </Button>
              <Separator orientation="vertical" className="hidden sm:block h-6" />
              <div className="hidden sm:flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">{currentMonth}</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1">
          <div className="p-4 sm:p-6 lg:p-8">
            {children}
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-card border-t mt-auto">
          <div className="px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center text-xs text-muted-foreground">
              <p>© 2025 FinanceHub. Personal finance tracking made simple.</p>
              <div className="flex space-x-4">
                <Link href="/help" className="hover:text-foreground transition-colors">Help</Link>
                <Link href="/privacy" className="hover:text-foreground transition-colors">Privacy</Link>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}