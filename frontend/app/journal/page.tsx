'use client'

import { useState } from 'react'
import { 
  Plus,
  Edit3,
  Save,
  X,
  Calendar,
  Tag,
  TrendingUp,
  ChevronRight,
  FileText,
  CheckCircle2,
  AlertCircle,
  Clock,
  ArrowUpRight,
  Filter as FilterIcon
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface ReviewEntry {
  id: string
  date: string
  title: string
  content: string
  tags: string[]
  status: 'completed' | 'in-progress' | 'pending'
  type: 'expense' | 'income' | 'asset' | 'liability'
  action?: string
}

const mockEntries: ReviewEntry[] = [
  {
    id: '1',
    date: '2024-12-15',
    title: 'Giving expenses significantly higher than planned',
    content: 'Set weekly dining out limit of $75 and track via all expenses',
    tags: ['Expense'],
    status: 'in-progress',
    type: 'expense',
    action: 'In Progress'
  },
  {
    id: '2',
    date: '2024-12-10',
    title: 'Freelance income exceeded expectations by 47%',
    content: 'Increase monthly investment contribution by $500',
    tags: ['Income'],
    status: 'completed',
    type: 'income',
    action: 'Completed'
  },
  {
    id: '3',
    date: '2024-12-01',
    title: 'Emergency fund reached 6-month target',
    content: 'Redirect excess savings to investment accounts',
    tags: ['Asset'],
    status: 'completed',
    type: 'asset',
    action: 'Completed'
  },
  {
    id: '4',
    date: '2024-11-28',
    title: 'Credit card balances creeping up due to holiday spending',
    content: 'Create dedicated holiday budget and pay down balances',
    tags: ['Liability'],
    status: 'pending',
    type: 'liability',
    action: 'Pending'
  },
  {
    id: '5',
    date: '2024-11-15',
    title: 'Investment portfolio heavily weighted in tech stocks',
    content: 'Diversify into bonds and international funds',
    tags: ['Asset'],
    status: 'in-progress',
    type: 'asset',
    action: 'In Progress'
  }
]

const statusConfig = {
  'completed': {
    label: 'Completed',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    icon: CheckCircle2
  },
  'in-progress': {
    label: 'In Progress',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    icon: Clock
  },
  'pending': {
    label: 'Pending',
    color: 'text-gray-600',
    bgColor: 'bg-gray-50',
    icon: AlertCircle
  }
}

const typeConfig = {
  'expense': {
    label: 'Expense',
    color: 'text-red-700',
    bgColor: 'bg-red-50'
  },
  'income': {
    label: 'Income',
    color: 'text-green-700',
    bgColor: 'bg-green-50'
  },
  'asset': {
    label: 'Asset',
    color: 'text-blue-700',
    bgColor: 'bg-blue-50'
  },
  'liability': {
    label: 'Liability',
    color: 'text-purple-700',
    bgColor: 'bg-purple-50'
  }
}

export default function ReviewLogPage() {
  const [entries, setEntries] = useState<ReviewEntry[]>(mockEntries)
  const [isCreating, setIsCreating] = useState(false)
  const [selectedFilter, setSelectedFilter] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  
  const [newEntry, setNewEntry] = useState<Partial<ReviewEntry>>({
    title: '',
    content: '',
    tags: [],
    status: 'pending',
    type: 'expense'
  })

  const filteredEntries = entries.filter(entry => {
    const matchesType = selectedFilter === 'all' || entry.type === selectedFilter
    const matchesStatus = selectedStatus === 'all' || entry.status === selectedStatus
    return matchesType && matchesStatus
  })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  function handleSave() {
    if (newEntry.title && newEntry.content) {
      const entry: ReviewEntry = {
        id: Date.now().toString(),
        date: new Date().toISOString().split('T')[0],
        title: newEntry.title,
        content: newEntry.content,
        tags: newEntry.tags || [],
        status: newEntry.status || 'pending',
        type: newEntry.type || 'expense',
        action: statusConfig[newEntry.status || 'pending'].label
      }
      setEntries([entry, ...entries])
      setNewEntry({ title: '', content: '', tags: [], status: 'pending', type: 'expense' })
      setIsCreating(false)
    }
  }

  // Calculate stats
  const completedCount = entries.filter(e => e.status === 'completed').length
  const pendingCount = entries.filter(e => e.status === 'pending').length
  const inProgressCount = entries.filter(e => e.status === 'in-progress').length

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Financial Review Log</h1>
          <p className="text-sm text-gray-500 mt-1">Track observations, actions, and follow-ups</p>
        </div>
        <button
          onClick={() => setIsCreating(true)}
          className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Entry
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Completed Actions</p>
            <CheckCircle2 className="w-4 h-4 text-green-600" />
          </div>
          <p className="text-2xl font-semibold text-gray-900">{completedCount}</p>
          <p className="text-xs text-gray-500 mt-1">This month</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Pending Actions</p>
            <AlertCircle className="w-4 h-4 text-gray-600" />
          </div>
          <p className="text-2xl font-semibold text-gray-900">{pendingCount}</p>
          <p className="text-xs text-gray-500 mt-1">Needs attention</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">In Progress</p>
            <Clock className="w-4 h-4 text-orange-600" />
          </div>
          <p className="text-2xl font-semibold text-gray-900">{inProgressCount}</p>
          <p className="text-xs text-gray-500 mt-1">Being worked on</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Successful Implementations</p>
            <TrendingUp className="w-4 h-4 text-green-600" />
          </div>
          <p className="text-2xl font-semibold text-green-600">
            {Math.round((completedCount / entries.length) * 100)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">Completion rate</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <FilterIcon className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Filter by:</span>
            </div>
            
            {/* Type Filter */}
            <div className="flex items-center gap-2">
              {['all', 'expense', 'income', 'asset', 'liability'].map(type => (
                <button
                  key={type}
                  onClick={() => setSelectedFilter(type)}
                  className={cn(
                    "px-3 py-1 rounded-md text-sm font-medium transition-colors",
                    selectedFilter === type
                      ? "bg-gray-900 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  )}
                >
                  {type === 'all' ? 'All' : type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
            
            <div className="w-px h-6 bg-gray-300"></div>
            
            {/* Status Filter */}
            <div className="flex items-center gap-2">
              {['all', 'completed', 'in-progress', 'pending'].map(status => (
                <button
                  key={status}
                  onClick={() => setSelectedStatus(status)}
                  className={cn(
                    "px-3 py-1 rounded-md text-sm font-medium transition-colors",
                    selectedStatus === status
                      ? "bg-gray-900 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  )}
                >
                  {status === 'all' ? 'All Status' : 
                   status === 'in-progress' ? 'In Progress' :
                   status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* New Entry Form */}
      {isCreating && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">New Review Entry</h3>
            <button
              onClick={() => setIsCreating(false)}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <X className="w-4 h-4 text-gray-600" />
            </button>
          </div>
          
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Title..."
              value={newEntry.title || ''}
              onChange={(e) => setNewEntry({ ...newEntry, title: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            />
            
            <textarea
              placeholder="Description and action items..."
              value={newEntry.content || ''}
              onChange={(e) => setNewEntry({ ...newEntry, content: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent h-24 resize-none"
            />
            
            <div className="grid grid-cols-2 gap-4">
              <select
                value={newEntry.type || 'expense'}
                onChange={(e) => setNewEntry({ ...newEntry, type: e.target.value as ReviewEntry['type'] })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
                <option value="asset">Asset</option>
                <option value="liability">Liability</option>
              </select>
              
              <select
                value={newEntry.status || 'pending'}
                onChange={(e) => setNewEntry({ ...newEntry, status: e.target.value as ReviewEntry['status'] })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              >
                <option value="pending">Pending</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setIsCreating(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                Save Entry
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Entries Table */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Observations</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Date/Period</th>
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Observation</th>
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="p-4"></th>
              </tr>
            </thead>
            <tbody>
              {filteredEntries.map((entry) => {
                const statusInfo = statusConfig[entry.status]
                const typeInfo = typeConfig[entry.type]
                const StatusIcon = statusInfo.icon
                
                return (
                  <tr key={entry.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">{formatDate(entry.date)}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <p className="text-sm font-medium text-gray-900">{entry.title}</p>
                    </td>
                    <td className="p-4">
                      <span className={cn(
                        "inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium",
                        typeInfo.bgColor,
                        typeInfo.color
                      )}>
                        {typeInfo.label}
                      </span>
                    </td>
                    <td className="p-4">
                      <p className="text-sm text-gray-600 max-w-xs truncate">{entry.content}</p>
                    </td>
                    <td className="p-4">
                      <div className={cn(
                        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium",
                        statusInfo.bgColor,
                        statusInfo.color
                      )}>
                        <StatusIcon className="w-3 h-3" />
                        {statusInfo.label}
                      </div>
                    </td>
                    <td className="p-4 text-right">
                      <button className="text-gray-400 hover:text-gray-600">
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}