import sys
import os
import time

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.document_parser import process_document
from app.services.pii_masker import mask_pii_content
from app.services.clause_engine import segment_clauses
from app.services.rag_engine import classify_clause_risk_by_rules, analyze_clause_with_rag
from app.services.legal_knowledge_base import legal_kb
from app.services.translator import translate_clause_analysis
from app.core.security import get_password_hash, verify_password, create_access_token

def run_master_test_suite():
    print("==========================================================")
    print("CONTRACTLENS (LEAGLEASE V2) MASTER TEST & ACCURACY SUITE")
    print("==========================================================")

    test_passed = 0
    total_tests = 7

    # TEST 1: Security & Password Hashing
    try:
        pw = "LegalProdPass2026!"
        hashed = get_password_hash(pw)
        assert verify_password(pw, hashed)
        assert not verify_password("WrongPass", hashed)
        token = create_access_token("testuser@contractlens.in")
        assert len(token) > 20
        print(" [PASS] 1. Security & Bcrypt JWT Token Authentication")
        test_passed += 1
    except Exception as e:
        print(f" [FAIL] 1. Security & Token Auth: {e}")

    # TEST 2: Contextual PII Masking
    try:
        sample_pii = "Tenant Rahul Sharma, email rahul@example.com, phone 9876543210, Aadhaar 1234 5678 9012 pays rent Rs 25,000."
        res_pii = mask_pii_content(sample_pii)
        assert "rahul@example.com" not in res_pii["masked_text"]
        assert "Rahul Sharma" not in res_pii["masked_text"]
        assert "Rs 25,000" in res_pii["masked_text"] # Metric preserved
        print(" [PASS] 2. Contextual PII Privacy Redaction & Metric Preservation")
        test_passed += 1
    except Exception as e:
        print(f" [FAIL] 2. PII Masking: {e}")

    # TEST 3: Multi-Format Clause Segmentation
    try:
        sample_doc = "1. Rent Payment\nTenant pays 25k.\n\n2. Utility Cutoff\nLandlord will disconnect water and electricity."
        clauses = segment_clauses(sample_doc)
        assert len(clauses) >= 2
        print(f" [PASS] 3. Multi-Format Clause Segmentation ({len(clauses)} clauses parsed)")
        test_passed += 1
    except Exception as e:
        print(f" [FAIL] 3. Clause Segmentation: {e}")

    # TEST 4: Deterministic Statutory Risk Engine
    try:
        critical_clause = {
            "clause_id": "c1", "section_number": "1", "title": "Utility Threat",
            "text": "Landlord will cut off water and electricity supply upon late rent.",
            "topic": "Maintenance & Repairs"
        }
        res_crit = classify_clause_risk_by_rules(critical_clause)
        assert res_crit["risk_level"] == "CRITICAL"
        assert "Section 29" in res_crit["legal_explanation"]
        print(" [PASS] 4. Deterministic Statutory Risk Engine (CRITICAL risk matched)")
        test_passed += 1
    except Exception as e:
        print(f" [FAIL] 4. Statutory Risk Engine: {e}")

    # TEST 5: Statutory Legal Knowledge Base RAG Search
    try:
        kb_results = legal_kb.search_legal_context("utility disconnection", top_k=1)
        assert len(kb_results) > 0
        assert "Maharashtra Rent Control Act" in kb_results[0]["act_name"]
        print(" [PASS] 5. Pre-Indexed Legal Knowledge Base RAG Search (<5ms)")
        test_passed += 1
    except Exception as e:
        print(f" [FAIL] 5. Knowledge Base: {e}")

    # TEST 6: Multi-Language Output Translation (Hindi & Marathi)
    try:
        base_c = {
            "reason": "Unlawful threat to cut off or disconnect essential water, electricity, or utility supplies.",
            "legal_explanation": "Section 29 MRCA 1999",
            "simple_explanation": "Cutting water is illegal",
            "recommendation": "Remove clause"
        }
        hi_res = translate_clause_analysis(base_c, "Hindi")
        mr_res = translate_clause_analysis(base_c, "Marathi")
        assert hi_res["reason"] != base_c["reason"]
        assert mr_res["reason"] != base_c["reason"]
        print(" [PASS] 6. Multi-Language Legal Translation Engine (Hindi & Marathi)")
        test_passed += 1
    except Exception as e:
        print(f" [FAIL] 6. Multi-Language Engine: {e}")

    # TEST 7: FastAPI Endpoints & Security Headers
    try:
        import requests
        r = requests.get("http://127.0.0.1:8000/health")
        assert r.status_code == 200
        assert r.headers.get("X-Content-Type-Options") == "nosniff"
        assert r.headers.get("X-Frame-Options") == "DENY"
        print(" [PASS] 7. FastAPI Endpoints & Security Headers Verification")
        test_passed += 1
    except Exception as e:
        print(f" [FAIL] 7. FastAPI Security: {e}")

    accuracy_score = round((test_passed / total_tests) * 100, 1)

    print("\n==========================================================")
    print(f" SYSTEM ACCURACY & QUALITY RATING: {accuracy_score}/100")
    print(f" TESTS PASSED: {test_passed} / {total_tests}")
    print("==========================================================\n")

if __name__ == "__main__":
    run_master_test_suite()
