'use client'

import { useState, useEffect } from 'react'
import { 
  Search, 
  Filter, 
  Download, 
  Edit2, 
  Trash2,
  Calendar,
  TrendingUp,
  TrendingDown,
  MoreVertical,
  ChevronLeft,
  ChevronRight,
  Building2,
  Tag,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface Transaction {
  id: string
  date: string
  description: string
  amount: number
  category: string
  subcategory?: string
  bank: string
  type: 'income' | 'expense'
}

// Mock data for demonstration
const mockTransactions: Transaction[] = [
  {
    id: '1',
    date: '2025-01-15',
    description: 'Salary Payment',
    amount: 5926.24,
    category: 'Revenus du travail',
    subcategory: 'Salaire',
    bank: 'Boursorama',
    type: 'income'
  },
  {
    id: '2',
    date: '2025-01-10',
    description: 'Carrefour Market',
    amount: -127.89,
    category: 'Courses',
    subcategory: 'Supermarché',
    bank: 'Boursorama',
    type: 'expense'
  },
  {
    id: '3',
    date: '2025-01-05',
    description: 'Netflix Subscription',
    amount: -15.99,
    category: 'Abonnements',
    subcategory: 'Streaming',
    bank: 'Revolut',
    type: 'expense'
  },
  {
    id: '4',
    date: '2025-01-03',
    description: 'Restaurant Le Bistrot',
    amount: -85.50,
    category: 'Sorties',
    subcategory: 'Restaurant',
    bank: 'BNP',
    type: 'expense'
  },
  {
    id: '5',
    date: '2025-01-02',
    description: 'Freelance Project',
    amount: 1200.00,
    category: 'Revenus complémentaires',
    subcategory: 'Freelance',
    bank: 'Revolut',
    type: 'income'
  }
]

const banks = ['all', 'Boursorama', 'BNP', 'Revolut']
const types = ['all', 'income', 'expense']

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>(mockTransactions)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedBank, setSelectedBank] = useState<string>('all')
  const [selectedType, setSelectedType] = useState<string>('all')
  const [dateRange, setDateRange] = useState({ start: '', end: '' })
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  const filteredTransactions = transactions.filter(txn => {
    const matchesSearch = searchTerm === '' || 
      txn.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      txn.category.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesBank = selectedBank === 'all' || txn.bank === selectedBank
    const matchesType = selectedType === 'all' || txn.type === selectedType
    
    return matchesSearch && matchesBank && matchesType
  })

  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage)
  const paginatedTransactions = filteredTransactions.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  const getBankColor = (bank: string) => {
    switch(bank) {
      case 'Boursorama': return 'text-pink-600 bg-pink-50'
      case 'BNP': return 'text-green-600 bg-green-50'
      case 'Revolut': return 'text-blue-600 bg-blue-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Transactions</h1>
          <p className="text-sm text-gray-500 mt-1">View and manage all your transactions</p>
        </div>
        <button className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search transactions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              />
            </div>
          </div>

          {/* Bank Filter */}
          <div>
            <select
              value={selectedBank}
              onChange={(e) => setSelectedBank(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            >
              {banks.map(bank => (
                <option key={bank} value={bank}>
                  {bank === 'all' ? 'All Banks' : bank}
                </option>
              ))}
            </select>
          </div>

          {/* Type Filter */}
          <div>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            >
              {types.map(type => (
                <option key={type} value={type}>
                  {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Active Filters */}
        <div className="flex items-center gap-2 mt-4">
          <span className="text-sm text-gray-500">Active filters:</span>
          {selectedBank !== 'all' && (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-sm">
              <Building2 className="w-3 h-3" />
              {selectedBank}
              <button 
                onClick={() => setSelectedBank('all')}
                className="ml-1 hover:text-gray-900"
              >
                ×
              </button>
            </span>
          )}
          {selectedType !== 'all' && (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-sm">
              <Tag className="w-3 h-3" />
              {selectedType}
              <button 
                onClick={() => setSelectedType('all')}
                className="ml-1 hover:text-gray-900"
              >
                ×
              </button>
            </span>
          )}
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                <th className="text-left p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Bank</th>
                <th className="text-right p-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th className="p-4"></th>
              </tr>
            </thead>
            <tbody>
              {paginatedTransactions.map((txn) => (
                <tr key={txn.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">{formatDate(txn.date)}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{txn.description}</p>
                      {txn.subcategory && (
                        <p className="text-xs text-gray-500 mt-0.5">{txn.subcategory}</p>
                      )}
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={cn(
                      "inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium",
                      txn.type === 'income' ? "badge-income" : 
                      txn.category.toLowerCase().includes('tax') ? "badge-tax" : "badge-expense"
                    )}>
                      {txn.category}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={cn(
                      "inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium",
                      getBankColor(txn.bank)
                    )}>
                      {txn.bank}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <div className={cn(
                      "flex items-center justify-end gap-1 text-sm font-medium",
                      txn.type === 'income' ? "text-green-600" : "text-gray-900"
                    )}>
                      {txn.type === 'income' ? (
                        <ArrowUpRight className="w-3 h-3" />
                      ) : (
                        <ArrowDownRight className="w-3 h-3 text-red-600" />
                      )}
                      €{Math.abs(txn.amount).toLocaleString('en-US', { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                      })}
                    </div>
                  </td>
                  <td className="p-4">
                    <button className="p-1 hover:bg-gray-100 rounded">
                      <MoreVertical className="w-4 h-4 text-gray-400" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-700">
              Showing {((currentPage - 1) * itemsPerPage) + 1} to{' '}
              {Math.min(currentPage * itemsPerPage, filteredTransactions.length)} of{' '}
              {filteredTransactions.length} transactions
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className={cn(
                  "p-2 rounded-lg transition-colors",
                  currentPage === 1 
                    ? "text-gray-300 cursor-not-allowed" 
                    : "text-gray-600 hover:bg-gray-100"
                )}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNum = i + 1
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={cn(
                        "px-3 py-1 rounded-md text-sm font-medium transition-colors",
                        currentPage === pageNum
                          ? "bg-gray-900 text-white"
                          : "text-gray-600 hover:bg-gray-100"
                      )}
                    >
                      {pageNum}
                    </button>
                  )
                })}
              </div>

              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className={cn(
                  "p-2 rounded-lg transition-colors",
                  currentPage === totalPages 
                    ? "text-gray-300 cursor-not-allowed" 
                    : "text-gray-600 hover:bg-gray-100"
                )}
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-6 mt-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Total Income</p>
            <TrendingUp className="w-4 h-4 text-green-600" />
          </div>
          <p className="text-2xl font-semibold text-green-600">
            €{transactions
              .filter(t => t.type === 'income')
              .reduce((sum, t) => sum + t.amount, 0)
              .toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Total Expenses</p>
            <TrendingDown className="w-4 h-4 text-red-600" />
          </div>
          <p className="text-2xl font-semibold text-red-600">
            €{Math.abs(transactions
              .filter(t => t.type === 'expense')
              .reduce((sum, t) => sum + t.amount, 0))
              .toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Net Balance</p>
            <div className="w-4 h-4 rounded-full bg-gray-900"></div>
          </div>
          <p className="text-2xl font-semibold text-gray-900">
            €{transactions
              .reduce((sum, t) => sum + t.amount, 0)
              .toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
      </div>
    </div>
  )
}