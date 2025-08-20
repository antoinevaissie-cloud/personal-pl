#!/usr/bin/env python3
"""Script to clear Boursorama data from the database"""

import sys
from db.duck import get_conn

def clear_boursorama_data(month=None, clear_all=False):
    conn = get_conn()
    
    print("=" * 80)
    print("CLEARING BOURSORAMA DATA")
    print("=" * 80)
    
    # First, show what we're about to delete
    print("\n1. CURRENT DATA:")
    print("-" * 40)
    
    # Count imports
    import_count = conn.execute("""
        SELECT COUNT(*), MIN(period_month), MAX(period_month)
        FROM imports 
        WHERE bank = 'Boursorama'
    """).fetchone()
    
    print(f"Boursorama imports: {import_count[0]}")
    if import_count[0] > 0:
        print(f"Period range: {import_count[1]} to {import_count[2]}")
    
    # Count transactions
    raw_count = conn.execute("""
        SELECT COUNT(*) 
        FROM transactions_raw 
        WHERE bank = 'Boursorama'
    """).fetchone()[0]
    
    derived_count = conn.execute("""
        SELECT COUNT(*) 
        FROM transactions 
        WHERE account_id = 'Boursorama'
    """).fetchone()[0]
    
    rollup_count = conn.execute("""
        SELECT COUNT(*) 
        FROM rollup_monthly 
        WHERE account_id = 'Boursorama'
    """).fetchone()[0]
    
    print(f"Raw transactions: {raw_count}")
    print(f"Processed transactions: {derived_count}")
    print(f"Rollup entries: {rollup_count}")
    
    if not clear_all and not month:
        print("\n⚠️  No action specified!")
        print("Usage:")
        print("  python clear_boursorama_data.py --all  # Clear all Boursorama data")
        print("  python clear_boursorama_data.py --month 2025-07  # Clear specific month")
        return
    
    # Confirm before deleting
    print("\n2. DELETION PLAN:")
    print("-" * 40)
    
    if clear_all:
        print("Will delete ALL Boursorama data")
    elif month:
        print(f"Will delete Boursorama data for month: {month}")
    
    response = input("\n⚠️  Are you sure? This cannot be undone! (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    # Perform deletion
    print("\n3. DELETING DATA:")
    print("-" * 40)
    
    try:
        conn.execute("BEGIN;")
        
        if clear_all:
            # Delete all Boursorama data
            
            # 1. Delete from rollup
            r1 = conn.execute("""
                DELETE FROM rollup_monthly 
                WHERE account_id = 'Boursorama'
            """).fetchone()
            print(f"Deleted rollup entries")
            
            # 2. Delete from transactions (derived)
            r2 = conn.execute("""
                DELETE FROM transactions 
                WHERE account_id = 'Boursorama'
            """).fetchone()
            print(f"Deleted processed transactions")
            
            # 3. Delete from transactions_raw
            r3 = conn.execute("""
                DELETE FROM transactions_raw 
                WHERE bank = 'Boursorama'
            """).fetchone()
            print(f"Deleted raw transactions")
            
            # 4. Delete from imports
            r4 = conn.execute("""
                DELETE FROM imports 
                WHERE bank = 'Boursorama'
            """).fetchone()
            print(f"Deleted import records")
            
        elif month:
            # Delete specific month
            from datetime import datetime
            month_date = datetime.strptime(month, "%Y-%m").date()
            month_date = month_date.replace(day=1)
            
            # Get import IDs for this month
            import_ids = conn.execute("""
                SELECT id FROM imports 
                WHERE bank = 'Boursorama' 
                AND period_month = ?
            """, [month_date]).fetchall()
            
            if import_ids:
                import_id_list = [str(row[0]) for row in import_ids]
                
                # 1. Delete from rollup
                conn.execute("""
                    DELETE FROM rollup_monthly 
                    WHERE account_id = 'Boursorama'
                    AND month = ?
                """, [month_date])
                print(f"Deleted rollup for {month}")
                
                # 2. Delete from transactions
                conn.execute("""
                    DELETE FROM transactions 
                    WHERE account_id = 'Boursorama'
                    AND DATE_TRUNC('month', ts) = ?
                """, [month_date])
                print(f"Deleted processed transactions for {month}")
                
                # 3. Delete from transactions_raw
                for import_id in import_id_list:
                    conn.execute("""
                        DELETE FROM transactions_raw 
                        WHERE import_batch_id = ?
                    """, [import_id])
                print(f"Deleted raw transactions for {month}")
                
                # 4. Delete from imports
                conn.execute("""
                    DELETE FROM imports 
                    WHERE bank = 'Boursorama' 
                    AND period_month = ?
                """, [month_date])
                print(f"Deleted import records for {month}")
            else:
                print(f"No imports found for {month}")
        
        conn.execute("COMMIT;")
        print("\n✅ Data cleared successfully!")
        
        # Show remaining data
        print("\n4. REMAINING DATA:")
        print("-" * 40)
        
        remaining_imports = conn.execute("""
            SELECT COUNT(*) FROM imports WHERE bank = 'Boursorama'
        """).fetchone()[0]
        
        remaining_raw = conn.execute("""
            SELECT COUNT(*) FROM transactions_raw WHERE bank = 'Boursorama'
        """).fetchone()[0]
        
        remaining_derived = conn.execute("""
            SELECT COUNT(*) FROM transactions WHERE account_id = 'Boursorama'
        """).fetchone()[0]
        
        print(f"Imports: {remaining_imports}")
        print(f"Raw transactions: {remaining_raw}")
        print(f"Processed transactions: {remaining_derived}")
        
    except Exception as e:
        conn.execute("ROLLBACK;")
        print(f"\n❌ Error: {e}")
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Clear Boursorama data from database')
    parser.add_argument('--all', action='store_true', help='Clear all Boursorama data')
    parser.add_argument('--month', type=str, help='Clear specific month (YYYY-MM format)')
    
    args = parser.parse_args()
    
    if args.all:
        clear_boursorama_data(clear_all=True)
    elif args.month:
        clear_boursorama_data(month=args.month)
    else:
        clear_boursorama_data()  # Show help