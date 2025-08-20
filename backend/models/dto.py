from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

# Enums
class BankType(str, Enum):
    BNP = "BNP"
    BOURSORAMA = "Boursorama" 
    REVOLUT = "Revolut"

class RuleOperator(str, Enum):
    CONTAINS = "contains"
    STARTSWITH = "startswith"
    EQUALS = "equals"
    REGEX = "regex"

class RuleField(str, Enum):
    MERCHANT = "merchant"
    DESCRIPTION = "description"

class CurrencyView(str, Enum):
    NATIVE = "native"
    EUR = "eur"

# Upload DTOs
class UploadResponse(BaseModel):
    import_batch_id: str
    bank: BankType
    period_month: date
    duplicate_detected: bool
    file_sha256: str
    raw_rows_imported: int
    source_file: str

# Import Commit DTOs  
class ImportCommitRequest(BaseModel):
    period_month: str  # Accept string and convert to date in the endpoint
    accounts: Optional[List[str]] = None

class ImportCommitResponse(BaseModel):
    period_month: date
    accounts_processed: List[str]
    transactions_derived: int
    rules_applied: int
    rollup_updated: bool
    uncategorized_count: int

# P&L DTOs
class PLSummaryRequest(BaseModel):
    month: date
    accounts: Optional[List[str]] = None
    exclude_transfers: bool = True
    currency_view: CurrencyView = CurrencyView.NATIVE

class PLSummary(BaseModel):
    income: float
    expenses: float
    net: float
    savings_rate: float
    delta_income: float
    delta_expenses: float
    delta_net: float

class CategoryRow(BaseModel):
    category: str
    income: float
    expense: float
    net: float
    subcategory_count: int
    income_pct: float
    expense_pct: float

class PLSummaryResponse(BaseModel):
    summary: PLSummary
    categories: List[CategoryRow]
    uncategorized_count: int
    period: Dict[str, Any]

# Transaction DTOs
class TransactionListRequest(BaseModel):
    month: Optional[date] = None
    accounts: Optional[List[str]] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    merchant: Optional[str] = None
    uncategorized_only: bool = False
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)

class TransactionRow(BaseModel):
    id: str
    ts: datetime
    account_id: str
    account_label: Optional[str]
    description: str
    merchant: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    amount: float
    currency: str
    is_transfer: bool
    balance: Optional[float]

class TransactionListResponse(BaseModel):
    transactions: List[TransactionRow]
    total_count: int
    has_more: bool
    offset: int
    limit: int

class TransactionUpdateRequest(BaseModel):
    category: Optional[str] = None
    subcategory: Optional[str] = None
    is_transfer: Optional[bool] = None
    note: Optional[str] = None

class TransactionUpdateResponse(BaseModel):
    id: str
    updated_fields: Dict[str, Any]
    rollup_updated: bool

# Rules DTOs
class RuleCreateRequest(BaseModel):
    field: RuleField
    operator: RuleOperator
    pattern: str
    set_category: Optional[str] = None
    set_subcategory: Optional[str] = None
    set_is_transfer: Optional[bool] = None
    priority: int = Field(default=100, ge=1, le=1000)
    active: bool = True

class RuleUpdateRequest(BaseModel):
    field: Optional[RuleField] = None
    operator: Optional[RuleOperator] = None
    pattern: Optional[str] = None
    set_category: Optional[str] = None
    set_subcategory: Optional[str] = None
    set_is_transfer: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1, le=1000)
    active: Optional[bool] = None

class RuleResponse(BaseModel):
    id: str
    field: RuleField
    operator: RuleOperator
    pattern: str
    set_category: Optional[str]
    set_subcategory: Optional[str]
    set_is_transfer: Optional[bool]
    priority: int
    active: bool

class RulePreviewRequest(BaseModel):
    field: RuleField
    operator: RuleOperator
    pattern: str
    period_month: Optional[date] = None

class RulePreviewResponse(BaseModel):
    match_count: int
    uncategorized_matches: int
    sample_transactions: List[Dict[str, Any]]

# Transfer DTOs
class TransferProposal(BaseModel):
    id: str
    transaction_ids: List[str]
    date: date
    from_account: str
    to_account: str
    amount: float
    descriptions: List[str]
    date_difference_days: int
    confidence: float

class TransferProposeRequest(BaseModel):
    month: date
    accounts: Optional[List[str]] = None

class TransferProposeResponse(BaseModel):
    proposals: List[TransferProposal]
    total_count: int

class TransferConfirmRequest(BaseModel):
    transaction_pairs: List[List[str]]

class TransferConfirmResponse(BaseModel):
    confirmed_transactions: int
    confirmed_pairs: int

# Reconciliation DTOs
class EOMAchievementRequest(BaseModel):
    account_id: str
    period_month: date
    balance: float

class EOMAchievementResponse(BaseModel):
    account_id: str
    period_month: date
    balance: float
    computed_balance: Optional[float]
    delta: Optional[float]

class ReconciliationResponse(BaseModel):
    account_id: str
    period_month: date
    statement_balance: Optional[float]
    computed_balance: float
    delta: Optional[float]
    transaction_count: int

# Journal DTOs
class JournalCreateRequest(BaseModel):
    period_start: date
    period_end: date
    observations_md: str = ""
    decisions_md: str = ""

class JournalUpdateRequest(BaseModel):
    observations_md: Optional[str] = None
    decisions_md: Optional[str] = None

class JournalResponse(BaseModel):
    id: str
    period_start: date
    period_end: date
    observations_md: str
    decisions_md: str
    created_at: datetime
    updated_at: datetime

class JournalListRequest(BaseModel):
    month: Optional[str] = None  # YYYY-MM format

# Error DTOs
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None