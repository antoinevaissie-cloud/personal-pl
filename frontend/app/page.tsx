'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import AuthService from '@/lib/auth'
import { getPLSummary, PLSummaryResponse } from '@/lib/api'
import {
  Euro,
  TrendingUp,
  TrendingDown,
  Upload,
  PieChart,
  Calendar,
  AlertCircle,
  ArrowUpRight,
  ArrowDownRight,
  Wallet,
  CreditCard,
  Activity,
  Target,
  ChevronRight,
  FileText,
  BarChart3,
  DollarSign,
  Users,
  ArrowRight
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as RePieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts'
import { motion } from 'framer-motion'

// Mock data for charts
const monthlyData = [
  { month: 'Mar', income: 5500, expenses: 3200, net: 2300 },
  { month: 'Apr', income: 5800, expenses: 3500, net: 2300 },
  { month: 'May', income: 5926, expenses: 3421, net: 2505 },
  { month: 'Jun', income: 6100, expenses: 3100, net: 3000 },
  { month: 'Jul', income: 5900, expenses: 3800, net: 2100 },
  { month: 'Aug', income: 5926, expenses: 229, net: 5697 },
]

const categoryData = [
  { name: 'Housing', value: 1500, color: '#3b82f6' },
  { name: 'Food', value: 600, color: '#10b981' },
  { name: 'Transport', value: 400, color: '#f59e0b' },
  { name: 'Entertainment', value: 300, color: '#8b5cf6' },
  { name: 'Other', value: 200, color: '#ef4444' },
]

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-card p-3 rounded-lg shadow-lg border">
        <p className="font-medium text-sm">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {entry.name}: €{entry.value.toLocaleString()}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export default function HomePage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [currentMonth, setCurrentMonth] = useState('')
  const [lastMonthData, setLastMonthData] = useState<PLSummaryResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const userInfo = AuthService.getUser()
    if (!userInfo) {
      router.push('/login')
      return
    }
    setUser(userInfo)

    const now = new Date()
    const monthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    setCurrentMonth(monthStr)

    // Load last month's data
    loadDashboardData(monthStr)
  }, [])

  async function loadDashboardData(month: string) {
    try {
      const response = await getPLSummary(month, [])
      setLastMonthData(response)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const stats = [
    {
      title: 'Total Income',
      value: '€5,926.24',
      change: '+12.5%',
      trend: 'up',
      icon: TrendingUp,
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-950',
    },
    {
      title: 'Total Expenses',
      value: '€229.38',
      change: '-8.3%',
      trend: 'down',
      icon: TrendingDown,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-950',
    },
    {
      title: 'Net Savings',
      value: '€5,696.86',
      change: '+15.2%',
      trend: 'up',
      icon: Wallet,
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-50 dark:bg-purple-950',
    },
    {
      title: 'Savings Rate',
      value: '96.1%',
      change: '+2.1%',
      trend: 'up',
      icon: Target,
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-50 dark:bg-orange-950',
    },
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100
      }
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-32 w-full" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Welcome Header */}
      <motion.div variants={itemVariants} className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 p-8 text-white">
        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, {user?.username || 'User'}! 👋
          </h1>
          <p className="text-blue-100 text-lg">
            Here's your financial overview for {new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </p>
        </div>
        <div className="absolute right-0 top-0 -mt-4 -mr-4 h-40 w-40 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute left-0 bottom-0 -mb-4 -ml-4 h-32 w-32 rounded-full bg-white/10 blur-2xl" />
      </motion.div>

      {/* KPI Cards */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index} className="relative overflow-hidden">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <div className={cn('p-2 rounded-lg', stat.bgColor)}>
                  <Icon className={cn('h-4 w-4', stat.color)} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="flex items-center text-xs mt-2">
                  {stat.trend === 'up' ? (
                    <ArrowUpRight className="mr-1 h-3 w-3 text-green-600 dark:text-green-400" />
                  ) : (
                    <ArrowDownRight className="mr-1 h-3 w-3 text-red-600 dark:text-red-400" />
                  )}
                  <span className={stat.trend === 'up' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                    {stat.change}
                  </span>
                  <span className="text-muted-foreground ml-1">from last month</span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </motion.div>

      {/* Charts Section */}
      <motion.div variants={itemVariants} className="grid gap-6 md:grid-cols-7">
        {/* Trend Chart */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Income & Expense Trend</CardTitle>
            <CardDescription>Your financial performance over the last 6 months</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={monthlyData}>
                <defs>
                  <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="colorExpenses" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="month" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="income"
                  stroke="#10b981"
                  fillOpacity={1}
                  fill="url(#colorIncome)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="expenses"
                  stroke="#ef4444"
                  fillOpacity={1}
                  fill="url(#colorExpenses)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Category Breakdown */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Expense Categories</CardTitle>
            <CardDescription>Breakdown of your spending this month</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RePieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </RePieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {categoryData.map((category, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: category.color }} />
                    <span className="text-sm">{category.name}</span>
                  </div>
                  <span className="text-sm font-medium">€{category.value.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Quick Actions & Recent Activity */}
      <motion.div variants={itemVariants} className="grid gap-6 md:grid-cols-2">
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and workflows</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/upload" className="block">
              <Button variant="outline" className="w-full justify-between group">
                <div className="flex items-center">
                  <Upload className="mr-3 h-4 w-4" />
                  <div className="text-left">
                    <p className="font-medium">Upload Bank Statement</p>
                    <p className="text-xs text-muted-foreground">Import CSV files</p>
                  </div>
                </div>
                <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/pl" className="block">
              <Button variant="outline" className="w-full justify-between group">
                <div className="flex items-center">
                  <PieChart className="mr-3 h-4 w-4" />
                  <div className="text-left">
                    <p className="font-medium">View P&L Analysis</p>
                    <p className="text-xs text-muted-foreground">Detailed breakdown</p>
                  </div>
                </div>
                <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/transactions" className="block">
              <Button variant="outline" className="w-full justify-between group">
                <div className="flex items-center">
                  <FileText className="mr-3 h-4 w-4" />
                  <div className="text-left">
                    <p className="font-medium">Browse Transactions</p>
                    <p className="text-xs text-muted-foreground">All records</p>
                  </div>
                </div>
                <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest financial events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-green-100 dark:bg-green-900 rounded-full">
                  <ArrowUpRight className="h-4 w-4 text-green-600 dark:text-green-400" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Salary Received</p>
                  <p className="text-xs text-muted-foreground">2 days ago</p>
                </div>
                <span className="text-sm font-medium text-green-600 dark:text-green-400">+€5,926.24</span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-red-100 dark:bg-red-900 rounded-full">
                  <ArrowDownRight className="h-4 w-4 text-red-600 dark:text-red-400" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Grocery Shopping</p>
                  <p className="text-xs text-muted-foreground">3 days ago</p>
                </div>
                <span className="text-sm font-medium text-red-600 dark:text-red-400">-€127.89</span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-full">
                  <Activity className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">CSV Import</p>
                  <p className="text-xs text-muted-foreground">1 week ago</p>
                </div>
                <Badge variant="secondary">42 transactions</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Goals Progress */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Financial Goals</CardTitle>
            <CardDescription>Track your progress towards financial targets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Emergency Fund</span>
                  <span className="text-sm text-muted-foreground">€15,000 / €20,000</span>
                </div>
                <Progress value={75} className="h-2" />
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Vacation Savings</span>
                  <span className="text-sm text-muted-foreground">€2,800 / €5,000</span>
                </div>
                <Progress value={56} className="h-2" />
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Investment Portfolio</span>
                  <span className="text-sm text-muted-foreground">€28,431 / €50,000</span>
                </div>
                <Progress value={57} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}