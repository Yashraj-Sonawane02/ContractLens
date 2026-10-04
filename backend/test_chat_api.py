from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_contract_chat():
    clauses = [
        {
            "clause_id": "clause_1",
            "section_number": "1",
            "title": "Term of Agreement",
            "original_text": "This Agreement shall be valid for a period of eleven (11) months.",
            "topic": "General Obligations",
            "legal_explanation": "11-month Leave and License tenure.",
            "simple_explanation": "This agreement is valid for 11 months.",
            "recommendation": "Ensure agreement is registered under Section 55 MRCA.",
            "relevant_statutes": [
                {
                    "act_name": "Maharashtra Rent Control Act, 1999",
                    "section": "Section 55",
                    "key_legal_takeaway": "Mandatory registration of Leave & License agreements."
                }
            ]
        }
    ]

    # TEST 1: Direct Clause Query
    response1 = client.post(
        "/api/v1/chat/ask",
        json={"question": "explain clause 1 in detail", "analyzed_clauses": clauses}
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["status"] == "success"
    assert "Term of Agreement" in data1["answer"]
    assert "Section 55" in data1["answer"]

    # TEST 2: Multi-Turn Simplification Follow-Up Query
    history = [
        {"sender": "user", "text": "explain clause 1 in detail"},
        {"sender": "bot", "text": data1["answer"]}
    ]
    response2 = client.post(
        "/api/v1/chat/ask",
        json={"question": "can you make it more simplified", "analyzed_clauses": clauses, "conversation_history": history}
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert "Ultra-Simplified" in data2["answer"] or "Plain-English" in data2["answer"]
    assert "Term of Agreement" in data2["answer"]

    # TEST 3: Direct Statutory Act / Section 74 Query (must NOT match Clause 1)
    response3 = client.post(
        "/api/v1/chat/ask",
        json={"question": "Under Section 74 of the Indian Contract Act, 1872 explain this act in very simple language", "analyzed_clauses": clauses}
    )
    assert response3.status_code == 200
    data3 = response3.json()
    assert "Section 74" in data3["answer"]
    assert "Indian Contract Act" in data3["answer"]
    assert "RENTAL / LEAVE AND LICENCE AGREEMENT" not in data3["answer"]  # Correctly answered statutory act, not clause 1!

    # TEST 4: Capability & Identity Query
    response4 = client.post(
        "/api/v1/chat/ask",
        json={"question": "what this chatbot does", "analyzed_clauses": clauses}
    )
    assert response4.status_code == 200
    data4 = response4.json()
    assert "What ContractLens Statutory Legal Assistant Does" in data4["answer"]

    print("CONTRACT CHAT API ALL 4 MULTI-TURN INTENT TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    test_contract_chat()
