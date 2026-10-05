import re
from typing import Dict, Any

SUPPORTED_RENTAL_PATTERNS = [
    r"\brent(al)?\b", r"\blease\b", r"\blicensee\b", r"\blicensor\b", r"\blandlord\b",
    r"\blessor\b", r"\blessee\b", r"\btenant\b", r"\bsecurity deposit\b", r"\bpremises\b",
    r"\bleave and license\b", r"\bmaharashtra rent control\b", r"\bflat\b", r"\bapartment\b",
    r"\bdemised property\b", r"\bmonthly fee\b", r"\block-in\b", r"\beviction\b", r"\bstatutory\b",
    r"\btransfer of property\b", r"\bindian contract act\b", r"\bstamp duty\b", r"\bsublet\b"
]

UNSUPPORTED_DOMAINS = {
    "Medical & Healthcare Report": [r"\bdoctor\b", r"\bpatient\b", r"\bhospital\b", r"\bdiagnosis\b", r"\bprescription\b", r"\bmedical\b"],
    "Financial Invoice / Receipt": [r"\binvoice\b", r"\bvat\b", r"\bgst\b", r"\bbill to\b", r"\bpayment receipt\b", r"\btax invoice\b"],
    "Software & Programming Code": [r"\bfunction\b", r"\bimport\b", r"\bconst\b", r"\bclass\b", r"\bdef\b", r"\breturn\b", r"\bvar\b"],
    "Resume / Curriculum Vitae": [r"\bresume\b", r"\bcurriculum vitae\b", r"\beducation\b", r"\bwork experience\b", r"\bskills\b"],
    "Unrelated Non-Legal Document": [r"\brecipe\b", r"\bnovel\b", r"\bstory\b", r"\bweather\b", r"\bnews\b"]
}

def detect_document_type(text: str) -> Dict[str, Any]:
    text_lower = text.lower()

    # 1. Check for Unsupported Non-Contract Domains
    for domain_name, patterns in UNSUPPORTED_DOMAINS.items():
        domain_matches = sum(len(re.findall(p, text_lower)) for p in patterns)
        if domain_matches >= 3 and not any(re.search(p, text_lower) for p in [r"\brent\b", r"\blease\b", r"\blicensee\b"]):
            return {
                "detected_type": domain_name,
                "is_supported_domain": False,
                "confidence": "high",
                "error_message": f"Unsupported Document Domain ({domain_name}): ContractLens is exclusively engineered for Maharashtra Leave & License Agreements, Leases, and Property Contracts under Indian Law. This file cannot be audited."
            }

    # 2. Check for Supported Rental & Property Legal Keywords
    rental_score = sum(len(re.findall(p, text_lower)) for p in SUPPORTED_RENTAL_PATTERNS)

    if rental_score >= 3:
        return {
            "detected_type": "Maharashtra Leave & License / Property Agreement",
            "is_supported_domain": True,
            "confidence": "high",
            "score": rental_score
        }
    elif rental_score >= 1:
        return {
            "detected_type": "General Property Contract",
            "is_supported_domain": True,
            "confidence": "medium",
            "score": rental_score
        }
    else:
        # Zero or insufficient rental contract keywords — Refuse Analysis
        return {
            "detected_type": "Invalid / Non-Contract Document",
            "is_supported_domain": False,
            "confidence": "low",
            "error_message": "Unsupported Document Domain: ContractLens is exclusively engineered for Maharashtra Leave & License Agreements, Residential/Commercial Leases, and Property Agreements under Indian Law. The uploaded document lacks contract covenants and cannot be audited."
        }
