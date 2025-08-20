from fastapi import APIRouter, HTTPException, Path
from models.dto import (
    TransactionListRequest, TransactionListResponse, TransactionRow,
    TransactionUpdateRequest, TransactionUpdateResponse
)
from db.duck import get_conn, execute_update
from services.rollup import rebuild_rollup_monthly
import uuid
from datetime import date
from typing import Optional

router = APIRouter()

@router.post("/tx", response_model=TransactionListResponse)
async def get_transactions(request: TransactionListRequest):
    """
    Get filtered list of transactions with pagination.
    
    Supports filtering by:
    - Month, accounts, category, subcategory, merchant
    - Uncategorized only flag
    - Pagination with limit/offset
    """
    
    try:
        conn = get_conn()
        
        # Build WHERE conditions
        where_conditions = []
        params = []
        
        if request.month:
            where_conditions.append("DATE_TRUNC('month', ts) = ?")
            params.append(request.month)
        
        if request.accounts:
            placeholders = ','.join('?' * len(request.accounts))
            where_conditions.append(f"account_id IN ({placeholders})")
            params.extend(request.accounts)
        
        if request.category:
            where_conditions.append("category = ?")
            params.append(request.category)
        
        if request.subcategory:
            where_conditions.append("subcategory = ?")
            params.append(request.subcategory)
        
        if request.merchant:
            where_conditions.append("LOWER(merchant) LIKE ?")
            params.append(f"%{request.merchant.lower()}%")
        
        if request.uncategorized_only:
            where_conditions.append("(category IS NULL OR category = '')")
            where_conditions.append("NOT is_transfer")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM transactions WHERE {where_clause}"
        total_count = conn.execute(count_query, params).fetchone()[0]
        
        # Get transactions with pagination
        data_query = f"""
        SELECT id, ts, account_id, account_label, description, merchant,
               category, subcategory, amount, currency, is_transfer, balance
        FROM transactions 
        WHERE {where_clause}
        ORDER BY ts DESC
        LIMIT ? OFFSET ?
        """
        
        params.extend([request.limit, request.offset])
        result = conn.execute(data_query, params).fetchall()
        
        # Convert to response format
        columns = ['id', 'ts', 'account_id', 'account_label', 'description', 'merchant',
                  'category', 'subcategory', 'amount', 'currency', 'is_transfer', 'balance']
        
        transactions = []
        for row in result:
            txn_data = dict(zip(columns, row))
            transactions.append(TransactionRow(**txn_data))
        
        has_more = (request.offset + len(transactions)) < total_count
        
        return TransactionListResponse(
            transactions=transactions,
            total_count=total_count,
            has_more=has_more,
            offset=request.offset,
            limit=request.limit
        )
        
    except Exception as e:
        print(f"Transaction list error: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting transactions: {str(e)}")

@router.patch("/tx/{transaction_id}", response_model=TransactionUpdateResponse)
async def update_transaction(
    transaction_id: str = Path(...),
    request: TransactionUpdateRequest = ...
):
    """
    Update transaction category/subcategory/transfer status via overrides.
    
    Creates an override record and updates the derived transaction.
    Rebuilds rollup for affected month.
    """
    
    try:
        conn = get_conn()
        
        # Verify transaction exists
        txn_result = conn.execute("""
            SELECT ts, account_id FROM transactions WHERE id = ?
        """, [transaction_id]).fetchone()
        
        if not txn_result:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        txn_ts, account_id = txn_result
        month = date(txn_ts.year, txn_ts.month, 1)
        
        # Create override record
        override_id = str(uuid.uuid4())
        execute_update("""
            INSERT INTO txn_overrides (id, txn_id, set_category, set_subcategory, set_is_transfer, note)
            VALUES (?, ?, ?, ?, ?, ?)
        """, {
            'id': override_id,
            'txn_id': transaction_id,
            'set_category': request.category,
            'set_subcategory': request.subcategory,
            'set_is_transfer': request.is_transfer,
            'note': request.note
        })
        
        # Update derived transaction
        update_fields = {}
        if request.category is not None:
            update_fields['category'] = request.category
        if request.subcategory is not None:
            update_fields['subcategory'] = request.subcategory
        if request.is_transfer is not None:
            update_fields['is_transfer'] = request.is_transfer
        
        if update_fields:
            # Build dynamic UPDATE query
            set_clauses = []
            update_params = []
            
            for field, value in update_fields.items():
                set_clauses.append(f"{field} = ?")
                update_params.append(value)
            
            update_params.append(transaction_id)
            
            update_query = f"""
                UPDATE transactions 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """
            
            execute_update(update_query, update_params)
        
        # Rebuild rollup for affected month
        rebuild_rollup_monthly(month, [account_id])
        
        return TransactionUpdateResponse(
            id=transaction_id,
            updated_fields=update_fields,
            rollup_updated=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Transaction update error: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating transaction: {str(e)}")