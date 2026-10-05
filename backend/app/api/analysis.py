import json
import time
import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from app.db.database import get_db
from app.models.models import User, AnalysisHistory
from app.api.auth import get_current_user_optional, decode_access_token
from app.services.document_parser import process_document
from app.services.pii_masker import mask_pii_content
from app.services.clause_engine import segment_clauses
from app.services.parallel_analyzer import analyze_full_contract_parallel
from app.services.empirical_benchmark import run_empirical_accuracy_benchmark
from app.services.evaluation_suite import run_comprehensive_project_evaluation
from app.services.document_classifier import detect_document_type
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["Contract Analysis Pipeline"])

@router.post("/run", response_model=Dict[str, Any])
async def run_contract_analysis(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    language: str = Form("English"),
    domains: str = Form('["rental_property"]'),
    authorization: Optional[str] = Header(None),
    auth_token: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    overall_start = time.time()
    storage_meta = None

    # 1. Document Extraction & Validation
    if file and file.filename:
        filename = file.filename
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
        # Save file to Encrypted Object Storage (AES-256 S3 or Local Fallback)
        try:
            storage_meta = storage_service.upload_file(filename, file_bytes)
        except Exception as storage_err:
            logger.warning(f"Storage service upload warning: {storage_err}")
            storage_meta = {"storage_type": "LOCAL_TEMPORARY", "file_key": None}

        extraction = process_document(filename, file_bytes)
        text_to_process = extraction["raw_text"]
    elif raw_text and len(raw_text.strip()) > 20:
        filename = "pasted_contract.txt"
        text_to_process = raw_text
        file_bytes = raw_text.encode('utf-8')
        try:
            storage_meta = storage_service.upload_file(filename, file_bytes)
        except Exception:
            storage_meta = {"storage_type": "LOCAL_TEMPORARY", "file_key": None}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid legal contract file or text for analysis."
        )

    # 1B. Strict Domain & Document Boundary Validation
    classification = detect_document_type(text_to_process)
    if not classification.get("is_supported_domain", True):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=classification.get("error_message", "Unsupported document domain. System exclusively audits Maharashtra Rental & Property Contracts.")
        )
    doc_type = classification["detected_type"]

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
        "storage_metadata": storage_meta,
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
    token_candidate = authorization or auth_token
    current_user = get_current_user_optional(authorization=token_candidate, db=db)
    if current_user:
        try:
            history_record = AnalysisHistory(
                user_id=current_user.id,
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
                file_key=storage_meta.get("file_key") if storage_meta else None,
                storage_type=storage_meta.get("storage_type", "LOCAL_ENCRYPTED_AES256") if storage_meta else "LOCAL_ENCRYPTED_AES256",
                analysis_result_json=json.dumps(pipeline_output)
            )
            db.add(history_record)
            db.commit()
            logger.info(f"Successfully archived analysis history record {history_record.id} for user {current_user.email}")
        except Exception as hist_err:
            logger.error(f"Failed to record analysis history: {hist_err}")
            db.rollback()

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
            "file_key": r.file_key,
            "storage_type": r.storage_type,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "analysis_result": json.loads(r.analysis_result_json)
        })

    return output

@router.delete("/history/{history_id}", response_model=Dict[str, Any])
def delete_history_record(history_id: int, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required.")

    token = authorization.replace("Bearer ", "").strip()
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id, AnalysisHistory.user_id == user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Audit history record not found.")

    db.delete(record)
    db.commit()
    return {"status": "success", "message": f"Deleted audit history record {history_id}."}

@router.get("/benchmark", response_model=Dict[str, Any])
async def get_empirical_accuracy_benchmark_endpoint():
    try:
        benchmark_results = await run_empirical_accuracy_benchmark()
        return benchmark_results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run empirical accuracy benchmark: {str(e)}"
        )

@router.get("/comprehensive-evaluation", response_model=Dict[str, Any])
async def get_comprehensive_evaluation_endpoint():
    try:
        results = await run_comprehensive_project_evaluation()
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute comprehensive multi-dataset evaluation: {str(e)}"
        )
