'use client'

import React, { useEffect, useState } from 'react'
import { getPLSummary, PLSummaryResponse } from '@/lib/api'
import { 
  ChevronDown, 
  ChevronRight, 
  TrendingUp, 
  TrendingDown,
  Download,
  Filter,
  ArrowUpRight,
  ArrowDownRight,
  MoreVertical
} from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'
import { toast } from 'sonner'

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
        <p className="font-medium text-sm text-gray-900">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm mt-1" style={{ color: entry.color }}>
            {entry.name}: €{entry.value.toLocaleString()}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export default function PLPage() {
  const [month, setMonth] = useState<string>('')
  const [accounts, setAccounts] = useState<string[]>(['Boursorama', 'BNP', 'Revolut'])
  const [data, setData] = useState<PLSummaryResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())
  const [selectedPeriod, setSelectedPeriod] = useState<'month' | 'quarter' | 'year'>('month')

  async function run() {
    if (!month) return
    setLoading(true)
    try {
      const res = await getPLSummary({ month, accounts })
      setData(res)
    } catch (error) {
      console.error('Failed to load P&L data:', error)
      toast.error('Failed to load P&L data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const now = new Date()
    const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    setMonth(currentMonth)
  }, [])

  useEffect(() => {
    if (month && accounts.length > 0) {
      run()
    }
  }, [month, accounts])

  function toggleCategory(categoryName: string) {
    setExpandedCategories(prev => {
      const newSet = new Set(prev)
      if (newSet.has(categoryName)) {
        newSet.delete(categoryName)
      } else {
        newSet.add(categoryName)
      }
      return newSet
    })
  }

  const totalIncome = data?.summary?.income || 0
  const totalExpenses = Math.abs(data?.summary?.expense || 0)
  const netIncome = data?.summary?.net || 0
  const savingsRate = data?.summary?.savings_rate || 0

  // Mock chart data - in production, would come from API
  const chartData = [
    { month: 'Jan', income: 5200, expenses: 3800 },
    { month: 'Feb', income: 5500, expenses: 4100 },
    { month: 'Mar', income: 5800, expenses: 3900 },
    { month: 'Apr', income: 5600, expenses: 4200 },
    { month: 'May', income: 5900, expenses: 4000 },
    { month: 'Jun', income: 6200, expenses: 4300 },
  ]

  // Get income and expense categories
  const incomeCategories = data?.rows?.filter((row: any) => row.net > 0) || []
  const expenseCategories = data?.rows?.filter((row: any) => row.net < 0) || []

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-100 rounded-lg"></div>
            ))}
          </div>
          <div className="h-96 bg-gray-100 rounded-lg"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Budget & P&L Overview</h1>
          <p className="text-sm text-gray-500 mt-1">Track income, expenses and savings</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Period Selector */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            {(['month', 'quarter', 'year'] as const).map(period => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={cn(
                  "px-3 py-1.5 text-sm font-medium rounded-md capitalize transition-colors",
                  selectedPeriod === period
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                )}
              >
                {period}
              </button>
            ))}
          </div>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Filter className="w-4 h-4 text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Download className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-600">Total Income</p>
            <span className="text-xs text-green-600 flex items-center gap-1">
              <ArrowUpRight className="w-3 h-3" />
              +12.5%
            </span>
          </div>
          <p className="text-2xl font-semibold text-gray-900">
            €{totalIncome.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-600">Total Expenses</p>
            <span className="text-xs text-red-600 flex items-center gap-1">
              <ArrowUpRight className="w-3 h-3" />
              +5.2%
            </span>
          </div>
          <p className="text-2xl font-semibold text-gray-900">
            €{totalExpenses.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-600">Net Income</p>
            <span className={cn(
              "text-xs flex items-center gap-1",
              netIncome >= 0 ? "text-green-600" : "text-red-600"
            )}>
              {netIncome >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
              {netIncome >= 0 ? '+' : ''}{((netIncome / totalIncome) * 100).toFixed(1)}%
            </span>
          </div>
          <p className={cn(
            "text-2xl font-semibold",
            netIncome >= 0 ? "text-green-600" : "text-red-600"
          )}>
            €{Math.abs(netIncome).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-600">Savings Rate</p>
            <span className={cn(
              "text-xs flex items-center gap-1",
              savingsRate >= 20 ? "text-green-600" : "text-orange-600"
            )}>
              {savingsRate >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              Target: 20%
            </span>
          </div>
          <p className="text-2xl font-semibold text-gray-900">
            {savingsRate.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Trend Analysis</h2>
          <button className="p-1 hover:bg-gray-100 rounded">
            <MoreVertical className="w-4 h-4 text-gray-600" />
          </button>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorExpenses" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#EF4444" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="month" stroke="#6B7280" fontSize={12} />
            <YAxis stroke="#6B7280" fontSize={12} />
            <Tooltip content={<CustomTooltip />} />
            <Area 
              type="monotone" 
              dataKey="income" 
              stroke="#10B981" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorIncome)" 
              name="Income"
            />
            <Area 
              type="monotone" 
              dataKey="expenses" 
              stroke="#EF4444" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorExpenses)" 
              name="Expenses"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Categories Table */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Category Breakdown</h2>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">
                {data?.rows?.length || 0} categories
              </span>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="text-right p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th className="text-right p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">% of Total</th>
                <th className="text-right p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Variance</th>
                <th className="p-4"></th>
              </tr>
            </thead>
            <tbody>
              {/* Income Categories */}
              {incomeCategories.length > 0 && (
                <>
                  <tr className="bg-green-50 border-b border-gray-200">
                    <td colSpan={6} className="px-4 py-2 text-sm font-medium text-green-900">
                      Income Categories
                    </td>
                  </tr>
                  {incomeCategories.map((category: any) => (
                    <React.Fragment key={category.category}>
                      <tr className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="p-4">
                          <button
                            onClick={() => toggleCategory(category.category)}
                            className="flex items-center gap-2 text-sm font-medium text-gray-900"
                          >
                            {category.subs && category.subs.length > 0 && (
                              expandedCategories.has(category.category) 
                                ? <ChevronDown className="w-4 h-4" />
                                : <ChevronRight className="w-4 h-4" />
                            )}
                            {category.category}
                          </button>
                        </td>
                        <td className="p-4">
                          <span className="badge-income">Income</span>
                        </td>
                        <td className="p-4 text-right text-sm font-medium text-gray-900">
                          €{category.net.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </td>
                        <td className="p-4 text-right text-sm text-gray-600">
                          {((category.net / totalIncome) * 100).toFixed(1)}%
                        </td>
                        <td className="p-4 text-right">
                          <span className="variance-positive">
                            <ArrowUpRight className="w-3 h-3" />
                            +8.2%
                          </span>
                        </td>
                        <td className="p-4 text-right">
                          <button className="p-1 hover:bg-gray-100 rounded">
                            <MoreVertical className="w-4 h-4 text-gray-400" />
                          </button>
                        </td>
                      </tr>
                      {expandedCategories.has(category.category) && category.subs?.map((sub: any, idx: number) => (
                        <tr key={idx} className="bg-gray-50 border-b border-gray-100">
                          <td className="pl-12 pr-4 py-2 text-sm text-gray-600">{sub.name}</td>
                          <td className="px-4 py-2 text-sm text-gray-500">Subcategory</td>
                          <td className="px-4 py-2 text-right text-sm text-gray-600">
                            €{sub.net.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </td>
                          <td colSpan={3}></td>
                        </tr>
                      ))}
                    </React.Fragment>
                  ))}
                </>
              )}

              {/* Expense Categories */}
              {expenseCategories.length > 0 && (
                <>
                  <tr className="bg-red-50 border-b border-gray-200">
                    <td colSpan={6} className="px-4 py-2 text-sm font-medium text-red-900">
                      Expense Categories
                    </td>
                  </tr>
                  {expenseCategories.map((category: any) => (
                    <React.Fragment key={category.category}>
                      <tr className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="p-4">
                          <button
                            onClick={() => toggleCategory(category.category)}
                            className="flex items-center gap-2 text-sm font-medium text-gray-900"
                          >
                            {category.subs && category.subs.length > 0 && (
                              expandedCategories.has(category.category) 
                                ? <ChevronDown className="w-4 h-4" />
                                : <ChevronRight className="w-4 h-4" />
                            )}
                            {category.category}
                          </button>
                        </td>
                        <td className="p-4">
                          <span className={category.category.toLowerCase().includes('tax') ? 'badge-tax' : 'badge-expense'}>
                            {category.category.toLowerCase().includes('tax') ? 'Tax' : 'Expense'}
                          </span>
                        </td>
                        <td className="p-4 text-right text-sm font-medium text-gray-900">
                          €{Math.abs(category.net).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </td>
                        <td className="p-4 text-right text-sm text-gray-600">
                          {((Math.abs(category.net) / totalExpenses) * 100).toFixed(1)}%
                        </td>
                        <td className="p-4 text-right">
                          <span className="variance-negative">
                            <ArrowUpRight className="w-3 h-3" />
                            +3.1%
                          </span>
                        </td>
                        <td className="p-4 text-right">
                          <button className="p-1 hover:bg-gray-100 rounded">
                            <MoreVertical className="w-4 h-4 text-gray-400" />
                          </button>
                        </td>
                      </tr>
                      {expandedCategories.has(category.category) && category.subs?.map((sub: any, idx: number) => (
                        <tr key={idx} className="bg-gray-50 border-b border-gray-100">
                          <td className="pl-12 pr-4 py-2 text-sm text-gray-600">{sub.name}</td>
                          <td className="px-4 py-2 text-sm text-gray-500">Subcategory</td>
                          <td className="px-4 py-2 text-right text-sm text-gray-600">
                            €{Math.abs(sub.net).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </td>
                          <td colSpan={3}></td>
                        </tr>
                      ))}
                    </React.Fragment>
                  ))}
                </>
              )}
            </tbody>
          </table>
        </div>

        {/* Summary Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Income</p>
              <p className="text-lg font-semibold text-green-600">
                €{totalIncome.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Expenses</p>
              <p className="text-lg font-semibold text-red-600">
                €{totalExpenses.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Net Income</p>
              <p className={cn(
                "text-lg font-semibold",
                netIncome >= 0 ? "text-green-600" : "text-red-600"
              )}>
                €{Math.abs(netIncome).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}