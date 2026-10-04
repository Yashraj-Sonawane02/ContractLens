from app.services.clause_engine import segment_clauses

def test_maharashtra_clause_segmentation():
    sample_text = """
1. DEMISED PREMISES
The Licensor agrees to let out Flat No 302, Bandra West, Mumbai to the Licensee for residential use.

2. LICENSE FEE AND SECURITY DEPOSIT
The Licensee shall pay a monthly license fee of ₹55,000 per month.
The Licensee has deposited a refundable Security Deposit of ₹2,000,000.

3. LOCK-IN PERIOD AND TERMINATION
This agreement has a strict lock-in period of 12 months. If the Licensee exits early, the entire Security Deposit shall be forfeited.

4. DELAYED PAYMENT PENALTY
Any delayed payment attracts a penalty of ₹2,000 per day of delay and interest of 18% per annum.
"""

    clauses = segment_clauses(sample_text)
    assert len(clauses) >= 4

    # Check Clause 2: Security Deposit Topic
    clause_2 = clauses[1]
    assert clause_2["topic"] == "Security Deposit" or "Rent" in clause_2["topic"]

    # Check Clause 3: Lock-in (Should be flagged for RAG due to forfeiture & lock-in)
    clause_3 = clauses[2]
    assert clause_3["triage_status"] == "flagged_for_rag"

    # Check Clause 4: Penalty (Should be flagged for RAG due to penalty keyword)
    clause_4 = clauses[3]
    assert clause_4["triage_status"] == "flagged_for_rag"

    print("CLAUSE SEGMENTATION & STAGE-1 TRIAGE TESTS PASSED CLEANLY!")
    print(f"Total Clauses Segmented: {len(clauses)}")
    for c in clauses:
        print(f" - [{c['clause_id']}] {c['title']} | Topic: {c['topic']} | Triage: {c['triage_status']}")

if __name__ == "__main__":
    test_maharashtra_clause_segmentation()
