from app.services.document_parser import process_document
from app.services.pii_masker import mask_pii_content
from app.services.clause_engine import segment_clauses
from app.services.parallel_analyzer import analyze_full_contract_parallel
import asyncio

CONTRACT_TEXT = """
RENTAL / LEAVE AND LICENCE AGREEMENT
(Leave and Licence Agreement under Section 52, Transfer of Property Act, 1882)
Executed on Non-Judicial Stamp Paper of Rs. 500/-
Stamp Duty: Rs. 500 | Registration No.: REG/MH/2024/00987 | Date of Registration: 01-April-2024
THIS RENTAL AGREEMENT is made and entered into at Mumbai, Maharashtra, on this 1st day of April, 2024, by and between:

LICENSOR / LANDLORD:
Ramesh Subramaniam Iyer
Aadhaar No.: 4729 8821 3045
PAN: ABCPI1234D
Address: Flat No. 302, Sunrise Apartments, Andheri West, Mumbai - 400053
Mobile: +91-98201-45678
Email: ramesh.iyer@gmail.com

LICENSEE / TENANT:
Priya Mehta
Aadhaar No.: 6523 4410 9871
PAN: BCDPM5678E
Address: 14-B, Rose Garden CHS, Borivali East, Mumbai - 400066
Mobile: +91-91234-56789
Email: priya.mehta@outlook.com

PROPERTY DETAILS:
Property Address: Flat No. 502, Wing B, Skyline Heights, Malad West, Mumbai - 400064

TERMS AND CONDITIONS

Clause 1: Term of Agreement
This Agreement shall be valid for a period of eleven (11) months, commencing from 01-April-2024 and expiring on 28-February-2025, unless renewed by mutual written consent of both Parties before the expiry date.

Clause 2: Monthly Licence Fee (Rent)
The Licensee agrees to pay a monthly licence fee of Rs. 22,000/- (Rupees Twenty-Two Thousand Only) to the Licensor on or before the 5th day of each calendar month.

Clause 3: Security Deposit
The Licensee has paid a refundable interest-free security deposit of Rs. 66,000/- (Rupees Sixty-Six Thousand Only) to the Licensor. The deposit shall be refunded within 30 days of vacation of the premises.

Clause 4: Maintenance Charges
The Licensee shall bear monthly society maintenance charges of Rs. 2,500/- directly payable to Skyline Heights Co-operative Housing Society. Electricity and piped gas bills shall be borne by the Licensee.

Clause 5: Use of Premises
The Licensee shall use the premises exclusively for residential purposes only.

Clause 6: Quiet Enjoyment
The Licensor covenants that the Licensee shall peaceably hold and enjoy the premises during the term of this Agreement without any interruption from the Licensor.

Clause 7: Inventory and Fixtures
An inventory of fixtures, fittings, and furnishings is annexed hereto as Schedule A.

Clause 8: Right to Inspect
The Licensor or the Licensor's authorised representative shall have the right to inspect the premises with a minimum notice of 48 hours.

Clause 9: Rent Escalation
The monthly licence fee shall be subject to an automatic escalation of 10% per annum upon each renewal. The Licensor reserves the sole and unilateral right to revise the rent at any time during the agreement period upon giving 15 days written notice, without requiring concurrence of the Licensee.

Clause 10: Lock-in Period and Premature Termination
This Agreement contains a mandatory lock-in period of six (6) months. Should the Licensee vacate before expiry of the lock-in period, the Licensee shall forfeit the entire security deposit of Rs. 66,000/- as liquidated damages. Additionally, the Licensee shall pay rent for the remaining lock-in period as a penalty.

Clause 11: Sub-letting and Assignment
The Licensee shall not sub-let, assign, or part with possession of the whole or any part of the premises to any third party.

Clause 12: Guests and Occupants
No person other than the Licensee and immediate family members shall reside in the premises. Any guest staying beyond 7 consecutive days must be intimated to the Licensor in writing.

Clause 13: Pets
Keeping of pets of any kind is strictly prohibited in the premises. Any violation shall entitle the Licensor to terminate with immediate effect and forfeit the security deposit in full.

Clause 14: Alterations and Improvements
The Licensee shall not make any alterations or improvements to the premises without prior written consent.

Clause 15: Dispute Resolution
The Licensee hereby irrevocably waives any right to approach any court, tribunal, consumer forum, or any quasi-judicial authority for any dispute arising out of this Agreement. All disputes shall be resolved exclusively by an arbitrator solely appointed by the Licensor, whose decision shall be final and binding.

Clause 16: Entry and Possession
Notwithstanding any other provision of this Agreement, the Licensor reserves the unconditional right to enter, take possession of, and lock the premises at any time, including in the Licensee's absence, without prior notice, if the Licensor suspects any misuse, non-payment, or breach.

Clause 17: Forfeiture of Deposit
The Licensor shall be entitled to forfeit the entire security deposit of Rs. 66,000/- upon any breach of this Agreement, howsoever minor, including but not limited to: late payment of even one day, failure to intimate a guest, presence of any pet, any wall-hanging or nail-work on walls.

Clause 18: Dietary and Lifestyle Restrictions
The Licensee shall not cook, store, or consume non-vegetarian food, eggs, alcohol, or any intoxicant within the premises. The Licensor reserves the right to conduct surprise inspections of the kitchen and refrigerator at any time without prior notice.

Clause 19: Tenant Data and Surveillance
The Licensee hereby grants the Licensor irrevocable consent to: (a) install CCTV cameras in the common areas and inside the premises including bedrooms; (b) access and retain Aadhaar biometric data, PAN details, bank statements; (c) share such data with any third party.

Clause 20: Rent Revision During Tenancy
The Licensor reserves the absolute right to increase the monthly rent by any amount, at any point during the agreement period, by sending a WhatsApp message to the Licensee's registered mobile number.

Clause 21: Renewal and Notice Period
This Agreement shall automatically renew for successive periods of 11 months unless the Licensee provides written notice of at least 90 days. The Licensor, however, may terminate this Agreement at any time with only 7 days notice.

Clause 22: Holdover and Eviction
Any occupancy beyond the agreed period shall be treated as illegal trespass, and the Licensor shall be entitled to file a criminal complaint and have the Licensee forcibly evicted through police assistance, bypassing the civil court process entirely.

Clause 23: Governing Law
This Agreement shall be governed by and construed in accordance with the laws of India, including the Transfer of Property Act, 1882 and Maharashtra Rent Control Act, 1999.
"""

