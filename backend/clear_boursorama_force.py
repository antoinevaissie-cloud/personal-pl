#!/usr/bin/env python3
"""Force clear Boursorama data without confirmation"""

from db.duck import get_conn

def force_clear_boursorama():
    conn = get_conn()
    
    print("Clearing all Boursorama data...")
    
    try:
        conn.execute("BEGIN;")
        
        # Get all Boursorama import IDs first
        import_ids = conn.execute("""
            SELECT id FROM imports WHERE bank = 'Boursorama'
        """).fetchall()
        
        import_id_list = [str(row[0]) for row in import_ids]
        
        if import_id_list:
            # Delete in correct order to respect foreign keys
            
            # 1. Delete from rollup
            deleted = conn.execute("DELETE FROM rollup_monthly WHERE account_id = 'Boursorama'").fetchone()
            print(f"  Deleted rollup entries")
            
            # 2. Delete from transactions (derived) - both by account_id AND by import_batch_id
            # First by account_id
            d1 = conn.execute("DELETE FROM transactions WHERE account_id = 'Boursorama'").fetchone()
            # Then by import_batch_id to catch any stragglers
            for import_id in import_id_list:
                conn.execute("DELETE FROM transactions WHERE import_batch_id = ?", [import_id])
            print(f"  Deleted processed transactions")
            
            # 3. Delete from transactions_raw using import_batch_id
            for import_id in import_id_list:
                conn.execute("DELETE FROM transactions_raw WHERE import_batch_id = ?", [import_id])
            print(f"  Deleted raw transactions for {len(import_id_list)} imports")
            
            # 4. Now safe to delete from imports
            conn.execute("DELETE FROM imports WHERE bank = 'Boursorama'")
            print(f"  Deleted {len(import_id_list)} import records")
        
        conn.execute("COMMIT;")
        
        print("✅ All Boursorama data cleared successfully!")
        
        # Verify
        imports_left = conn.execute("SELECT COUNT(*) FROM imports WHERE bank = 'Boursorama'").fetchone()[0]
        raw_left = conn.execute("SELECT COUNT(*) FROM transactions_raw WHERE bank = 'Boursorama'").fetchone()[0]
        derived_left = conn.execute("SELECT COUNT(*) FROM transactions WHERE account_id = 'Boursorama'").fetchone()[0]
        
        print(f"\nVerification:")
        print(f"  Imports remaining: {imports_left}")
        print(f"  Raw transactions remaining: {raw_left}")
        print(f"  Processed transactions remaining: {derived_left}")
        
    except Exception as e:
        conn.execute("ROLLBACK;")
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    force_clear_boursorama()