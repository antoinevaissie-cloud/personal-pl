// frontend/lib/api.ts
import AuthService from './auth'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export const api = {
  baseURL: API_BASE,
}

// Helper to add auth headers
function getAuthHeaders(): HeadersInit {
  const token = AuthService.getToken()
  return token
    ? {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      }
    : {
        'Content-Type': 'application/json',
      }
}

// Helper to handle API errors
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    if (response.status === 401) {
      AuthService.removeToken()
      window.location.href = '/login'
    }
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || error.error || 'Request failed')
  }
  return response.json()
}

export async function uploadBankCSV(params: {
  bank: "BNP" | "Boursorama" | "Revolut"
  period_month: string // YYYY-MM
  file: File
}) {
  const token = AuthService.getToken()
  if (!token) {
    throw new Error('Authentication required')
  }

  const fd = new FormData()
  fd.append("bank", params.bank)
  fd.append("period_month", params.period_month)
  fd.append("file", params.file)
  
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: fd,
  })
  
  return handleResponse(res)
}

export async function importCommit(period_month: string) {
  const res = await fetch(`${API_BASE}/api/import/commit`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ period_month }),
  })
  
  return handleResponse(res)
}

export type PLSummaryResponse = {
  summary: {
    month: string
    income: number
    expense: number
    net: number
    delta_mom: number
    savings_rate: number
  }
  rows: {
    category: string
    net: number
    subs: { name: string; net: number }[]
  }[]
  filters: { month: string; accounts: string[] }
}

export async function getPLSummary(input: { month: string; accounts?: string[] }) {
  const res = await fetch(`${API_BASE}/api/pl/summary`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ month: input.month, accounts: input.accounts ?? [] }),
  })
  
  return handleResponse<PLSummaryResponse>(res)
}