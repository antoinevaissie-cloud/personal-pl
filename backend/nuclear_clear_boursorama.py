#!/usr/bin/env python3
"""Nuclear option - clear ALL Boursorama data, bypassing constraints"""

from db.duck import get_conn

def nuclear_clear():
    conn = get_conn()
    
    print("NUCLEAR CLEAR - Removing ALL Boursorama data...")
    print("-" * 50)
    
    try:
        # Disable foreign key constraints temporarily
        conn.execute("BEGIN;")
        
        # Get stats before
        stats_before = {
            'imports': conn.execute("SELECT COUNT(*) FROM imports WHERE bank = 'Boursorama'").fetchone()[0],
            'raw': conn.execute("SELECT COUNT(*) FROM transactions_raw WHERE bank = 'Boursorama'").fetchone()[0],
            'transactions': conn.execute("SELECT COUNT(*) FROM transactions WHERE account_id = 'Boursorama'").fetchone()[0],
            'rollup': conn.execute("SELECT COUNT(*) FROM rollup_monthly WHERE account_id = 'Boursorama'").fetchone()[0]
        }
        
        print(f"Before deletion:")
        for key, val in stats_before.items():
            print(f"  {key}: {val}")
        
        # Get all Boursorama import IDs
        import_ids = conn.execute("SELECT id FROM imports WHERE bank = 'Boursorama'").fetchall()
        import_id_list = [str(row[0]) for row in import_ids]
        
        if import_id_list:
            # Delete EVERYTHING that could reference these imports
            
            # 1. Delete from transactions by import_batch_id
            for import_id in import_id_list:
                conn.execute("DELETE FROM transactions WHERE import_batch_id = ?", [import_id])
            
            # 2. Also delete by account_id to be sure
            conn.execute("DELETE FROM transactions WHERE account_id = 'Boursorama'")
            
            # 3. Delete overrides if any
            conn.execute("""
                DELETE FROM txn_overrides 
                WHERE txn_id IN (
                    SELECT id FROM transactions WHERE account_id = 'Boursorama'
                )
            """)
            
            # 4. Delete from transactions_raw
            for import_id in import_id_list:
                count = conn.execute("DELETE FROM transactions_raw WHERE import_batch_id = ?", [import_id]).fetchone()
            
            # Also try by bank
            conn.execute("DELETE FROM transactions_raw WHERE bank = 'Boursorama'")
            
            # 5. Delete from rollup
            conn.execute("DELETE FROM rollup_monthly WHERE account_id = 'Boursorama'")
            
            # 6. Finally delete imports
            conn.execute("DELETE FROM imports WHERE bank = 'Boursorama'")
        
        conn.execute("COMMIT;")
        
        # Get stats after
        stats_after = {
            'imports': conn.execute("SELECT COUNT(*) FROM imports WHERE bank = 'Boursorama'").fetchone()[0],
            'raw': conn.execute("SELECT COUNT(*) FROM transactions_raw WHERE bank = 'Boursorama'").fetchone()[0],
            'transactions': conn.execute("SELECT COUNT(*) FROM transactions WHERE account_id = 'Boursorama'").fetchone()[0],
            'rollup': conn.execute("SELECT COUNT(*) FROM rollup_monthly WHERE account_id = 'Boursorama'").fetchone()[0]
        }
        
        print(f"\n✅ SUCCESS! After deletion:")
        for key, val in stats_after.items():
            print(f"  {key}: {val}")
            
    except Exception as e:
        conn.execute("ROLLBACK;")
        print(f"\n❌ Failed: {e}")
        print("\nTrying alternative approach...")
        
        # Alternative: Drop foreign key constraint temporarily
        try:
            conn.execute("BEGIN;")
            
            # Get import IDs
            import_ids = conn.execute("SELECT id FROM imports WHERE bank = 'Boursorama'").fetchall()
            
            for import_id in import_ids:
                id_str = str(import_id[0])
                # Force delete from all tables
                conn.execute(f"DELETE FROM transactions_raw WHERE import_batch_id = '{id_str}'")
                conn.execute(f"DELETE FROM transactions WHERE import_batch_id = '{id_str}'")
            
            conn.execute("DELETE FROM rollup_monthly WHERE account_id = 'Boursorama'")
            conn.execute("DELETE FROM imports WHERE bank = 'Boursorama'")
            
            conn.execute("COMMIT;")
            print("✅ Alternative approach succeeded!")
            
        except Exception as e2:
            conn.execute("ROLLBACK;")
            print(f"❌ Alternative also failed: {e2}")
            raise

if __name__ == "__main__":
    nuclear_clear()