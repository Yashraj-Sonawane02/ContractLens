import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.services.clause_engine import segment_clauses
from app.services.rag_engine import classify_clause_risk_by_rules

test_sample = """
1. Utility Provision: In the event of non-payment of rent for 5 days, the Licensor shall disconnect electricity and cut off water supply to the premises without further notice.
2. Legal Remedies Waiver: The Licensee waives any right to approach any court of law and agrees that any dispute shall be decided by a sole arbitrator solely appointed by the licensor.
3. Locks and Re-entry: The Licensor reserves the right to lock the premises and forcibly evict the licensee without prior notice upon breach.
4. Late Payment Penalty: A late fee penalty of Rs. 2000 per day shall be charged for delayed rent, along with 18% per annum interest.
5. Lock-in Period Exit: If tenant leaves during 12-month lock-in period, tenant shall forfeit entire security deposit of Rs 66,000.
6. Rent Escalation: The landlord reserves the right to revise rent unilaterally via WhatsApp message at any time.
7. Notice Period: Tenant must provide 90 days notice before vacating, while landlord may terminate with 7 days notice.
8. Sub-letting Restriction: The Licensee shall not sub-let or assign the premises to any third party without written consent.
9. Major Repairs: Major structural repairs shall be reported to the Licensor for maintenance.
10. Rent Payment Due: Monthly rent of Rs. 25,000 must be paid before 5th of every month via bank transfer.
"""

def test_risk_classification():
    print("==================================================")
    print("TESTING DETERMINISTIC STATUTORY RISK CLASSIFICATION")
    print("==================================================")
    
    clauses = segment_clauses(test_sample)
    print(f"Segmented Total Clauses: {len(clauses)}\n")

    for c in clauses:
        evaluated = classify_clause_risk_by_rules(c)
        print(f"[{evaluated['risk_level']}] {evaluated['section_number']}: {evaluated['title']}")
        print(f"   Reason: {evaluated['reason']}")
        print(f"   Statute: {evaluated['legal_explanation'][:100]}...")
        print("-" * 50)

if __name__ == "__main__":
    test_risk_classification()
