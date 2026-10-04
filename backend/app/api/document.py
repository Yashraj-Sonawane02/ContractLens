from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Dict, Any
from app.services.document_parser import process_document

router = APIRouter(prefix="/document", tags=["Document Processing"])

MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024 # 15MB

@router.post("/extract", response_model=Dict[str, Any])
async def extract_document_endpoint(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_contract.pdf"
    ext = filename.split('.')[-1].lower()

    if ext not in ['pdf', 'docx', 'doc', 'txt']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: .{ext}. Please upload a PDF, DOCX, or TXT legal document."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty. Please upload a valid legal document."
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 15MB limit. Please upload a smaller contract document."
        )

    try:
        extraction_result = process_document(filename, file_bytes)
        return {
            "status": "success",
            "message": "Document parsed and structured successfully",
            "data": extraction_result
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process legal document: {str(e)}"
        )
