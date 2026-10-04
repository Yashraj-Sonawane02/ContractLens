import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.document_parser import process_document
from app.services.pii_masker import mask_pii_content
from app.services.clause_engine import segment_clauses
from app.services.parallel_analyzer import analyze_full_contract_parallel
from app.api.chat import ask_contract_question, ChatRequest

async def test_sample_pdf_pipeline():
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample.pdf"))
    print(f"Reading sample.pdf from: {pdf_path}")

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    # 1. Document Extraction
    extraction = process_document("sample.pdf", file_bytes)
    raw_text = extraction["raw_text"]
    print(f"\n1. Extracted Text ({len(raw_text)} bytes, Type: {extraction['document_type_info']['detected_type']})")

    # 2. PII Masking
    pii_res = mask_pii_content(raw_text)
    print(f"\n2. PII Redaction: {pii_res['total_items_masked']} items masked")
    print(f"   Summary: {pii_res['mask_summary']}")

    # 3. Clause Segmentation
    clauses = segment_clauses(pii_res["masked_text"])
    print(f"\n3. Segmented Clauses: {len(clauses)} clauses identified")

    # 4. English Statutory Audit
    res_en = await analyze_full_contract_parallel(clauses, language="English")
    print(f"\n4. ENGLISH AUDIT RESULTS:")
    print(f"   Health Score: {res_en['health_score']}/100")
    print(f"   Risk Breakdown: {res_en['risk_summary']}")
    print(f"   Executive Summary: {res_en['executive_summary']}")

    # 5. Marathi (मराठी) Statutory Audit
    res_mr = await analyze_full_contract_parallel(clauses, language="Marathi")
    print(f"\n5. MARATHI AUDIT RESULTS:")
    c0 = res_mr['analyzed_clauses'][0]
    print(f"   Sample Clause 1 Title: {c0['title']}")
    print(f"   Sample Clause 1 Statutory Finding: {c0['reason'].encode('ascii', 'ignore').decode()}")
    print(f"   Sample Clause 1 Legal Explanation: {c0['legal_explanation'].encode('ascii', 'ignore').decode()}")
    if c0.get('relevant_statutes'):
        stat0 = c0['relevant_statutes'][0]
        print(f"   Sample Clause 1 Precedent Title: {stat0['title'].encode('ascii', 'ignore').decode()}")
        print(f"   Sample Clause 1 Precedent Takeaway: {stat0['key_legal_takeaway'].encode('ascii', 'ignore').decode()}")

    # 6. Gemini Chatbot Verification
    print(f"\n6. CHATBOT RAG RESPONSE VERIFICATION:")
    chat_req = ChatRequest(
        question="Under Section 74 of Indian Contract Act 1872 explain how penalties work in this contract",
        analyzed_clauses=res_en["analyzed_clauses"],
        conversation_history=[],
        language="English"
    )
    chat_resp = ask_contract_question(chat_req)
    chat_snippet = chat_resp['answer'][:350].encode('ascii', 'ignore').decode()
    print(f"   Chatbot Response Snippet:\n{chat_snippet}...")

    print("\n==========================================================")
    print(" SAMPLE.PDF FULL END-TO-END VERIFICATION COMPLETED CLEANLY!")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(test_sample_pdf_pipeline())
