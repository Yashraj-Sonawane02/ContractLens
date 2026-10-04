import os
import json
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Modern Google GenAI SDK Client
try:
    from google import genai
    from google.genai import types
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False

SYSTEM_PROMPT = """
You are LeagLease V2, an expert AI Legal Document Intelligence System specialized in Indian Law, specifically Maharashtra Rental & Property Laws (Maharashtra Rent Control Act 1999, Transfer of Property Act 1882, Indian Contract Act 1872).

Your task is to analyze a given contract clause using ONLY the provided statutory legal context.

STRICT LAWS & RULES:
1. Do NOT invent or hallucinate non-existent laws, sections, or court cases.
2. If the provided statutory legal evidence does not support a finding, respond with legal_status: "Insufficient legal evidence".
3. Evaluate risk based strictly on statutory provisions (e.g. Section 74 Indian Contract Act for unreasonable penalties/deposit forfeitures; Section 29 Maharashtra Rent Control Act for utility cutoffs; Section 55 MRCA for registration).
4. Provide structured JSON output matching the requested schema exactly.
"""

def evaluate_clause_with_gemini(
    clause_text: str,
    topic: str,
    statutory_context: List[Dict[str, Any]],
    language: str = "English"
) -> Optional[Dict[str, Any]]:
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or getattr(settings, "GEMINI_API_KEY", "").strip()
    
    # Instant validation guardrail: Return None if no real API key configured
    if not api_key or "your_" in api_key.lower() or len(api_key) < 15 or not HAS_GENAI_SDK:
        return None

    # Format statutory context string
    statute_str = ""
    for s in statutory_context:
        statute_str += f"- [{s['act_name']} {s['section']}] {s['title']}: {s['content']}\n  Key Takeaway: {s['key_legal_takeaway']}\n\n"

    user_prompt = f"""
{SYSTEM_PROMPT}

TARGET OUTPUT LANGUAGE: {language}

CLAUSE TO ANALYZE:
"{clause_text}"

CLAUSE TOPIC: {topic}

RETRIEVED STATUTORY LEGAL EVIDENCE:
{statute_str if statute_str else "No direct statutory context found for this topic."}

Return a valid JSON object matching this schema:
{{
  "risk_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "legal_status": "No obvious issue" | "Potentially risky" | "Insufficient legal evidence",
  "confidence": "High" | "Medium" | "Low",
  "reason": "Short summary of statutory concern",
  "legal_explanation": "Detailed technical analysis referencing specific statutory sections",
  "simple_explanation": "Simple plain-language explanation for non-lawyers ('Explain Like I'm Not a Lawyer')",
  "recommendation": "Practical recommendation",
  "suggested_wording": "Safer alternative clause wording"
}}
"""

    models_to_try = ["gemini-flash-latest", "gemini-3.6-flash", "gemini-3.5-flash"]
    response = None
    for m_name in models_to_try:
        try:
            client = genai.Client(api_key=api_key)
            res = client.models.generate_content(
                model=m_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            if res and res.text:
                response = res
                break
        except Exception as ex:
            logger.warning(f"Gemini RAG model {m_name} failed: {ex}")
            continue

    if response and response.text:
        try:
            result_json = json.loads(response.text)
            return result_json
        except Exception as err:
            logger.warning(f"Failed to parse Gemini RAG JSON output: {err}")

    except Exception as e:
        logger.warning(f"Gemini API evaluation fallback triggered due to: {e}")
        return None

    return None
