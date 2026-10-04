from app.services.pii_masker import mask_pii_content

def test_maharashtra_rental_pii_masking():
    sample_text = """
LEAVE AND LICENSE AGREEMENT

This Leave and License Agreement is executed in Mumbai on 10th February 2026 between:
Licensor: Ramesh Sharma, residing at 12 Bandra West, Mumbai 400050. Email: ramesh.sharma@example.com, Phone: +919820123456, PAN: ABCDE1234F.
Licensee: Suresh Verma, residing at 45 Andheri East, Mumbai 400069. Email: suresh.v@example.com, Phone: 9819876543, Aadhaar: 1234 5678 9012.

1. LICENSED PREMISES
The Licensor grants license to the Licensee for Flat No 501, Sea View Apartments, Bandra West, Mumbai.

2. LICENSE FEE AND SECURITY DEPOSIT
The Licensee shall pay a monthly license fee of ₹55,000 per month.
The Licensee has paid an interest-free Security Deposit of ₹2,000,000.

3. LOCK-IN PERIOD AND TERMINATION
The Agreement has a lock-in period of 6 months. Either party may terminate by giving 30 days notice.
Any delayed payment attracts 18% annual interest and ₹2,000 daily penalty.
"""
    result = mask_pii_content(sample_text)
    masked = result["masked_text"]
    summary = result["mask_summary"]

    # Assert PII is redacted
    assert "ramesh.sharma@example.com" not in masked
    assert "+919820123456" not in masked
    assert "ABCDE1234F" not in masked
    assert "[EMAIL_1]" in masked or "[EMAIL_2]" in masked
    assert "[PHONE_1]" in masked
    assert "[GOVT_ID_PAN_1]" in masked

    # Assert Legal & Financial metrics remain preserved
    assert "₹55,000" in masked
    assert "₹2,000,000" in masked
    assert "18%" in masked
    assert "30 days" in masked
    assert "6 months" in masked

    print("MAHARASHTRA RENTAL PII MASKING TESTS PASSED CLEANLY!")
    print(f"Masked Summary: {summary}")

if __name__ == "__main__":
    test_maharashtra_rental_pii_masking()
