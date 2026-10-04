from app.services.document_parser import process_document

def test_txt_contract_extraction():
    sample_text = """
RENTAL AGREEMENT

This Rent Agreement is executed on 15th January 2026 at Mumbai between:
Landlord: Ramesh Kumar, residing at 12 Bandra West, Mumbai.
Tenant: Suresh Verma, residing at 45 Andheri East, Mumbai.

1. DEMISED PREMISES
The Landlord agrees to let out Flat No 302, Green Acres, Mumbai to the Tenant.

2. RENT AND SECURITY DEPOSIT
The monthly rent shall be ₹45,000 per month payable on or before the 5th of each month.
The Tenant has deposited a refundable Security Deposit of ₹1,50,000.

3. INTEREST AND PENALTY
Any delayed rent payment shall attract an interest rate of 12% per annum and a penalty of ₹1,000 per day of delay.

4. NOTICE PERIOD AND TERMINATION
Either party may terminate this agreement by giving 60 days notice in writing.
"""
    file_bytes = sample_text.encode('utf-8')
    result = process_document("sample_rental_agreement.txt", file_bytes)

    assert result["file_name"] == "sample_rental_agreement.txt"
    assert result["document_type_info"]["detected_type"] == "Rental & Lease Agreement"
    assert "₹45,000" in result["extracted_metrics"]["monetary_amounts"] or "₹1,50,000" in result["extracted_metrics"]["monetary_amounts"]
    assert "12%" in result["extracted_metrics"]["percentages"]
    assert len(result["sections"]) >= 3
    print("DOCUMENT PROCESSING & CLASSIFICATION TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    test_txt_contract_extraction()
