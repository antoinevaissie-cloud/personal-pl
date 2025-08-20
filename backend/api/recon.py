from fastapi import APIRouter, HTTPException
from models.dto import (
    EOMStatementRequest, EOMStatementResponse, ReconciliationResponse
)
from db.duck import get_conn, execute_update
from datetime import date
from typing import List, Optional

router = APIRouter()

@router.post("/recon/eom", response_model=EOMStatementResponse)
async def upsert_eom_statement(request: EOMStatementRequest):
    """
    Insert or update end-of-month statement balance.
    
    Used for reconciliation against computed balances from transactions.
    """
    
    try:
        conn = get_conn()
        
        # Get computed balance for the account/month
        computed_result = conn.execute("""
            SELECT SUM(amount) as computed_balance
            FROM transactions 
            WHERE account_id = ? 
              AND DATE_TRUNC('month', ts) = ?
        """, [request.account_id, request.period_month]).fetchone()
        
        computed_balance = computed_result[0] if computed_result else 0.0
        
        # Calculate delta
        delta = computed_balance - request.balance if computed_balance is not None else None
        
        # Upsert statement balance
        execute_update("""
            INSERT INTO statements_eom (account_id, period_month, balance)
            VALUES (?, ?, ?)
            ON CONFLICT (account_id, period_month) 
            DO UPDATE SET balance = ?
        """, [request.account_id, request.period_month, request.balance, request.balance])
        
        return EOMStatementResponse(
            account_id=request.account_id,
            period_month=request.period_month,
            balance=request.balance,
            computed_balance=computed_balance,
            delta=delta
        )
        
    except Exception as e:
        print(f"EOM statement error: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating EOM statement: {str(e)}")

@router.get("/recon/eom", response_model=List[ReconciliationResponse])
async def get_reconciliation_status(
    month: Optional[str] = None,  # YYYY-MM-DD format
    account_id: Optional[str] = None
):
    """
    Get reconciliation status showing statement vs computed balances.
    
    - **month**: Optional month filter in YYYY-MM-DD format
    - **account_id**: Optional account filter
    """
    
    try:
        conn = get_conn()
        
        # Build query conditions
        conditions = []
        params = []
        
        if month:
            from datetime import datetime
            month_date = datetime.strptime(month, '%Y-%m-%d').date()
            conditions.append("s.period_month = ?")
            params.append(month_date)
        
        if account_id:
            conditions.append("s.account_id = ?")
            params.append(account_id)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Get reconciliation data
        query = f"""
        SELECT 
            s.account_id,
            s.period_month,
            s.balance as statement_balance,
            COALESCE(computed.balance, 0) as computed_balance,
            computed.transaction_count
        FROM statements_eom s
        LEFT JOIN (
            SELECT 
                account_id,
                DATE_TRUNC('month', ts) as period_month,
                SUM(amount) as balance,
                COUNT(*) as transaction_count
            FROM transactions
            GROUP BY account_id, DATE_TRUNC('month', ts)
        ) computed ON s.account_id = computed.account_id 
                   AND s.period_month = computed.period_month
        WHERE {where_clause}
        ORDER BY s.period_month DESC, s.account_id
        """
        
        result = conn.execute(query, params).fetchall()
        
        reconciliations = []
        for row in result:
            account_id, period_month, stmt_balance, comp_balance, txn_count = row
            
            delta = comp_balance - stmt_balance if stmt_balance is not None else None
            
            reconciliations.append(ReconciliationResponse(
                account_id=account_id,
                period_month=period_month,
                statement_balance=stmt_balance,
                computed_balance=comp_balance or 0.0,
                delta=delta,
                transaction_count=txn_count or 0
            ))
        
        return reconciliations
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        print(f"Reconciliation status error: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting reconciliation status: {str(e)}")