async def main():
    # 1. PII Redaction
    pii_res = mask_pii_content(CONTRACT_TEXT)
    print("=== 1. PII REDACTION VERIFICATION ===")
    print(f"Total PII Entities Masked: {pii_res['total_items_masked']}")
    print(f"Mask Summary: {pii_res['mask_summary']}")
    assert "ramesh.iyer@gmail.com" not in pii_res["masked_text"]
    assert "ABCPI1234D" not in pii_res["masked_text"]
    assert "+91-98201-45678" not in pii_res["masked_text"]
    assert "Rs. 22,000" in pii_res["masked_text"]
    assert "Rs. 66,000" in pii_res["masked_text"]

    # 2. Clause Segmentation
    clauses = segment_clauses(pii_res["masked_text"])
    print(f"\n=== 2. CLAUSE SEGMENTATION VERIFICATION ===")
    print(f"Total Clauses Segmented: {len(clauses)}")
    assert len(clauses) >= 20

    # 3. Full Statutory RAG Analysis
    analysis = await analyze_full_contract_parallel(clauses, language="English")
    print(f"\n=== 3. RAG ANALYSIS & HEALTH SCORE VERIFICATION ===")
    print(f"Contract Health Score: {analysis['health_score']}/100")
    print(f"Risk Breakdown: {analysis['risk_summary']}")
    print(f"Execution Latency: {analysis['processing_time_seconds']} seconds")

    print("\n=== TOP FLAGGED STATUTORY RISKS ===")
    for c in analysis["analyzed_clauses"]:
        if c["risk_level"] in ["CRITICAL", "HIGH"]:
            print(f"\n[{c['risk_level']}] {c['title']} (Sec {c['section_number']})")
            print(f" - Reason: {c['reason']}")
            print(f" - Simple Explanation: {c['simple_explanation']}")
            if c["relevant_statutes"]:
                print(f" - Statutory Citation: {c['relevant_statutes'][0]['act_name']} {c['relevant_statutes'][0]['section']}")

if __name__ == "__main__":
    asyncio.run(main())
