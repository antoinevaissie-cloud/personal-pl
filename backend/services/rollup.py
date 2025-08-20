# backend/services/rollup.py
from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from db.duck import execute_update, execute_query, get_conn

def rebuild_rollup_monthly(month: date, user_id: str, accounts: Optional[List[str]] = None) -> Dict[str, Any]:
    # Delete existing
    params = [month]
    acc_sql = ""
    if accounts:
        acc_sql = "AND account_id IN (" + ",".join("?"*len(accounts)) + ")"
        params += accounts
    execute_update(f"""
        DELETE FROM rollup_monthly
        WHERE month = ?
          {acc_sql if accounts else ""};
    """, params)

    # Insert aggregated (exclude transfers)
    params = [month]
    if accounts:
        params += accounts
    execute_update(f"""
        INSERT INTO rollup_monthly (account_id, month, category, subcategory, income, expense, net)
        SELECT
            t.account_id,
            DATE_TRUNC('month', t.ts) AS month,
            COALESCE(t.category, 'Uncategorized') AS category,
            COALESCE(t.subcategory, '') AS subcategory,
            SUM(CASE WHEN t.amount > 0 AND NOT t.is_transfer THEN t.amount ELSE 0 END) AS income,
            SUM(CASE WHEN t.amount < 0 AND NOT t.is_transfer THEN -t.amount ELSE 0 END) AS expense,
            SUM(CASE WHEN NOT t.is_transfer THEN t.amount ELSE 0 END) AS net
        FROM transactions t
        WHERE DATE_TRUNC('month', t.ts) = ?
          {acc_sql if accounts else ""}
        GROUP BY 1,2,3,4;
    """, params)

    # Summary
    summary = get_rollup_summary(month, accounts)
    summary["rows_inserted"] = execute_query(
        "SELECT COUNT(*) FROM rollup_monthly WHERE month = ?;", [month]
    )[0][0]
    return summary

def get_uncategorized_count(month: date, accounts: Optional[List[str]] = None) -> int:
    """Get count of uncategorized transactions for a month"""
    conn = get_conn()
    params = [month]
    acc_sql = ""
    if accounts:
        acc_sql = "AND account_id IN (" + ",".join("?"*len(accounts)) + ")"
        params += accounts
    
    result = conn.execute(f"""
        SELECT COUNT(*) 
        FROM transactions 
        WHERE DATE_TRUNC('month', ts) = ?
        AND (category IS NULL OR category = 'Uncategorized')
        {acc_sql}
    """, params).fetchone()
    
    return result[0] if result else 0

def get_rollup_summary(month: date, accounts: Optional[List[str]] = None) -> Dict[str, Any]:
    acc_sql = ""
    params = [month]
    if accounts:
        acc_sql = "AND account_id IN (" + ",".join("?"*len(accounts)) + ")"
        params += accounts

    row = execute_query(f"""
        SELECT
          SUM(income) AS income,
          SUM(expense) AS expense,
          SUM(net) AS net
        FROM rollup_monthly
        WHERE month = ?
          {acc_sql if accounts else ""};
    """, params)[0]
    income, expense, net = (row[0] or 0.0, row[1] or 0.0, row[2] or 0.0)

    prev_month = (month.replace(day=1) - timedelta(days=1)).replace(day=1)
    params_prev = [prev_month]
    acc_sql_prev = ""
    if accounts:
        acc_sql_prev = "AND account_id IN (" + ",".join("?"*len(accounts)) + ")"
        params_prev += accounts
    prev = execute_query(f"""
        SELECT SUM(net) FROM rollup_monthly
        WHERE month = ?
          {acc_sql_prev if accounts else ""};
    """, params_prev)[0][0] or 0.0

    delta_mom = net - prev
    savings_rate = (net / income) if income else 0.0
    return {
        "month": month.isoformat(),
        "income": round(income, 2),
        "expense": round(expense, 2),
        "net": round(net, 2),
        "delta_mom": round(delta_mom, 2),
        "savings_rate": round(savings_rate, 4),
    }
