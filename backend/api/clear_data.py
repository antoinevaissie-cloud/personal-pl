from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from db.duck import execute_update
from typing import Dict, Any

router = APIRouter()

@router.post("/api/clear-data")
async def clear_user_data(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Clear all data for the current user (for testing purposes)."""
    user_id = current_user["id"]
    
    # Clear data in order (respecting foreign keys)
    tables_to_clear = [
        ("transactions", "user_id"),
        ("transactions_raw", "user_id"),
        ("imports", "user_id"),
        ("rollup_monthly", "user_id"),
        ("txn_overrides", "user_id"),
        ("category_rules", "user_id"),
    ]
    
    cleared = {}
    for table, user_column in tables_to_clear:
        count = execute_update(
            f"DELETE FROM {table} WHERE {user_column} = ?",
            [user_id]
        )
        cleared[table] = count
    
    return {
        "message": "All data cleared successfully",
        "cleared": cleared
    }