import json
import time
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from app.db.database import get_db
from app.models.models import User, AnalysisHistory
from app.api.auth import decode_access_token
from app.services.document_parser import process_document
from app.services.pii_masker import mask_pii_content
from app.services.clause_engine import segment_clauses
from app.services.parallel_analyzer import analyze_full_contract_parallel

router = APIRouter(prefix="/analysis", tags=["Contract Analysis Pipeline"])

@router.post("/run", response_model=Dict[str, Any])
async def run_contract_analysis(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    language: str = Form("English"),
    domains: str = Form('["rental_property"]'),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    overall_start = time.time()

    # 1. Document Extraction & Validation
    if file and file.filename:
        filename = file.filename
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        extraction = process_document(filename, file_bytes)
        text_to_process = extraction["raw_text"]
        doc_type = extraction["document_type_info"]["detected_type"]
    elif raw_text and len(raw_text.strip()) > 20:
        filename = "pasted_contract.txt"
        text_to_process = raw_text
        doc_type = "Maharashtra Leave & License Agreement"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid legal contract file or text for analysis."
        )

    # 2. PII Privacy Masking
    privacy_result = mask_pii_content(text_to_process)
    masked_text = privacy_result["masked_text"]

    # 3. Clause Segmentation & Stage-1 Triage
    segmented_clauses = segment_clauses(masked_text)

    # 4. Async Parallel Statutory RAG Analysis
    analysis_result = await analyze_full_contract_parallel(segmented_clauses, language=language)

    total_latency = round(time.time() - overall_start, 3)

    # Compile Final Pipeline Payload
    pipeline_output = {
        "status": "success",
        "document_name": filename,
        "document_type": doc_type,
        "language": language,
        "domains": json.loads(domains) if isinstance(domains, str) else domains,
        "privacy_summary": privacy_result["mask_summary"],
        "total_items_masked": privacy_result["total_items_masked"],
        "health_score": analysis_result["health_score"],
        "risk_summary": analysis_result["risk_summary"],
        "executive_summary": analysis_result["executive_summary"],
        "top_concerns": analysis_result["top_concerns"],
        "processing_time_seconds": total_latency,
        "risk_heatmap": analysis_result["risk_heatmap"],
        "analyzed_clauses": analysis_result["analyzed_clauses"]
    }

    # 5. Save to User History if Authenticated
    current_user_email = None
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        current_user_email = decode_access_token(token)

    if current_user_email:
        user = db.query(User).filter(User.email == current_user_email).first()
        if user:
            history_record = AnalysisHistory(
                user_id=user.id,
                document_name=filename,
                document_type=doc_type,
                selected_domains=domains,
                health_score=analysis_result["health_score"],
                critical_count=analysis_result["risk_summary"]["critical"],
                high_count=analysis_result["risk_summary"]["high"],
                medium_count=analysis_result["risk_summary"]["medium"],
                low_count=analysis_result["risk_summary"]["low"],
                total_clauses=len(segmented_clauses),
                processing_time_seconds=total_latency,
                analysis_result_json=json.dumps(pipeline_output)
            )
            db.add(history_record)
            db.commit()

    return pipeline_output

@router.get("/history", response_model=List[Dict[str, Any]])
def get_user_history(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required.")

    token = authorization.replace("Bearer ", "").strip()
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    records = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == user.id).order_by(AnalysisHistory.created_at.desc()).all()
    
    output = []
    for r in records:
        output.append({
            "id": r.id,
            "document_name": r.document_name,
            "document_type": r.document_type,
            "health_score": r.health_score,
            "critical_count": r.critical_count,
            "high_count": r.high_count,
            "medium_count": r.medium_count,
            "low_count": r.low_count,
            "total_clauses": r.total_clauses,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "analysis_result": json.loads(r.analysis_result_json)
        })

    return output
