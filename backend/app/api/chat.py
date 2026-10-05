import os
import json
import re
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.legal_knowledge_base import legal_kb
from app.core.config import settings

logger = logging.getLogger(__name__)

# Try importing google genai SDK
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

router = APIRouter(prefix="/chat", tags=["Contract Chat Engine"])

class ChatRequest(BaseModel):
    question: str
    analyzed_clauses: Optional[List[Dict[str, Any]]] = []
    conversation_history: Optional[List[Dict[str, Any]]] = []
    language: Optional[str] = "English"

@router.post("/ask", response_model=Dict[str, Any])
def ask_contract_question(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    q_lower = question.lower().strip()
    clauses = request.analyzed_clauses or []
    history = request.conversation_history or []
    lang = (request.language or "English").strip()

    # =========================================================================
    # AI ENGINE: Gemini 2.0 Flash Contextual Statutory Legal Chat Assistant
    # =========================================================================
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or getattr(settings, "GEMINI_API_KEY", "").strip()
    if HAS_GENAI and api_key and len(api_key) > 15 and "your_" not in api_key.lower():
        try:
            client = genai.Client(api_key=api_key)

            # Build clauses summary context
            clauses_summary = ""
            for c in clauses[:30]:
                sec_num = c.get("section_number", "N/A")
                title = c.get("title", "Untitled Clause")
                risk = c.get("risk_level", "LOW")
                orig = c.get("original_text", "")
                reason = c.get("reason", "")
                explanation = c.get("legal_explanation", "")
                clauses_summary += f"\n- Clause {sec_num} ({title}) [Risk: {risk}]: \"{orig[:250]}\"\n  Finding: {reason}\n  Legal Analysis: {explanation}\n"

            # Build conversation history text
            history_text = ""
            if history:
                for h in history[-8:]:
                    sender = "User" if h.get("sender") == "user" else "Assistant"
                    history_text += f"\n{sender}: {h.get('text', '')}"

            # Query pre-indexed statutory knowledge base
            stat_matches = legal_kb.search_legal_context(question, top_k=3)
            stat_text = ""
            for sm in stat_matches:
                stat_text += f"\n- {sm['act_name']} ({sm['section']}) - {sm['title']}: {sm['key_legal_takeaway']}"

            system_prompt = f"""
You are **ContractLens Statutory Legal Assistant**, an expert Indian legal AI assistant grounded strictly in Indian Contract Law and Rent Control Acts (*Maharashtra Rent Control Act 1999*, *Transfer of Property Act 1882*, *Indian Contract Act 1872*).

YOUR TASK: Answer the user's question accurately and fluently in {lang}.

CONTEXT:
1. UPLOADED CONTRACT CLAUSES:
{clauses_summary if clauses_summary else "No specific contract uploaded."}

2. RELEVANT STATUTORY PROVISIONS:
{stat_text if stat_text else "No direct statutory matches found for this specific query."}

3. PREVIOUS CONVERSATION HISTORY:
{history_text if history_text else "First message in thread."}

STRICT ZERO-HALLUCINATION RULES:
- Answer ONLY using the provided statutory provisions and contract clauses above.
- Every cited section MUST be an authentic section from MRCA 1999, TPA 1882, or ICA 1872. Do NOT invent non-existent section numbers or court cases.
- If the question is completely unrelated to Indian contract/rental law or if the provided context lacks sufficient legal evidence, respond strictly with: "no grounded answer — The query cannot be answered using the verified Indian statutory database (MRCA 1999, TPA 1882, ICA 1872) or contract context."
"""

            models_to_try = ["gemini-flash-latest", "gemini-3.6-flash", "gemini-3.5-flash"]
            response = None
            for m_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=f"{system_prompt}\n\nUSER QUESTION: {question}"
                    )
                    if response and response.text:
                        break
                except Exception as ex:
                    logger.warning(f"Gemini model {m_name} failed: {ex}")
                    continue

            if response and response.text:
                ans_text = response.text.strip()
                # Verification Pass: Check for hallucinated section citations
                cited_sections = re.findall(r'(?:section|sec)\s*(\d+)', ans_text, re.IGNORECASE)
                valid_sec_nums = {re.sub(r'[^\d]', '', law['section']) for law in legal_kb.laws if law.get('section')}
                
                hallucinated = False
                for cs in cited_sections:
                    if cs not in valid_sec_nums and int(cs) > 200:
                        hallucinated = True
                        break

                if hallucinated:
                    ans_text = "no grounded answer — The query cited a statutory section not found in the verified Indian legal database."

                return {
                    "status": "success",
                    "question": question,
                    "matched_clause": None,
                    "answer": ans_text
                }
        except Exception as e:
            logger.warning(f"Gemini Chat API fallback to rule engine: {e}")

    # =========================================================================
    # FALLBACK ENGINE: Deterministic Intent Engine
    # =========================================================================
    # INTENT HANDLER 1: Conversational Greetings
    if re.search(r'^\s*(hi|hello|hey|greetings|good morning|good afternoon|good evening|namaste)\b', q_lower):
        return {
            "status": "success",
            "question": question,
            "matched_clause": None,
            "answer": (
                "Greetings! I am your **ContractLens Statutory Legal Assistant**.\n\n"
                "I can analyze and explain any provision in your uploaded contract or Indian statutory law. Try asking:\n"
                "- *'Explain Clause 10 in detail'*\n"
                "- *'Can you make it more simplified?'*\n"
                "- *'Explain Section 74 of the Indian Contract Act in simple terms'*\n"
                "- *'Is the late payment per-day fine legal under Maharashtra law?'*"
            )
        }

    # INTENT HANDLER 2: User Identity & Profile Queries
    if re.search(r'\b(who am i|who is logged in|my profile|user info|who are you|who created you|your name|identity)\b', q_lower):
        return {
            "status": "success",
            "question": question,
            "matched_clause": None,
            "answer": (
                "I am **ContractLens Statutory Legal Assistant**, an automated AI legal compliance engine built specifically for Indian Contract Law and Rent Control Acts (*MRCA 1999*, *TPA 1882*, *ICA 1872*).\n\n"
                "I evaluate your contract covenants against mandatory statutory rights, flag oppressive penalties or illegal clauses, and provide plain-language legal guidance with DPDP Act 2023 privacy redacting."
            )
        }

    # INTENT HANDLER 3: Platform Help & Capability Queries
    if re.search(r'\b(what (this|the|an|a|ai)?\s*(chatbot|assistant|ai|engine)?\s*(does|can|do|help)|how to use|what can you do|what is this|capabilities|features)\b', q_lower):
        return {
            "status": "success",
            "question": question,
            "matched_clause": None,
            "answer": (
                "### What ContractLens Statutory Legal Assistant Does:\n\n"
                "1. **Statutory Risk Audit**: Evaluates contractual covenants against mandatory provisions of Indian legislation (*Maharashtra Rent Control Act 1999*, *Transfer of Property Act 1882*, *Indian Contract Act 1872*).\n"
                "2. **Specific Clause Analysis**: Ask *'Explain Clause 4'* or *'Check maintenance terms'* to get statutory breakdown and balanced re-drafts.\n"
                "3. **Direct Statutory Act Lookup**: Ask about Indian laws directly (e.g. *'Under Section 74 of Indian Contract Act, explain penalties'*).\n"
                "4. **Multi-Turn Context & Simplification**: Ask *'Can you make it more simplified?'* or *'What is the legal remedy?'* to get plain-English breakdowns.\n"
                "5. **DPDP Act Privacy Shield**: Redacts personal names, emails, Aadhaar/PAN IDs locally before cloud processing."
            )
        }

    # INTENT HANDLER 4: Direct Statutory Act / Section Query
    stat_results = legal_kb.search_legal_context(question, top_k=2)
    if stat_results and ("section" in q_lower or "act" in q_lower or "law" in q_lower):
        top_stat = stat_results[0]
        answer = (
            f"### 🏛️ Statutory Breakdown: **{top_stat['act_name']} ({top_stat['section']})**\n\n"
            f"📜 **Official Title**: *{top_stat['title']}*\n\n"
            f"💡 **Plain-Language Legal Explanation**:\n{top_stat['key_legal_takeaway']}\n\n"
            f"📖 **Statutory Provisions & Content**:\n\"{top_stat['content']}\"\n\n"
            f"⚖️ **Legal Enforceability & Application**:\n"
            f"Under Indian law ({top_stat['jurisdiction']}), any contractual stipulation that violates **{top_stat['section']}** of the **{top_stat['act_short']}** is legally invalid and unenforceable under Section 23 of the Indian Contract Act."
        )
        return {
            "status": "success",
            "question": question,
            "matched_clause": None,
            "answer": answer
        }

    # INTENT HANDLER 5: Simplification / ELI5 / Follow-Up Intent
    is_simplification_query = bool(re.search(
        r'\b(simplif\w*|simple|easier|plain english|explain simpler|like i\'m 5|eli5|make it easy|more detail|tell me more|in simple language)\b', 
        q_lower
    ))

    if is_simplification_query:
        target_clause = None
        if history:
            for msg in reversed(history):
                if msg.get("sender") == "bot":
                    text = msg.get("text", "")
                    sec_match = re.search(r'(?:Section|Clause)\s*(\d+)', text, re.IGNORECASE)
                    if sec_match:
                        num = sec_match.group(1)
                        for c in clauses:
                            if str(c.get("section_number")) == num or str(c.get("clause_id")) == f"clause_{num}":
                                target_clause = c
                                break
                    if target_clause:
                        break

        if not target_clause and clauses:
            crit_clauses = [c for c in clauses if c.get("risk_level") in ["CRITICAL", "HIGH"]]
            target_clause = crit_clauses[0] if crit_clauses else clauses[0]

        if target_clause:
            answer = (
                f"### 💡 Ultra-Simplified Plain-English Breakdown for **{target_clause.get('title')}** (Section {target_clause.get('section_number')})\n\n"
                f"1. 📌 **What it means in simple terms**:\n"
                f"   {target_clause.get('simple_explanation', target_clause.get('original_text'))}\n\n"
                f"2. ⚠️ **Why you should care (The Risk)**:\n"
                f"   {target_clause.get('reason', 'Contains restrictive or imbalanced obligations.')}\n\n"
                f"3. 🛡️ **What you should do (Your Action)**:\n"
                f"   {target_clause.get('recommendation', 'Ask the landlord for a balanced, statutorily compliant clause.')}"
            )
            return {
                "status": "success",
                "question": question,
                "matched_clause": target_clause.get("title"),
                "answer": answer
            }

    # INTENT HANDLER 6: Explicit Clause Matching & Keyword Search
    matched_clause = None
    clause_match = re.search(r'\b(?:clause|sec|section)\s*(\d+)\b', q_lower)
    if clause_match:
        target_num = clause_match.group(1)
        for c in clauses:
            sec_num = str(c.get("section_number") or "").strip(".: ")
            clause_id = str(c.get("clause_id") or "")
            title_text = str(c.get("title") or "").lower()
            if (sec_num == target_num or clause_id == f"clause_{target_num}" or re.search(rf'\bclause\s*{target_num}\b', title_text)):
                matched_clause = c
                break

    if matched_clause:
        answer = (
            f"### Detailed Explanation for **{matched_clause['title']}** (Section {matched_clause['section_number']})\n\n"
            f"📜 **Contract Clause Text**:\n\"{matched_clause['original_text']}\"\n\n"
            f"⚖️ **Legal Assessment**: {matched_clause['legal_explanation']}\n\n"
            f"💡 **Plain-Language Summary**: {matched_clause['simple_explanation']}\n\n"
            f"👉 **Action Recommendation**: {matched_clause['recommendation']}"
        )
    else:
        stat_str = ""
        for s in stat_results[:2]:
            stat_str += f"\n- **{s['act_name']} {s['section']}**: {s['key_legal_takeaway']}"
        answer = (
            f"Based on your contract analysis and Indian Legal Statutory database:\n\n"
            f"Your contract contains {len(clauses)} clauses. Related statutory provisions:\n{stat_str if stat_str else '- Transfer of Property Act 1882 & Maharashtra Rent Control Act 1999'}\n\n"
            f"For specific commitments, ask about any specific clause (e.g., 'Explain Clause 4') or statutory act."
        )

    return {
        "status": "success",
        "question": question,
        "matched_clause": matched_clause["title"] if matched_clause else None,
        "answer": answer
    }

