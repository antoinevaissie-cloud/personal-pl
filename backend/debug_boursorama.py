#!/usr/bin/env python3
"""Debug script to check Boursorama data flow"""

import sys
from datetime import date
from db.duck import get_conn
from pprint import pprint

def check_boursorama_data():
    conn = get_conn()
    
    print("=" * 80)
    print("BOURSORAMA DATA FLOW DEBUG")
    print("=" * 80)
    
    # 1. Check imports table
    print("\n1. CHECKING IMPORTS TABLE (Boursorama only):")
    print("-" * 40)
    imports = conn.execute("""
        SELECT id, bank, period_month, source_file, created_at, notes
        FROM imports 
        WHERE bank = 'Boursorama'
        ORDER BY created_at DESC
        LIMIT 5
    """).fetchall()
    
    if not imports:
        print("❌ No Boursorama imports found!")
        return
    
    for imp in imports:
        print(f"Import ID: {imp[0]}")
        print(f"  Bank: {imp[1]}, Period: {imp[2]}, File: {imp[3]}")
        print(f"  Created: {imp[4]}")
    
    latest_import_id = imports[0][0]
    latest_period = imports[0][2]
    
    # 2. Check transactions_raw
    print(f"\n2. CHECKING TRANSACTIONS_RAW (Import: {latest_import_id}):")
    print("-" * 40)
    raw_count = conn.execute("""
        SELECT COUNT(*) 
        FROM transactions_raw 
        WHERE import_batch_id = ?
    """, [latest_import_id]).fetchone()[0]
    
    print(f"Total raw transactions: {raw_count}")
    
    if raw_count > 0:
        # Sample raw transactions
        sample_raw = conn.execute("""
            SELECT ts, description, merchant, amount, currency, account_label
            FROM transactions_raw 
            WHERE import_batch_id = ?
            LIMIT 3
        """, [latest_import_id]).fetchall()
        
        print("\nSample raw transactions:")
        for row in sample_raw:
            print(f"  {row[0]} | {row[1][:50]} | Amount: {row[3]} {row[4]}")
    else:
        print("❌ No raw transactions found for this import!")
        return
    
    # 3. Check if commit was run
    print(f"\n3. CHECKING TRANSACTIONS TABLE (Normalized):")
    print("-" * 40)
    
    # Check for this specific import
    derived_count = conn.execute("""
        SELECT COUNT(*) 
        FROM transactions 
        WHERE import_batch_id = ?
    """, [latest_import_id]).fetchone()[0]
    
    print(f"Transactions from this import: {derived_count}")
    
    # Check for the period month
    period_count = conn.execute("""
        SELECT COUNT(*) 
        FROM transactions 
        WHERE DATE_TRUNC('month', ts) = ?
        AND account_id = 'Boursorama'
    """, [latest_period]).fetchone()[0]
    
    print(f"Total Boursorama transactions for {latest_period}: {period_count}")
    
    if derived_count == 0:
        print("❌ No derived transactions found!")
        print("📝 You need to run the import commit endpoint:")
        print(f"   POST /api/import/commit with period_month: '{latest_period}'")
        return
    
    # 4. Check rollup
    print(f"\n4. CHECKING ROLLUP_MONTHLY:")
    print("-" * 40)
    
    rollup_data = conn.execute("""
        SELECT account_id, category, subcategory, income, expense, net
        FROM rollup_monthly
        WHERE month = ?
        AND account_id = 'Boursorama'
        ORDER BY (income + expense) DESC
        LIMIT 5
    """, [latest_period]).fetchall()
    
    if rollup_data:
        print(f"Top categories for {latest_period}:")
        for row in rollup_data:
            print(f"  {row[1]}/{row[2]}: Income={row[3]:.2f}, Expense={row[4]:.2f}, Net={row[5]:.2f}")
    else:
        print("❌ No rollup data found!")
        print("📝 Rollup should be created when running import commit")
    
    # 5. Check for common issues
    print(f"\n5. CHECKING FOR COMMON ISSUES:")
    print("-" * 40)
    
    # Check for NULL timestamps
    null_ts = conn.execute("""
        SELECT COUNT(*) 
        FROM transactions_raw 
        WHERE import_batch_id = ? 
        AND ts IS NULL
    """, [latest_import_id]).fetchone()[0]
    
    if null_ts > 0:
        print(f"⚠️  Found {null_ts} transactions with NULL timestamps!")
    
    # Check for zero amounts
    zero_amounts = conn.execute("""
        SELECT COUNT(*) 
        FROM transactions_raw 
        WHERE import_batch_id = ? 
        AND (amount = 0 OR amount IS NULL)
    """, [latest_import_id]).fetchone()[0]
    
    if zero_amounts > 0:
        print(f"⚠️  Found {zero_amounts} transactions with zero/null amounts!")
    
    # Check date range
    date_range = conn.execute("""
        SELECT MIN(ts), MAX(ts)
        FROM transactions_raw 
        WHERE import_batch_id = ?
        AND ts IS NOT NULL
    """, [latest_import_id]).fetchone()
    
    if date_range[0]:
        print(f"Date range: {date_range[0]} to {date_range[1]}")
    
    # 6. Summary
    print(f"\n6. SUMMARY:")
    print("-" * 40)
    
    if raw_count > 0 and derived_count == 0:
        print("❌ Data uploaded but not committed!")
        print("   Action: Call POST /api/import/commit")
    elif raw_count > 0 and derived_count > 0 and not rollup_data:
        print("⚠️  Data committed but rollup might be incomplete")
        print("   Action: Check rollup rebuild process")
    elif raw_count > 0 and derived_count > 0 and rollup_data:
        print("✅ Data flow complete!")
        print(f"   {raw_count} raw → {derived_count} processed → rollup created")
    
    # Check if user_id is being used
    print(f"\n7. CHECKING USER CONTEXT:")
    print("-" * 40)
    users_check = conn.execute("""
        SELECT COUNT(DISTINCT user_id) as user_count
        FROM imports
        WHERE bank = 'Boursorama'
    """).fetchone()[0]
    
    if users_check > 1:
        print(f"⚠️  Multiple users detected ({users_check}). Make sure you're logged in!")

if __name__ == "__main__":
    check_boursorama_data()