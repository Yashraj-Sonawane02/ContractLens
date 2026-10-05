from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.negotiation_engine import generate_negotiation_email

router = APIRouter(prefix="/negotiation", tags=["Contract Negotiation Generator"])

class NegotiationRequest(BaseModel):
    analysis_data: Dict[str, Any]
    tone: Optional[str] = "formal" # "polite", "formal", "legal_notice"
    recipient_name: Optional[str] = "Landlord / Licensor"
    sender_name: Optional[str] = "Tenant / Licensee"
    language: Optional[str] = "English"

@router.post("/generate", response_model=Dict[str, Any])
def generate_negotiation_endpoint(request: NegotiationRequest):
    try:
        result = generate_negotiation_email(
            analysis_data=request.analysis_data,
            tone=request.tone or "formal",
            recipient_name=request.recipient_name or "Landlord / Licensor",
            sender_name=request.sender_name or "Tenant / Licensee",
            language=request.language or "English"
        )
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate negotiation email: {str(e)}"
        )
