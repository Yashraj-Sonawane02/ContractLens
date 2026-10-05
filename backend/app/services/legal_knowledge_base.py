import os
import json
import re
from typing import List, Dict, Any

LEGAL_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "legal_db", "maharashtra_rental_laws.json")

# Generic party words that shouldn't skew specific statutory matching
GENERIC_TERMS = {"licensor", "licensee", "tenant", "landlord", "premises", "agreement", "contract", "shall", "party", "parties"}

class LegalKnowledgeBase:
    def __init__(self, db_path: str = LEGAL_DB_PATH):
        self.db_path = db_path
        self.laws: List[Dict[str, Any]] = []
        self.load_knowledge_base()

    def load_knowledge_base(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.laws = json.load(f)
        else:
            self.laws = []

    def search_legal_context(self, query_text: str, topic: str = "", top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.laws:
            return []

        query_lower = query_text.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        results = []

        # Extract explicit section numbers mentioned in query e.g. "Section 29", "Sec 11", "74"
        sec_matches = set(re.findall(r'(?:section|sec|calum|kalam|kalum)?\s*(\d+)', query_lower))

        for law in self.laws:
            score = 0
            content_lower = law["content"].lower()
            title_lower = law["title"].lower()
            act_lower = (law.get("act_name", "") + " " + law.get("act_short", "")).lower()
            sec_lower = law.get("section", "").lower()
            sec_num = re.sub(r'[^\d]', '', sec_lower)
            keywords = [k.lower() for k in law.get("keywords", [])]

            # Direct section number match (Highest Priority: +40)
            if sec_num and sec_num in sec_matches:
                score += 40

            for word in query_words:
                if len(word) < 2:
                    continue
                
                # Filter out generic party words from giving massive boosts
                if word in GENERIC_TERMS:
                    score += 1
                    continue

                if word in sec_lower:
                    score += 15
                if word in act_lower:
                    score += 5

                # Keyword match weighting
                for k in keywords:
                    if k in GENERIC_TERMS:
                        continue
                    if word == k or (len(word) > 3 and word in k):
                        score += 12
                    elif k in word:
                        score += 8

                if word in title_lower:
                    score += 6
                if word in content_lower:
                    score += 2

            # Exact keyword phrase match boost
            for k in keywords:
                if k not in GENERIC_TERMS and k in query_lower:
                    score += 20

            # Topic boost
            if topic and topic.lower() in law.get("domain", "").lower():
                score += 4

            if score > 0:
                results.append({
                    "score": score,
                    "id": law["id"],
                    "act_name": law["act_name"],
                    "act_short": law["act_short"],
                    "section": law["section"],
                    "title": law["title"],
                    "jurisdiction": law["jurisdiction"],
                    "content": law["content"],
                    "key_legal_takeaway": law["key_legal_takeaway"]
                })

        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

# Global instance for instant <5ms lookups
legal_kb = LegalKnowledgeBase()
