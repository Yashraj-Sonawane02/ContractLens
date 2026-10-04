from app.services.rag_engine import analyze_full_contract

def test_risk_scoring_and_heatmap():
    clauses = [
        {"clause_id": "c1", "section_number": "1", "title": "Premises", "text": "Flat 302, Bandra", "topic": "General Obligations", "triage_status": "routine"},
        {"clause_id": "c2", "section_number": "2", "title": "Rent", "text": "₹55,000 monthly", "topic": "Rent & License Fee", "triage_status": "routine"},
        {"clause_id": "c3", "section_number": "3", "title": "Penalty", "text": "₹2,000 per day penalty for delay", "topic": "Penalty & Interest", "triage_status": "flagged_for_rag"},
        {"clause_id": "c4", "section_number": "4", "title": "Utilities Cutoff", "text": "Licensor may cut off water and electricity", "topic": "Maintenance & Repairs", "triage_status": "flagged_for_rag"}
    ]

    result = analyze_full_contract(clauses)

    # Health score should drop from 100 to 60 due to 2 critical clauses (20 * 2 = 40 deduction)
    assert result["health_score"] == 60
    assert result["risk_summary"]["critical"] == 2
    assert len(result["risk_heatmap"]) == 4

    print("PHASE 8 & 9 RISK SCORING AND HEATMAP DATA TESTS PASSED CLEANLY!")
    print(f"Health Score: {result['health_score']}/100")
    print(f"Heatmap Nodes: {result['risk_heatmap']}")

if __name__ == "__main__":
    test_risk_scoring_and_heatmap()
