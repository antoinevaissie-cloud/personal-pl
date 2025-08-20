import re
from typing import List, Dict, Any, Optional, Tuple
from db.duck import get_conn

def apply_rules(transactions_raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply category rules to raw transactions, return derived transactions."""
    # Get active rules ordered by priority
    rules = get_active_rules()
    
    derived_transactions = []
    
    for raw_txn in transactions_raw:
        # Parse extra field for Boursorama categories
        import json
        extra = raw_txn.get('extra', {})
        if isinstance(extra, str):
            try:
                extra = json.loads(extra) if extra else {}
            except:
                extra = {}
        
        # Start with base transaction
        derived = {
            'raw_id': raw_txn['id'],
            'ts': raw_txn['ts'],
            'account_id': raw_txn['bank'],  # Use bank as account_id
            'account_label': raw_txn['account_label'],
            'description': raw_txn['description'],
            'merchant': raw_txn['merchant'],
            'amount': raw_txn['amount'],
            'currency': raw_txn['currency'],
            'balance': extra.get('balance'),
            'source_file': raw_txn.get('source_file', ''),
            'import_batch_id': raw_txn['import_batch_id'],
            'category': None,
            'subcategory': None,
            'is_transfer': False
        }
        
        # For Boursorama, use built-in categories
        if raw_txn['bank'] == 'Boursorama':
            # Use categoryParent as main category and category as subcategory
            category_parent = extra.get('category_parent', '').strip()
            category = extra.get('category', '').strip()
            
            if category_parent:
                derived['category'] = category_parent
                derived['subcategory'] = category if category else None
        
        # Apply rules in priority order (only if no category set yet)
        if not derived['category']:
            for rule in rules:
                if _rule_matches(rule, derived):
                    # Apply rule effects
                    if rule['set_category']:
                        derived['category'] = rule['set_category']
                    if rule['set_subcategory']:
                        derived['subcategory'] = rule['set_subcategory']
                    if rule['set_is_transfer'] is not None:
                        derived['is_transfer'] = rule['set_is_transfer']
                    
                    # Only apply first matching rule (highest priority)
                    break
        
        # Apply any existing overrides
        overrides = get_transaction_overrides(derived.get('id'))
        if overrides:
            override = overrides[-1]  # Last write wins
            if override['set_category']:
                derived['category'] = override['set_category']
            if override['set_subcategory']:
                derived['subcategory'] = override['set_subcategory']
            if override['set_is_transfer'] is not None:
                derived['is_transfer'] = override['set_is_transfer']
        
        derived_transactions.append(derived)
    
    return derived_transactions

def get_active_rules() -> List[Dict[str, Any]]:
    """Get all active rules ordered by priority."""
    conn = get_conn()
    
    result = conn.execute("""
        SELECT id, active, priority, field, operator, pattern, 
               set_category, set_subcategory, set_is_transfer
        FROM category_rules 
        WHERE active = TRUE 
        ORDER BY priority DESC
    """).fetchall()
    
    # Convert to dict format
    columns = ['id', 'active', 'priority', 'field', 'operator', 'pattern',
               'set_category', 'set_subcategory', 'set_is_transfer']
    
    rules = []
    for row in result:
        rule = dict(zip(columns, row))
        rules.append(rule)
    
    return rules

def _rule_matches(rule: Dict[str, Any], transaction: Dict[str, Any]) -> bool:
    """Check if a rule matches a transaction."""
    field_value = transaction.get(rule['field'], '')
    if not field_value:
        return False
    
    field_value = str(field_value).lower()
    pattern = rule['pattern'].lower()
    operator = rule['operator']
    
    if operator == 'contains':
        return pattern in field_value
    elif operator == 'startswith':
        return field_value.startswith(pattern)
    elif operator == 'equals':
        return field_value == pattern
    elif operator == 'regex':
        try:
            return bool(re.search(pattern, field_value, re.IGNORECASE))
        except re.error:
            return False
    
    return False

def get_transaction_overrides(txn_id: Optional[str]) -> List[Dict[str, Any]]:
    """Get overrides for a transaction."""
    if not txn_id:
        return []
    
    conn = get_conn()
    
    result = conn.execute("""
        SELECT id, txn_id, set_category, set_subcategory, set_is_transfer, note, created_at
        FROM txn_overrides 
        WHERE txn_id = ?
        ORDER BY created_at ASC
    """, [txn_id]).fetchall()
    
    columns = ['id', 'txn_id', 'set_category', 'set_subcategory', 
               'set_is_transfer', 'note', 'created_at']
    
    overrides = []
    for row in result:
        override = dict(zip(columns, row))
        overrides.append(override)
    
    return overrides

def preview_rule_matches(field: str, operator: str, pattern: str, period_month: Optional[str] = None) -> Dict[str, Any]:
    """Preview how many transactions would match a proposed rule."""
    conn = get_conn()
    
    # Build WHERE clause based on field and operator
    where_conditions = []
    params = []
    
    if period_month:
        where_conditions.append("DATE_TRUNC('month', ts) = ?")
        params.append(period_month)
    
    # Build field condition based on operator
    field_condition = ""
    if operator == 'contains':
        field_condition = f"LOWER({field}) LIKE ?"
        params.append(f"%{pattern.lower()}%")
    elif operator == 'startswith':
        field_condition = f"LOWER({field}) LIKE ?"
        params.append(f"{pattern.lower()}%")
    elif operator == 'equals':
        field_condition = f"LOWER({field}) = ?"
        params.append(pattern.lower())
    elif operator == 'regex':
        # DuckDB regex support
        field_condition = f"regexp_matches(LOWER({field}), ?)"
        params.append(pattern.lower())
    
    if field_condition:
        where_conditions.append(field_condition)
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # Count matches
    count_query = f"""
        SELECT COUNT(*) as match_count,
               COUNT(CASE WHEN category IS NULL THEN 1 END) as uncategorized_matches
        FROM transactions 
        WHERE {where_clause}
    """
    
    result = conn.execute(count_query, params).fetchone()
    
    # Get sample matches
    sample_query = f"""
        SELECT description, merchant, amount, category
        FROM transactions 
        WHERE {where_clause}
        LIMIT 5
    """
    
    samples = conn.execute(sample_query, params).fetchall()
    sample_columns = ['description', 'merchant', 'amount', 'category']
    sample_transactions = [dict(zip(sample_columns, row)) for row in samples]
    
    return {
        'match_count': result[0] if result else 0,
        'uncategorized_matches': result[1] if result else 0,
        'sample_transactions': sample_transactions
    }