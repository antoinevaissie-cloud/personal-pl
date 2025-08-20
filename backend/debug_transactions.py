#!/usr/bin/env python
"""Debug script to check transaction dates"""
from db.duck import get_conn

conn = get_conn()

print("=== Checking Raw Transactions ===")
# Check what's in transactions_raw
raw_data = conn.execute("""
    SELECT 
        DATE_TRUNC('month', ts) as month,
        COUNT(*) as count,
        MIN(ts) as first_date,
        MAX(ts) as last_date,
        i.bank,
        i.user_id
    FROM transactions_raw r
    JOIN imports i ON i.id = r.import_batch_id
    GROUP BY DATE_TRUNC('month', ts), i.bank, i.user_id
    ORDER BY month DESC
""").fetchall()

if raw_data:
    print(f"Found {len(raw_data)} month/bank combinations:")
    for row in raw_data:
        print(f"  Month: {row[0]}, Count: {row[1]}, First: {row[2]}, Last: {row[3]}, Bank: {row[4]}, User: {row[5]}")
else:
    print("No raw transactions found")

print("\n=== Checking Imports ===")
imports = conn.execute("""
    SELECT 
        id,
        bank,
        period_month,
        created_at,
        u.username
    FROM imports i
    LEFT JOIN users u ON u.id = i.user_id
    ORDER BY created_at DESC
    LIMIT 10
""").fetchall()

if imports:
    print(f"Recent imports:")
    for row in imports:
        print(f"  ID: {row[0][:8]}..., Bank: {row[1]}, Period: {row[2]}, Created: {row[3]}, User: {row[4]}")
        
        # Check transactions for this import
        tx_count = conn.execute("""
            SELECT COUNT(*), MIN(ts), MAX(ts)
            FROM transactions_raw
            WHERE import_batch_id = ?
        """, [row[0]]).fetchone()
        print(f"    -> {tx_count[0]} transactions, dates: {tx_count[1]} to {tx_count[2]}")
else:
    print("No imports found")

print("\n=== Checking Processed Transactions ===")
tx_data = conn.execute("""
    SELECT 
        DATE_TRUNC('month', ts) as month,
        COUNT(*) as count,
        account_id
    FROM transactions
    GROUP BY DATE_TRUNC('month', ts), account_id
    ORDER BY month DESC
""").fetchall()

if tx_data:
    print(f"Found {len(tx_data)} month/account combinations:")
    for row in tx_data:
        print(f"  Month: {row[0]}, Count: {row[1]}, Account: {row[2]}")
else:
    print("No processed transactions found")