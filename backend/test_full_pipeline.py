from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_analysis_pipeline():
    sample_maharashtra_contract = """
LEAVE AND LICENSE AGREEMENT

This Leave and License Agreement is executed in Mumbai on 15th January 2026 between:
Licensor: Ramesh Sharma, residing at 12 Bandra West, Mumbai. Email: ramesh@example.com, Phone: +919820123456.
Licensee: Suresh Verma, residing at 45 Andheri East, Mumbai. Email: suresh@example.com, Phone: 9819876543.

1. LICENSED PREMISES
The Licensor agrees to license Flat No 302, Green Acres, Bandra West, Mumbai to the Licensee for residential use.

2. LICENSE FEE AND SECURITY DEPOSIT
The Licensee shall pay a monthly license fee of ₹55,000 per month.
The Licensee has paid an interest-free Security Deposit of ₹2,000,000.

3. LOCK-IN PERIOD AND TERMINATION
This agreement has a strict lock-in period of 12 months. If the Licensee exits early, the entire Security Deposit shall be forfeited.

4. DELAYED PAYMENT PENALTY
Any delayed payment attracts a penalty of ₹2,000 per day of delay and interest of 18% per annum.

5. ESSENTIAL UTILITIES
If the Licensee delays payment for more than 7 days, the Licensor reserves the right to cut off electricity and water supply without notice.
"""

    response = client.post(
        "/api/v1/analysis/run",
        data={"raw_text": sample_maharashtra_contract, "language": "English", "domains": '["rental_property"]'}
    )

    assert response.status_code == 200
    data = response.json()

    print("Risk Summary Breakdown:", data["risk_summary"])
    assert data["status"] == "success"
    assert data["health_score"] < 70
    assert data["risk_summary"]["critical"] >= 1
    assert data["processing_time_seconds"] < 2.0

    print("FULL PIPELINE END-TO-END RAG ANALYSIS TESTS PASSED CLEANLY!")
    print(f"Health Score: {data['health_score']}/100")
    print(f"Execution Speed: {data['processing_time_seconds']} seconds")

if __name__ == "__main__":
    test_full_analysis_pipeline()
