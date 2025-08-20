from fastapi import APIRouter, HTTPException, Path
from models.dto import (
    RuleCreateRequest, RuleUpdateRequest, RuleResponse, 
    RulePreviewRequest, RulePreviewResponse
)
from services.rules_engine import preview_rule_matches
from db.duck import get_conn, execute_update
import uuid
from typing import List

router = APIRouter()

@router.post("/rules", response_model=RuleResponse)
async def create_rule(request: RuleCreateRequest):
    """Create a new category rule."""
    
    try:
        rule_id = str(uuid.uuid4())
        
        execute_update("""
            INSERT INTO category_rules (
                id, active, priority, field, operator, pattern,
                set_category, set_subcategory, set_is_transfer
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, {
            'id': rule_id,
            'active': request.active,
            'priority': request.priority,
            'field': request.field.value,
            'operator': request.operator.value,
            'pattern': request.pattern,
            'set_category': request.set_category,
            'set_subcategory': request.set_subcategory,
            'set_is_transfer': request.set_is_transfer
        })
        
        return RuleResponse(
            id=rule_id,
            field=request.field,
            operator=request.operator,
            pattern=request.pattern,
            set_category=request.set_category,
            set_subcategory=request.set_subcategory,
            set_is_transfer=request.set_is_transfer,
            priority=request.priority,
            active=request.active
        )
        
    except Exception as e:
        print(f"Rule creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating rule: {str(e)}")

@router.get("/rules", response_model=List[RuleResponse])
async def get_rules():
    """Get all category rules."""
    
    try:
        conn = get_conn()
        
        result = conn.execute("""
            SELECT id, active, priority, field, operator, pattern,
                   set_category, set_subcategory, set_is_transfer
            FROM category_rules
            ORDER BY priority DESC, created_at ASC
        """).fetchall()
        
        rules = []
        columns = ['id', 'active', 'priority', 'field', 'operator', 'pattern',
                  'set_category', 'set_subcategory', 'set_is_transfer']
        
        for row in result:
            rule_data = dict(zip(columns, row))
            rules.append(RuleResponse(**rule_data))
        
        return rules
        
    except Exception as e:
        print(f"Rules list error: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting rules: {str(e)}")

@router.patch("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(rule_id: str = Path(...), request: RuleUpdateRequest = ...):
    """Update an existing category rule."""
    
    try:
        conn = get_conn()
        
        # Check if rule exists
        existing = conn.execute("SELECT id FROM category_rules WHERE id = ?", [rule_id]).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Build dynamic update query
        update_fields = {}
        if request.field is not None:
            update_fields['field'] = request.field.value
        if request.operator is not None:
            update_fields['operator'] = request.operator.value
        if request.pattern is not None:
            update_fields['pattern'] = request.pattern
        if request.set_category is not None:
            update_fields['set_category'] = request.set_category
        if request.set_subcategory is not None:
            update_fields['set_subcategory'] = request.set_subcategory
        if request.set_is_transfer is not None:
            update_fields['set_is_transfer'] = request.set_is_transfer
        if request.priority is not None:
            update_fields['priority'] = request.priority
        if request.active is not None:
            update_fields['active'] = request.active
        
        if update_fields:
            set_clauses = []
            params = []
            
            for field, value in update_fields.items():
                set_clauses.append(f"{field} = ?")
                params.append(value)
            
            params.append(rule_id)
            
            update_query = f"""
                UPDATE category_rules 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """
            
            execute_update(update_query, params)
        
        # Get updated rule
        updated_rule = conn.execute("""
            SELECT id, active, priority, field, operator, pattern,
                   set_category, set_subcategory, set_is_transfer
            FROM category_rules WHERE id = ?
        """, [rule_id]).fetchone()
        
        columns = ['id', 'active', 'priority', 'field', 'operator', 'pattern',
                  'set_category', 'set_subcategory', 'set_is_transfer']
        
        rule_data = dict(zip(columns, updated_rule))
        return RuleResponse(**rule_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Rule update error: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating rule: {str(e)}")

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str = Path(...)):
    """Delete a category rule."""
    
    try:
        conn = get_conn()
        
        # Check if rule exists
        existing = conn.execute("SELECT id FROM category_rules WHERE id = ?", [rule_id]).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        execute_update("DELETE FROM category_rules WHERE id = ?", [rule_id])
        
        return {"message": f"Rule {rule_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Rule deletion error: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting rule: {str(e)}")

@router.post("/rules/preview", response_model=RulePreviewResponse)
async def preview_rule(request: RulePreviewRequest):
    """Preview how many transactions would match a proposed rule."""
    
    try:
        preview_data = preview_rule_matches(
            field=request.field.value,
            operator=request.operator.value,
            pattern=request.pattern,
            period_month=request.period_month.isoformat() if request.period_month else None
        )
        
        return RulePreviewResponse(**preview_data)
        
    except Exception as e:
        print(f"Rule preview error: {e}")
        raise HTTPException(status_code=500, detail=f"Error previewing rule: {str(e)}")