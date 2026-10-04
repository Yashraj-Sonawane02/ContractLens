import re
from typing import Dict, Any

DOCUMENT_PATTERNS = {
    "Rental & Lease Agreement": [
        r"\brent(al)?\b", r"\blease\b", r"\blandlord\b", r"\blessor\b", r"\blessee\b",
        r"\btenant\b", r"\bsecurity deposit\b", r"\bpremises\b", r"\bdemised property\b"
    ],
    "Employment & HR Agreement": [
        r"\bemployment\b", r"\bemployer\b", r"\bemployee\b", r"\bsalary\b", r"\bcompensation\b",
        r"\bprobation\b", r"\bnon-compete\b", r"\bappointment letter\b", r"\bnotice period\b"
    ],
    "Loan & Financial Agreement": [
        r"\bloan\b", r"\bborrower\b", r"\blender\b", r"\bpromissory note\b", r"\binterest rate\b",
        r"\bprincipal amount\b", r"\bcollateral\b", r"\bemi\b", r"\bfinancial facility\b"
    ],
    "Business & Commercial Contract": [
        r"\bnon-disclosure\b", r"\bnda\b", r"\bvendor\b", r"\bservice agreement\b", r"\bpartnership\b",
        r"\bindemnity\b", r"\bconfidential information\b", r"\bstatement of work\b", r"\bsow\b"
    ],
    "Consumer & E-Commerce Terms": [
        r"\bterms of service\b", r"\bterms of use\b", r"\bprivacy policy\b", r"\bconsumer\b",
        r"\brefund policy\b", r"\buser account\b", r"\be-commerce\b", r"\bend user\b"
    ]
}

def detect_document_type(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    scores = {doc_type: 0 for doc_type in DOCUMENT_PATTERNS}

    for doc_type, patterns in DOCUMENT_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            scores[doc_type] += len(matches)

    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_match, max_score = sorted_types[0]

    if max_score == 0:
        best_match = "General Legal Contract"
        confidence = "low"
    elif max_score >= 5:
        confidence = "high"
    else:
        confidence = "medium"

    return {
        "detected_type": best_match,
        "confidence": confidence,
        "scores": scores
    }
