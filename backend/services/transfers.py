from typing import List, Dict, Any, Optional
from datetime import date, datetime
from db.duck import get_conn, execute_update
import uuid

def propose_transfers(month: date, accounts: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Propose transfer candidates using heuristic matching."""
    conn = get_conn()
    
    # Build account filter
    account_filter = ""
    params = [month]
    
    if accounts:
        placeholders = ','.join('?' * len(accounts))
        account_filter = f"AND t.account_id IN ({placeholders})"
        params.extend(accounts)
    
    # SQL for transfer detection heuristic
    query = f"""
    WITH base AS (
      SELECT id, ts::DATE AS d, account_id, amount, ABS(amount) AS a, description, merchant
      FROM transactions
      WHERE DATE_TRUNC('month', ts) = ?
        AND is_transfer = FALSE  -- Don't match already marked transfers
        {account_filter}
    ),
    pairs AS (
      SELECT 
        b1.id AS id1, 
        b2.id AS id2, 
        b1.d, 
        b1.account_id AS from_acct, 
        b2.account_id AS to_acct,
        b1.amount AS amt1, 
        b2.amount AS amt2,
        b1.description AS desc1,
        b2.description AS desc2,
        ABS(DATEDIFF('day', b1.d, b2.d)) AS date_diff
      FROM base b1
      JOIN base b2
        ON b1.a = b2.a  -- Same absolute amount
       AND b1.amount * b2.amount < 0  -- Opposite signs
       AND b1.account_id <> b2.account_id  -- Different accounts
       AND ABS(DATEDIFF('day', b1.d, b2.d)) <= 1  -- Within 1 day
       AND b1.id < b2.id  -- Avoid duplicates
    )
    SELECT * FROM pairs
    ORDER BY date_diff ASC, ABS(amt1) DESC
    LIMIT 100
    """
    
    result = conn.execute(query, params).fetchall()
    
    columns = ['id1', 'id2', 'd', 'from_acct', 'to_acct', 'amt1', 'amt2', 
               'desc1', 'desc2', 'date_diff']
    
    proposals = []
    for row in result:
        proposal = dict(zip(columns, row))
        
        # Calculate confidence score
        confidence = calculate_transfer_confidence(proposal)
        proposal['confidence'] = confidence
        
        # Format for response
        proposals.append({
            'id': str(uuid.uuid4()),  # Temporary ID for proposal
            'transaction_ids': [proposal['id1'], proposal['id2']],
            'date': proposal['d'],
            'from_account': proposal['from_acct'],
            'to_account': proposal['to_acct'],
            'amount': abs(proposal['amt1']),
            'descriptions': [proposal['desc1'], proposal['desc2']],
            'date_difference_days': proposal['date_diff'],
            'confidence': confidence
        })
    
    return proposals

def calculate_transfer_confidence(proposal: Dict[str, Any]) -> float:
    """Calculate confidence score for transfer proposal (0-1)."""
    confidence = 0.5  # Base score
    
    # Same day bonus
    if proposal['date_diff'] == 0:
        confidence += 0.3
    
    # Description similarity bonus
    desc1 = proposal['desc1'].lower()
    desc2 = proposal['desc2'].lower()
    
    # Common transfer keywords
    transfer_keywords = ['virement', 'transfer', 'vir ', 'transfert']
    if any(keyword in desc1 or keyword in desc2 for keyword in transfer_keywords):
        confidence += 0.2
    
    # Exact amount match (already guaranteed, but reinforces confidence)
    confidence += 0.1
    
    return min(confidence, 1.0)

def confirm_transfers(proposal_ids: List[str], transaction_pairs: List[List[str]]) -> Dict[str, Any]:
    """Confirm transfer proposals by marking transactions as transfers."""
    conn = get_conn()
    confirmed_count = 0
    
    try:
        for pair in transaction_pairs:
            if len(pair) != 2:
                continue
            
            txn_id1, txn_id2 = pair
            
            # Create overrides to mark both as transfers
            for txn_id in [txn_id1, txn_id2]:
                override_id = str(uuid.uuid4())
                execute_update("""
                    INSERT INTO txn_overrides (id, txn_id, set_is_transfer, note)
                    VALUES (?, ?, TRUE, 'Confirmed as transfer')
                """, {
                    'id': override_id,
                    'txn_id': txn_id
                })
            
            # Update the derived transactions table
            for txn_id in [txn_id1, txn_id2]:
                execute_update("""
                    UPDATE transactions 
                    SET is_transfer = TRUE 
                    WHERE id = ?
                """, {'id': txn_id})
            
            confirmed_count += 2
        
        return {
            'confirmed_transactions': confirmed_count,
            'confirmed_pairs': len(transaction_pairs)
        }
        
    except Exception as e:
        raise ValueError(f"Error confirming transfers: {e}")

def get_potential_transfers(transaction_id: str) -> List[Dict[str, Any]]:
    """Find potential transfer matches for a specific transaction."""
    conn = get_conn()
    
    # Get the target transaction
    txn = conn.execute("""
        SELECT id, ts::DATE as d, account_id, amount, ABS(amount) as a, description
        FROM transactions 
        WHERE id = ? AND is_transfer = FALSE
    """, [transaction_id]).fetchone()
    
    if not txn:
        return []
    
    # Find potential matches
    matches = conn.execute("""
        SELECT id, ts::DATE as d, account_id, amount, description,
               ABS(DATEDIFF('day', ts::DATE, ?)) as date_diff
        FROM transactions
        WHERE ABS(amount) = ?  -- Same absolute amount
          AND amount * ? < 0   -- Opposite sign  
          AND account_id <> ?  -- Different account
          AND is_transfer = FALSE
          AND ABS(DATEDIFF('day', ts::DATE, ?)) <= 2  -- Within 2 days
        ORDER BY date_diff ASC, ABS(amount) DESC
        LIMIT 10
    """, [txn[1], txn[4], txn[3], txn[2], txn[1]]).fetchall()
    
    columns = ['id', 'date', 'account_id', 'amount', 'description', 'date_diff']
    potential_matches = []
    
    for match in matches:
        match_dict = dict(zip(columns, match))
        match_dict['confidence'] = calculate_simple_confidence(
            txn[5], match_dict['description'], match_dict['date_diff']
        )
        potential_matches.append(match_dict)
    
    return potential_matches

def calculate_simple_confidence(desc1: str, desc2: str, date_diff: int) -> float:
    """Simple confidence calculation for individual matches."""
    confidence = 0.3
    
    if date_diff == 0:
        confidence += 0.4
    elif date_diff == 1:
        confidence += 0.2
    
    # Description similarity
    desc1_lower = desc1.lower()
    desc2_lower = desc2.lower()
    
    transfer_keywords = ['virement', 'transfer', 'vir ', 'transfert']
    if any(keyword in desc1_lower or keyword in desc2_lower for keyword in transfer_keywords):
        confidence += 0.3
    
    return min(confidence, 1.0)