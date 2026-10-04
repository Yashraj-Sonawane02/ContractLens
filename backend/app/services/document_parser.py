import re
import io
from typing import Dict, Any, List
import pdfplumber
from pypdf import PdfReader
import docx
from app.services.document_classifier import detect_document_type

def extract_legal_metrics(text: str) -> Dict[str, List[str]]:
    """Extract critical legal figures that MUST NOT be masked (monetary amounts, dates, rates, notice periods)."""
    monetary_amounts = list(set(re.findall(r'(?:₹|INR|Rs\.?)\s*[\d,]+(?:\.\d+)?', text, re.IGNORECASE)))
    percentages = list(set(re.findall(r'\b\d+(?:\.\d+)?\s*%', text)))
    notice_periods = list(set(re.findall(r'\b\d+\s*(?:day|month|week)s?\b(?:\s*notice)?', text, re.IGNORECASE)))
    dates = list(set(re.findall(r'\b(?:\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b', text, re.IGNORECASE)))
    
    return {
        "monetary_amounts": monetary_amounts,
        "percentages": percentages,
        "notice_periods": notice_periods,
        "dates": dates
    }

def parse_pdf(file_bytes: bytes) -> Dict[str, Any]:
    full_text = ""
    tables = []
    sections = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                full_text += f"\n--- Page {i+1} ---\n" + page_text
                
                # Extract tables
                page_tables = page.extract_tables()
                for t in page_tables:
                    if t:
                        tables.append({"page": i+1, "rows": t})
    except Exception:
        # Fallback to PyPDF if pdfplumber encounters an issue
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text() or ""
            full_text += f"\n--- Page {i+1} ---\n" + page_text

    return {
        "text": full_text.strip(),
        "tables": tables
    }

def parse_docx(file_bytes: bytes) -> Dict[str, Any]:
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs)

    tables = []
    for t_idx, table in enumerate(doc.tables):
        rows = []
        for row in table.rows:
            rows.append([cell.text.strip() for cell in row.cells])
        tables.append({"table_index": t_idx + 1, "rows": rows})

    return {
        "text": full_text.strip(),
        "tables": tables
    }

def parse_txt(file_bytes: bytes) -> Dict[str, Any]:
    try:
        text = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        text = file_bytes.decode('latin-1', errors='replace')

    return {
        "text": text.strip(),
        "tables": []
    }

def process_document(file_name: str, file_bytes: bytes) -> Dict[str, Any]:
    ext = file_name.split('.')[-1].lower()

    if ext == 'pdf':
        parsed_data = parse_pdf(file_bytes)
    elif ext in ['docx', 'doc']:
        parsed_data = parse_docx(file_bytes)
    elif ext == 'txt':
        parsed_data = parse_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file format: .{ext}. Supported formats are PDF, DOCX, and TXT.")

    raw_text = parsed_data["text"]

    if not raw_text or len(raw_text.strip()) < 20:
        raise ValueError("We could not extract meaningful content from this document. Please upload a readable legal document.")

    # Split into sections based on numbered titles or headings
    raw_sections = re.split(r'\n(?=(?:Clause|Section|Article|\d+\.|\b[A-Z\s]{4,}\b)\s)', raw_text)
    sections = [s.strip() for s in raw_sections if s.strip()]

    legal_metrics = extract_legal_metrics(raw_text)
    doc_type_info = detect_document_type(raw_text)

    return {
        "file_name": file_name,
        "file_type": ext,
        "total_char_count": len(raw_text),
        "total_sections": len(sections),
        "raw_text": raw_text,
        "sections": sections[:50], # first 50 sections for efficiency
        "tables": parsed_data["tables"],
        "extracted_metrics": legal_metrics,
        "document_type_info": doc_type_info
    }
