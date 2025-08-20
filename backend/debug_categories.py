#!/usr/bin/env python3
"""Debug script to trace where categories are being lost"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.duck import get_conn
from services.rules_engine import apply_rules

def debug_category_flow():
    conn = get_conn()
    
    print("=" * 80)
    print("DEBUGGING BOURSORAMA CATEGORY FLOW")
    print("=" * 80)
    
    # Step 1: Check raw data
    print("\n1. CHECKING RAW DATA (transactions_raw):")
    print("-" * 40)
    
    raw_data = conn.execute("""
        SELECT id, bank, description, amount, extra
        FROM transactions_raw 
        WHERE bank = 'Boursorama'
        LIMIT 5
    """).fetchall()
    
    if not raw_data:
        print("❌ No Boursorama data in transactions_raw!")
        return
    
    print(f"Found {len(raw_data)} sample transactions")
    for row in raw_data:
        extra = json.loads(row[4]) if row[4] else {}
        print(f"\nTransaction: {row[2][:50]}")
        print(f"  Amount: {row[3]}")
        print(f"  category_parent: {extra.get('category_parent', 'MISSING')}")
        print(f"  category: {extra.get('category', 'MISSING')}")
    
    # Step 2: Test rules engine directly
    print("\n2. TESTING RULES ENGINE:")
    print("-" * 40)
    
    # Get raw transactions for testing
    test_raw = conn.execute("""
        SELECT id, import_batch_id, bank, ts, description, merchant, 
               amount_raw, amount, currency, account_label, extra
        FROM transactions_raw
        WHERE bank = 'Boursorama'
        LIMIT 3
    """).fetchall()
    
    columns = ['id', 'import_batch_id', 'bank', 'ts', 'description', 'merchant',
              'amount_raw', 'amount', 'currency', 'account_label', 'extra']
    
    raw_transactions = []
    for row in test_raw:
        raw_txn = dict(zip(columns, row))
        raw_transactions.append(raw_txn)
        
    # Apply rules
    derived = apply_rules(raw_transactions)
    
    print(f"Applied rules to {len(raw_transactions)} transactions")
    for i, d in enumerate(derived):
        print(f"\nDerived transaction {i+1}:")
        print(f"  Description: {d['description'][:50]}")
        print(f"  Category: {d.get('category', 'NONE')}")
        print(f"  Subcategory: {d.get('subcategory', 'NONE')}")
    
    # Step 3: Check what's in transactions table
    print("\n3. CHECKING PROCESSED DATA (transactions):")
    print("-" * 40)
    
    processed = conn.execute("""
        SELECT id, description, category, subcategory, amount
        FROM transactions 
        WHERE account_id = 'Boursorama'
        LIMIT 5
    """).fetchall()
    
    if not processed:
        print("❌ No Boursorama data in transactions table!")
        print("   You need to run import commit")
    else:
        print(f"Found {len(processed)} sample transactions")
        for row in processed:
            print(f"\nTransaction: {row[1][:50]}")
            print(f"  Category: {row[2] or 'NULL'}")
            print(f"  Subcategory: {row[3] or 'NULL'}")
            print(f"  Amount: {row[4]}")
    
    # Step 4: Check rollup
    print("\n4. CHECKING ROLLUP:")
    print("-" * 40)
    
    rollup = conn.execute("""
        SELECT category, subcategory, income, expense, net
        FROM rollup_monthly
        WHERE account_id = 'Boursorama'
        ORDER BY (income + expense) DESC
        LIMIT 5
    """).fetchall()
    
    if not rollup:
        print("❌ No rollup data!")
    else:
        for row in rollup:
            print(f"Category: {row[0]}, Net: {row[4]}")

if __name__ == "__main__":
    debug_category_flow()