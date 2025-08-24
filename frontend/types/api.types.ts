// Authentication types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

// Upload types
export type BankType = 'BNP' | 'Boursorama' | 'Revolut';

export interface UploadResponse {
  import_batch_id: string;
  bank: BankType;
  period_month: string;
  duplicate_detected: boolean;
  file_sha256: string;
  raw_rows_imported: number;
  source_file: string;
}

// Import commit types
export interface ImportCommitRequest {
  period_month: string;
  accounts?: string[];
}

export interface ImportCommitResponse {
  period_month: string;
  accounts_processed: string[];
  transactions_derived: number;
  rules_applied: number;
  rollup_updated: boolean;
  uncategorized_count: number;
}

// P&L types
export interface PLSummaryRequest {
  month: string;
  accounts?: string[];
  exclude_transfers?: boolean;
  currency_view?: 'native' | 'eur';
}

export interface PLSummary {
  month: string;
  income: number;
  expense: number;
  net: number;
  delta_mom: number;
  savings_rate: number;
}

export interface SubcategoryRow {
  name: string;
  net: number;
}

export interface CategoryRow {
  category: string;
  net: number;
  subs: SubcategoryRow[];
}

export interface PLSummaryResponse {
  summary: PLSummary;
  rows: CategoryRow[];
  filters: {
    month: string;
    accounts: string[];
  };
}

// Transaction types
export interface TransactionListRequest {
  month?: string;
  accounts?: string[];
  category?: string;
  subcategory?: string;
  merchant?: string;
  uncategorized_only?: boolean;
  limit?: number;
  offset?: number;
}

export interface Transaction {
  id: string;
  ts: string;
  account_id: string;
  account_label?: string;
  description: string;
  merchant?: string;
  category?: string;
  subcategory?: string;
  amount: number;
  amount_eur?: number;
  currency: string;
  is_transfer: boolean;
}

export interface TransactionListResponse {
  transactions: Transaction[];
  total: number;
  page: number;
  limit: number;
}

// Review types
export interface ReviewNote {
  period_month: string;
  note: string;
  status: 'pending' | 'reviewed';
  created_at: string;
  updated_at: string;
}