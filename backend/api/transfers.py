from fastapi import APIRouter, HTTPException
from models.dto import (
    TransferProposeRequest, TransferProposeResponse, TransferProposal,
    TransferConfirmRequest, TransferConfirmResponse
)
from services.transfers import propose_transfers, confirm_transfers

router = APIRouter()

@router.post("/transfers/propose", response_model=TransferProposeResponse)
async def propose_transfers_endpoint(request: TransferProposeRequest):
    """
    Propose transfer candidates using heuristic matching.
    
    Finds potential transfers by matching:
    - Same absolute amount
    - Opposite signs (one positive, one negative)
    - Different accounts
    - Within ±1 day of each other
    """
    
    try:
        proposals = propose_transfers(
            month=request.month,
            accounts=request.accounts
        )
        
        # Convert to response format
        proposal_objects = []
        for proposal in proposals:
            proposal_objects.append(TransferProposal(**proposal))
        
        return TransferProposeResponse(
            proposals=proposal_objects,
            total_count=len(proposal_objects)
        )
        
    except Exception as e:
        print(f"Transfer proposal error: {e}")
        raise HTTPException(status_code=500, detail=f"Error proposing transfers: {str(e)}")

@router.post("/transfers/confirm", response_model=TransferConfirmResponse)
async def confirm_transfers_endpoint(request: TransferConfirmRequest):
    """
    Confirm transfer proposals by marking transactions as transfers.
    
    Creates overrides to mark both transactions in each pair as transfers.
    Updates rollups to exclude these from P&L calculations.
    """
    
    try:
        # Extract proposal IDs (not used currently but included for future)
        proposal_ids = [f"proposal_{i}" for i in range(len(request.transaction_pairs))]
        
        result = confirm_transfers(
            proposal_ids=proposal_ids,
            transaction_pairs=request.transaction_pairs
        )
        
        return TransferConfirmResponse(**result)
        
    except Exception as e:
        print(f"Transfer confirmation error: {e}")
        raise HTTPException(status_code=500, detail=f"Error confirming transfers: {str(e)}")

@router.get("/transfers/potential/{transaction_id}")
async def get_potential_transfers(transaction_id: str):
    """
    Get potential transfer matches for a specific transaction.
    
    Useful for manual transfer matching in the UI.
    """
    
    try:
        from services.transfers import get_potential_transfers
        
        matches = get_potential_transfers(transaction_id)
        
        return {
            "transaction_id": transaction_id,
            "potential_matches": matches,
            "match_count": len(matches)
        }
        
    except Exception as e:
        print(f"Potential transfers error: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting potential transfers: {str(e)}")