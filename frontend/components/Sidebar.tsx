'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { 
  FileText, 
  TrendingUp, 
  DollarSign, 
  ClipboardList 
} from 'lucide-react'
import { cn } from '@/lib/utils'
import AuthService from '@/lib/auth'

interface SidebarItem {
  label: string
  href: string
  icon: React.ElementType
  isActive?: boolean
  isDisabled?: boolean
}

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()

  const navigationItems: SidebarItem[] = [
    {
      label: 'Budget / P&L',
      href: '/pl',
      icon: FileText,
      isActive: pathname === '/pl' || pathname === '/' || pathname === '/upload' || pathname === '/transactions'
    },
    {
      label: 'Net Worth',
      href: '#',
      icon: TrendingUp,
      isDisabled: true
    },
    {
      label: 'Cash Flow',
      href: '#',
      icon: DollarSign,
      isDisabled: true
    },
    {
      label: 'Review Log',
      href: '/journal',
      icon: ClipboardList,
      isActive: pathname === '/journal'
    }
  ]

  const handleLogout = async () => {
    await AuthService.logout()
    router.push('/login')
  }

  return (
    <div className="fixed left-0 top-0 h-full w-[240px] bg-[#F5F6F8] border-r border-gray-200">
      {/* Logo */}
      <div className="flex items-center gap-2 px-6 py-6 border-b border-gray-200">
        <div className="w-8 h-8 bg-gray-900 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-lg">$</span>
        </div>
        <div>
          <h1 className="font-semibold text-gray-900">FinanceHub</h1>
          <p className="text-xs text-gray-500">Personal Dashboard</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4">
        <div className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon
            const isActive = item.isActive && !item.isDisabled
            
            if (item.isDisabled) {
              return (
                <div
                  key={item.label}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-400 cursor-not-allowed"
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
              )
            }

            return (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive 
                    ? "bg-gray-900 text-white" 
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </div>
      </nav>

      {/* User Section */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <button
          onClick={handleLogout}
          className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        >
          Sign Out
        </button>
      </div>
    </div>
  )
}