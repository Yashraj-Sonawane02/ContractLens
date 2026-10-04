import os
import json
import re
from typing import List, Dict, Any

LEGAL_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "legal_db", "maharashtra_rental_laws.json")

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

    def search_legal_context(self, query_text: str, topic: str = "", top_k: int = 2) -> List[Dict[str, Any]]:
        if not self.laws:
            return []

        query_words = set(re.findall(r'\w+', query_text.lower()))
        results = []

        for law in self.laws:
            score = 0
            content_lower = law["content"].lower()
            title_lower = law["title"].lower()
            act_lower = (law.get("act_name", "") + " " + law.get("act_short", "")).lower()
            sec_lower = law.get("section", "").lower()
            keywords = [k.lower() for k in law.get("keywords", [])]

            for word in query_words:
                if len(word) < 2:
                    continue
                if word in sec_lower or word == sec_lower.replace("section", "").strip():
                    score += 15
                if word in act_lower:
                    score += 5
                if any(word in k or k in word for k in keywords):
                    score += 5
                if word in title_lower:
                    score += 3
                if word in content_lower:
                    score += 1

            # Topic boost
            if topic and topic.lower() in law.get("domain", "").lower():
                score += 2

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
