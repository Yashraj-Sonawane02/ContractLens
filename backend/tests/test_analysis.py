import pytest

VALID_MAHARASHTRA_LEASE = """
RESIDENTIAL LEAVE AND LICENSE AGREEMENT
Executed at Mumbai, Maharashtra under Maharashtra Rent Control Act 1999.
Licensor grants licensee premises for 11 months at Rs 25,000 monthly fee.
If licensee delays rent by 5 days, licensor reserves right to cut off water and electricity.
"""

UNSUPPORTED_MEDICAL_REPORT = """
PATIENT MEDICAL EXAMINATION REPORT
Hospital: Lilavati Hospital, Mumbai
Patient: Rajesh Shah
Diagnosis: Acute Viral Bronchitis. Prescribed Amoxicillin 500mg.
"""

def test_unsupported_domain_refusal(client):
    response = client.post(
        "/api/v1/analysis/run",
        data={
            "raw_text": UNSUPPORTED_MEDICAL_REPORT,
            "language": "English",
            "domains": '["rental_property"]'
        }
    )
    assert response.status_code == 422
    assert "unsupported document domain" in response.json()["detail"].lower()

def test_contract_analysis_and_history(client):
    # 1. Register & Login
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Advocate Priya Sharma", "email": "priya@mumbailaw.in", "password": "Password123!"}
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "priya@mumbailaw.in", "password": "Password123!"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Run Contract Analysis
    res = client.post(
        "/api/v1/analysis/run",
        data={
            "raw_text": VALID_MAHARASHTRA_LEASE,
            "language": "English",
            "domains": '["rental_property"]'
        },
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "analyzed_clauses" in data
    assert data["storage_metadata"]["encrypted"] is True

    # 3. Retrieve History for Logged in User
    hist_res = client.get("/api/v1/analysis/history", headers=headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) > 0
    assert "Maharashtra" in history[0]["document_type"] or "Leave & License" in history[0]["document_type"]

    # 4. Delete History Record
    record_id = history[0]["id"]
    del_res = client.delete(f"/api/v1/analysis/history/{record_id}", headers=headers)
    assert del_res.status_code == 200

    # 5. Verify Record Deleted
    hist_res2 = client.get("/api/v1/analysis/history", headers=headers)
    assert len(hist_res2.json()) == 0
