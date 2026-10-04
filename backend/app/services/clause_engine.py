import re
from typing import Dict, Any, List

TOPIC_PATTERNS = {
    "Rent & License Fee": [r"\brent\b", r"\blicense fee\b", r"\bmonthly payment\b", r"\bpayable\b"],
    "Security Deposit": [r"\bsecurity deposit\b", r"\bdeposit\b", r"\brefund\b", r"\bforfeiture?\b"],
    "Lock-in & Notice Period": [r"\block-?in\b", r"\bnotice period\b", r"\bterminate\b", r"\btermination\b", r"\bvacate\b"],
    "Penalty & Interest": [r"\bpenalty\b", r"\binterest\b", r"\bdelayed payment\b", r"\bdefault\b", r"\bper day\b"],
    "Sub-letting & Assignment": [r"\bsub-?let\b", r"\bassign\b", r"\btransfer\b", r"\bthird party\b"],
    "Maintenance & Repairs": [r"\bmaintenance\b", r"\brepair\b", r"\bdamage\b", r"\belectricity\b", r"\bwater\b"],
    "Dispute & Jurisdiction": [r"\bjurisdiction\b", r"\bcourts\b", r"\barbitration\b", r"\bdispute\b", r"\bmumbai\b"],
    "General Obligations": [r"\bpremises\b", r"\bpurpose\b", r"\bresidential\b", r"\bcompliance\b"]
}

RAG_TRIGGER_KEYWORDS = [
    "penalty", "forfeit", "interest", "lock-in", "eviction", "non-refundable",
    "unilateral", "damage", "indemnify", "without notice", "deduct", "breach"
]

def classify_clause_topic(text: str) -> str:
    text_lower = text.lower()
    scores = {}
    
    for topic, patterns in TOPIC_PATTERNS.items():
        score = 0
        for pattern in patterns:
            score += len(re.findall(pattern, text_lower))
        scores[topic] = score

    sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_topic, max_score = sorted_topics[0]
    
    return best_topic if max_score > 0 else "General Obligations"

def triage_clause(text: str) -> str:
    """Stage-1 Fast Triage tagging clause as routine vs flagged_for_rag."""
    text_lower = text.lower()
    for trigger in RAG_TRIGGER_KEYWORDS:
        if trigger in text_lower:
            return "flagged_for_rag"
    return "routine"

def segment_clauses(text: str) -> List[Dict[str, Any]]:
    # Split text by numbered headings, Clause/Section/Article prefixes, or capitalized headings
    split_pattern = r'\n+(?=(?:Clause|Section|Article|\d+[\.\)]|\b[A-Z\s]{4,}\b)\s*)'
    raw_blocks = re.split(split_pattern, text)
    
    # Fallback to double newline split if regex split produced too few blocks
    if len(raw_blocks) < 3:
        raw_blocks = re.split(r'\n\s*\n', text)

    clauses = []
    clause_counter = 1

    for block in raw_blocks:
        clean_block = block.strip()
        if not clean_block or len(clean_block) < 15:
            continue

        lines = [l.strip() for l in clean_block.split('\n') if l.strip()]
        if not lines:
            continue

        header_line = lines[0]

        # Extract title and section number
        sec_num_match = re.search(r'^(?:Clause|Section|Article|\d+[\.\)]?)\s*(\d+(?:\.\d+)?|\b[A-Z\s]+\b)?', header_line, re.IGNORECASE)
        if sec_num_match and sec_num_match.group(1):
            section_number = sec_num_match.group(1)
        else:
            section_number = str(clause_counter)

        # Clean title
        title = header_line
        if len(title) > 60:
            title = title[:57] + "..."

        topic = classify_clause_topic(clean_block)
        triage_status = triage_clause(clean_block)

        clauses.append({
            "clause_id": f"clause_{clause_counter}",
            "section_number": section_number,
            "title": title,
            "text": clean_block,
            "topic": topic,
            "triage_status": triage_status
        })
        clause_counter += 1

    return clauses
