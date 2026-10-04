from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
from app.services.pii_masker import mask_pii_content

router = APIRouter(prefix="/privacy", tags=["Privacy Protection"])

class MaskRequest(BaseModel):
    text: str

@router.post("/mask", response_model=Dict[str, Any])
def mask_contract_privacy(request: MaskRequest):
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract text cannot be empty."
        )

    result = mask_pii_content(request.text)
    return {
        "status": "success",
        "message": f"Privacy masking completed cleanly. Masked {result['total_items_masked']} sensitive data points.",
        "data": result
    }
