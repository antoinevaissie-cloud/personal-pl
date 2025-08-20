from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import PlainTextResponse
from models.dto import (
    JournalCreateRequest, JournalUpdateRequest, JournalResponse,
    JournalListRequest
)
from services.journal import (
    create_journal_entry, update_journal_entry, get_journal_entry,
    get_journal_entries_by_month, export_journal_as_markdown
)
from datetime import datetime
from typing import List, Optional

router = APIRouter()

@router.post("/journal", response_model=JournalResponse)
async def create_journal(request: JournalCreateRequest):
    """
    Create a new journal entry with auto-generated metrics snapshot.
    
    The system automatically appends financial metrics for the period.
    """
    
    try:
        entry_id = create_journal_entry(
            period_start=request.period_start,
            period_end=request.period_end,
            observations_md=request.observations_md,
            decisions_md=request.decisions_md
        )
        
        entry = get_journal_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=500, detail="Error retrieving created journal entry")
        
        return JournalResponse(**entry)
        
    except Exception as e:
        print(f"Journal creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating journal entry: {str(e)}")

@router.patch("/journal/{entry_id}", response_model=JournalResponse)
async def update_journal(
    entry_id: str = Path(...),
    request: JournalUpdateRequest = ...
):
    """
    Update an existing journal entry.
    
    Auto-regenerates metrics snapshot if observations are updated.
    """
    
    try:
        entry = update_journal_entry(
            entry_id=entry_id,
            observations_md=request.observations_md,
            decisions_md=request.decisions_md
        )
        
        return JournalResponse(**entry)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Journal update error: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating journal entry: {str(e)}")

@router.get("/journal/{entry_id}", response_model=JournalResponse)
async def get_journal(entry_id: str = Path(...)):
    """Get a specific journal entry by ID."""
    
    try:
        entry = get_journal_entry(entry_id)
        
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        return JournalResponse(**entry)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Journal get error: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting journal entry: {str(e)}")

@router.get("/journal", response_model=List[JournalResponse])
async def list_journal_entries(month: Optional[str] = None):
    """
    List journal entries, optionally filtered by month.
    
    - **month**: Optional month filter in YYYY-MM format
    """
    
    try:
        if month:
            # Parse month (YYYY-MM format)
            try:
                month_date = datetime.strptime(f"{month}-01", '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Month must be in YYYY-MM format")
            
            entries = get_journal_entries_by_month(month_date)
        else:
            # Get all entries (implement if needed)
            entries = []
        
        return [JournalResponse(**entry) for entry in entries]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Journal list error: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing journal entries: {str(e)}")

@router.get("/journal/{entry_id}/export", response_class=PlainTextResponse)
async def export_journal(entry_id: str = Path(...)):
    """
    Export journal entry as formatted Markdown.
    
    Returns plain text Markdown suitable for download.
    """
    
    try:
        markdown_content = export_journal_as_markdown(entry_id)
        
        return PlainTextResponse(
            content=markdown_content,
            headers={
                "Content-Disposition": f"attachment; filename=journal_{entry_id}.md"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Journal export error: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting journal entry: {str(e)}")

@router.delete("/journal/{entry_id}")
async def delete_journal(entry_id: str = Path(...)):
    """Delete a journal entry."""
    
    try:
        from db.duck import execute_update, get_conn
        
        conn = get_conn()
        
        # Check if entry exists
        existing = conn.execute("SELECT id FROM journal_entries WHERE id = ?", [entry_id]).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        execute_update("DELETE FROM journal_entries WHERE id = ?", [entry_id])
        
        return {"message": f"Journal entry {entry_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Journal deletion error: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting journal entry: {str(e)}")