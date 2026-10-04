from app.services.legal_knowledge_base import legal_kb

def test_legal_knowledge_base_retrieval():
    # Test 1: Penalty & Security Deposit Query
    res_penalty = legal_kb.search_legal_context("excessive penalty for delay and security deposit forfeiture", top_k=2)
    assert len(res_penalty) > 0
    assert any("Section 74" in r["section"] or "Section 24" in r["section"] for r in res_penalty)

    # Test 2: Registration Query
    res_reg = legal_kb.search_legal_context("leave and license agreement registration obligation", top_k=1)
    assert len(res_reg) > 0
    assert "Section 55" in res_reg[0]["section"]
    assert "Maharashtra Rent Control Act" in res_reg[0]["act_name"]

    # Test 3: Essential Supply & Eviction Query
    res_evict = legal_kb.search_legal_context("landlord cutting electricity and water supply eviction", top_k=1)
    assert len(res_evict) > 0
    assert "Section 29" in res_evict[0]["section"]

    print("MAHARASHTRA RENTAL STATUTORY KNOWLEDGE BASE TESTS PASSED CLEANLY!")
    print(f"Total Statutes Pre-Indexed: {len(legal_kb.laws)}")

if __name__ == "__main__":
    test_legal_knowledge_base_retrieval()
