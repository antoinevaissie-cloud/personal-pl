#!/usr/bin/env python3
"""Clear test data for a specific user to allow re-uploading files."""

import sys
from db.duck import execute_update, execute_query

def clear_user_data(username: str):
    """Clear all data for a specific user."""
    
    # Get user ID
    result = execute_query(
        "SELECT id FROM users WHERE username = ?",
        [username]
    )
    
    if not result:
        print(f"User '{username}' not found")
        return False
    
    user_id = result[0][0]
    print(f"Found user '{username}' with ID: {user_id}")
    
    # Clear data in order (respecting foreign keys)
    tables_to_clear = [
        ("transactions", "user_id"),
        ("transactions_raw", "user_id"),
        ("imports", "user_id"),
        ("rollup_monthly", "user_id"),
        ("txn_overrides", "user_id"),
        ("category_rules", "user_id"),
    ]
    
    for table, user_column in tables_to_clear:
        count = execute_update(
            f"DELETE FROM {table} WHERE {user_column} = ?",
            [user_id]
        )
        print(f"Deleted {count} rows from {table}")
    
    print(f"\nAll data cleared for user '{username}'")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python clear_test_data.py <username>")
        print("Example: python clear_test_data.py testuser")
        sys.exit(1)
    
    username = sys.argv[1]
    if clear_user_data(username):
        print("You can now re-upload files for this user.")
    else:
        sys.exit(1)