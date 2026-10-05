import os
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def generate_negotiation_email(
    analysis_data: Dict[str, Any],
    tone: str = "formal", # "polite", "formal", "legal_notice"
    recipient_name: str = "Landlord / Licensor",
    sender_name: str = "Tenant / Licensee",
    language: str = "English"
) -> Dict[str, str]:
    """
    Generates a formal, statutorily grounded negotiation email or legal notice
    addressed to the counterparty proposing safer redline amendments.
    """
    doc_name = analysis_data.get("document_name", "Agreement")
    doc_type = analysis_data.get("document_type", "Leave & License Agreement")
    clauses = analysis_data.get("analyzed_clauses", [])

    # Filter clauses with CRITICAL, HIGH, or MEDIUM risk
    flagged_clauses = [c for c in clauses if c.get("risk_level") in ["CRITICAL", "HIGH", "MEDIUM"]]
    if not flagged_clauses:
        flagged_clauses = clauses[:3]

    api_key = os.getenv("GEMINI_API_KEY", "").strip() or getattr(settings, "GEMINI_API_KEY", "").strip()
    
    # Format clause details for prompt
    clause_details_str = ""
    for idx, c in enumerate(flagged_clauses, 1):
        sec = c.get("section_number", idx)
        title = c.get("title", f"Clause {sec}")
        orig = c.get("original_text", "")
        reason = c.get("reason", "")
        explanation = c.get("legal_explanation", "")
        suggested = c.get("suggested_wording", "")
        clause_details_str += f"""
{idx}. Provision {sec}: {title}
- Original Text: "{orig}"
- Statutory Rationale: {reason} ({explanation})
- Proposed Counter-Wording: "{suggested}"
"""

    prompt = f"""
You are a senior Indian Legal Counsel specializing in contract negotiation and statutory compliance (MRCA 1999, TPA 1882, ICA 1872).

YOUR TASK: Write a highly professional, formal legal negotiation email / communication in {language}.

CONTEXT:
- Document Type: {doc_type}
- Subject Contract: {doc_name}
- Addressed To: {recipient_name}
- From: {sender_name}
- Selected Tone: {tone.upper()} (Options: POLITE = friendly & collaborative, FORMAL = structured corporate legal, LEGAL_NOTICE = authoritative advocate notice)
- Language: {language}

FLAGGED PROVISIONS REQUIRING AMENDMENT:
{clause_details_str}

GUIDELINES:
1. Subject Line: Must be clean, authoritative, and professional (e.g. "Proposed Statutory Amendments & Redline Review — {doc_type}").
2. Salutation: Formal legal salutation.
3. Introduction: Acknowledge receipt of the draft agreement politely and express intent to proceed once key statutory alignments are addressed.
4. Clause Counter-Proposals: List each flagged provision clearly with:
   - Specific Clause reference and Title
   - Concise statutory rationale under Indian law (referencing MRCA 1999, ICA 1872, or TPA 1882)
   - Proposed statutorily compliant counter-wording
5. Closing: Professional request for review and next steps, indicating attached redlined revised draft (.docx).
6. Do NOT use marketing fluff or emojis. Use clean, formal legal tone.

Return output strictly as a JSON object matching this schema:
{{
  "subject": "Clear Subject Line",
  "body": "Full body text formatted cleanly with line breaks"
}}
"""

    if HAS_GENAI and api_key and len(api_key) > 15 and "your_" not in api_key.lower():
        models_to_try = ["gemini-flash-latest", "gemini-3.6-flash", "gemini-3.5-flash"]
        for m_name in models_to_try:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=m_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                if response and response.text:
                    import json
                    parsed = json.loads(response.text)
                    if parsed.get("subject") and parsed.get("body"):
                        return {
                            "subject": parsed["subject"].strip(),
                            "body": parsed["body"].strip(),
                            "tone": tone
                        }
            except Exception as ex:
                logger.warning(f"Negotiation model {m_name} failed: {ex}")
                continue

    # Deterministic Rule-Based Fallback Generator
    subject = f"Proposed Statutory Compliance Amendments — {doc_type}"
    
    body = f"Dear {recipient_name},\n\n"
    body += f"Thank you for sharing the draft {doc_type} ({doc_name}) for review.\n\n"
    body += "Upon conducting a statutory compliance review under the Maharashtra Rent Control Act, 1999 and the Indian Contract Act, 1872, I would like to request a few standard amendments to align the instrument with mandatory legal provisions:\n\n"

    for idx, c in enumerate(flagged_clauses, 1):
        sec = c.get("section_number", idx)
        title = c.get("title", f"Clause {sec}")
        suggested = c.get("suggested_wording", c.get("original_text"))
        reason = c.get("reason", "Statutory alignment required.")
        
        body += f"{idx}. Clause {sec} ({title}):\n"
        body += f"   • Statutory Ground: {reason}\n"
        body += f"   • Proposed Counter-Wording: \"{suggested}\"\n\n"

    body += "I have attached the formal revised contract document (.docx) with tracked redline changes for your convenience. Please review and confirm if we can incorporate these updates.\n\n"
    body += f"Sincerely,\n{sender_name}"

    return {
        "subject": subject,
        "body": body,
        "tone": tone
    }
