from fastapi import APIRouter, UploadFile, File, HTTPException, status, Response
from typing import Dict, Any
from app.services.document_parser import process_document
from app.services.pdf_generator import generate_formal_legal_pdf
from app.services.docx_generator import generate_revised_contract_docx
from app.services.certificate_generator import generate_compliance_certificate

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

@router.post("/export-pdf")
async def export_formal_legal_pdf(analysis_data: Dict[str, Any]):
    try:
        pdf_bytes = generate_formal_legal_pdf(analysis_data)
        doc_name = analysis_data.get("document_name", "Contract").replace(" ", "_")
        filename = f"ContractLens_Formal_Legal_Opinion_{doc_name}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate formal PDF report: {str(e)}")

@router.post("/export-docx")
async def export_revised_contract_docx(analysis_data: Dict[str, Any]):
    try:
        docx_bytes = generate_revised_contract_docx(analysis_data)
        doc_name = analysis_data.get("document_name", "Contract").replace(" ", "_")
        filename = f"Revised_Redlined_{doc_name}.docx"
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate revised DOCX contract: {str(e)}")

@router.post("/export-certificate")
async def export_compliance_certificate(analysis_data: Dict[str, Any]):
    try:
        cert_bytes = generate_compliance_certificate(analysis_data)
        doc_name = analysis_data.get("document_name", "Contract").replace(" ", "_")
        filename = f"ContractLens_Compliance_Certificate_{doc_name}.pdf"
        return Response(
            content=cert_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate compliance certificate: {str(e)}")


