from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List
from app.services.clause_engine import segment_clauses

router = APIRouter(prefix="/clause", tags=["Clause Engine"])

class ClauseSegmentRequest(BaseModel):
    text: str

@router.post("/segment", response_model=Dict[str, Any])
def segment_contract_clauses(request: ClauseSegmentRequest):
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract text cannot be empty."
        )

    clauses = segment_clauses(request.text)
    flagged_count = sum(1 for c in clauses if c["triage_status"] == "flagged_for_rag")

    return {
        "status": "success",
        "total_clauses": len(clauses),
        "flagged_for_rag_count": flagged_count,
        "routine_count": len(clauses) - flagged_count,
        "clauses": clauses
    }
