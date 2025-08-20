from fastapi import APIRouter, HTTPException, Depends
from models.dto import ImportCommitRequest, ImportCommitResponse
from services.rules_engine import apply_rules
from services.rollup import rebuild_rollup_monthly, get_uncategorized_count
from db.duck import get_conn, execute_update
from auth import get_current_user
import uuid
from typing import List, Dict, Any

router = APIRouter()

@router.post("/api/import/commit", response_model=ImportCommitResponse)
async def commit_import(
    request: ImportCommitRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Commit imported raw data by applying rules and building derived transactions.
    
    This endpoint:
    1. Gets raw transactions for the period
    2. Applies category rules in priority order
    3. Builds derived transactions table
    4. Rebuilds materialized rollups
    """
    
    try:
        conn = get_conn()
        
        # Convert period_month string to date
        from datetime import datetime
        if isinstance(request.period_month, str):
            # Handle both "2025-07" and "2025-07-01" formats
            if len(request.period_month) == 7:  # YYYY-MM format
                period_month = datetime.strptime(request.period_month + "-01", "%Y-%m-%d").date()
            else:
                period_month = datetime.strptime(request.period_month, "%Y-%m-%d").date()
        else:
            period_month = request.period_month
        
        # Get accounts to process
        if request.accounts:
            accounts_filter = f"AND bank IN ({','.join(['?' for _ in request.accounts])})"
            accounts_params = request.accounts
        else:
            # Get all banks for the period
            accounts_result = conn.execute("""
                SELECT DISTINCT bank 
                FROM imports 
                WHERE period_month = ?
            """, [period_month]).fetchall()
            
            accounts_params = [row[0] for row in accounts_result]
            accounts_filter = f"AND bank IN ({','.join(['?' for _ in accounts_params])})" if accounts_params else ""
        
        # Get raw transactions for the period
        raw_query = f"""
        SELECT id, import_batch_id, bank, ts, description, merchant, 
               amount_raw, amount, currency, account_label, extra
        FROM transactions_raw
        WHERE import_batch_id IN (
            SELECT id FROM imports 
            WHERE period_month = ?
        ) {accounts_filter}
        """
        
        params = [period_month] + accounts_params
        raw_result = conn.execute(raw_query, params).fetchall()
        
        if not raw_result:
            raise HTTPException(status_code=404, detail=f"No raw transactions found for period {period_month}")
        
        # Convert to dict format for rules engine
        raw_transactions = []
        columns = ['id', 'import_batch_id', 'bank', 'ts', 'description', 'merchant',
                  'amount_raw', 'amount', 'currency', 'account_label', 'extra']
        
        for row in raw_result:
            raw_txn = dict(zip(columns, row))
            raw_transactions.append(raw_txn)
        
        # Apply rules to generate derived transactions
        derived_transactions = apply_rules(raw_transactions)
        
        # Clear existing derived transactions for this period
        execute_update("""
            DELETE FROM transactions 
            WHERE import_batch_id IN (
                SELECT id FROM imports WHERE period_month = ?
            )
        """, [period_month])
        
        # Insert derived transactions
        transactions_inserted = 0
        for derived in derived_transactions:
            txn_id = str(uuid.uuid4())
            
            execute_update("""
                INSERT INTO transactions (
                    id, raw_id, ts, account_id, account_label, description, merchant,
                    category, subcategory, amount, currency, balance, is_transfer,
                    source_file, import_batch_id, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                txn_id,
                derived['raw_id'],
                derived['ts'],
                derived['account_id'],
                derived['account_label'],
                derived['description'],
                derived['merchant'],
                derived['category'],
                derived['subcategory'],
                derived['amount'],
                derived['currency'],
                derived.get('balance'),
                derived['is_transfer'],
                derived['source_file'],
                derived['import_batch_id'],
                current_user['id']
            ])
            
            transactions_inserted += 1
        
        # Rebuild rollups for the month
        rollup_result = rebuild_rollup_monthly(period_month, current_user['id'], accounts_params)
        
        # Count rules applied (approximate based on categorized transactions)
        rules_applied = sum(1 for t in derived_transactions if t['category'])
        
        # Get uncategorized count
        uncategorized = get_uncategorized_count(period_month, accounts_params)
        
        return ImportCommitResponse(
            period_month=period_month,
            accounts_processed=accounts_params,
            transactions_derived=transactions_inserted,
            rules_applied=rules_applied,
            rollup_updated=True,
            uncategorized_count=uncategorized
        )
        
    except Exception as e:
        print(f"Import commit error: {e}")
        raise HTTPException(status_code=500, detail=f"Error committing import: {str(e)}")