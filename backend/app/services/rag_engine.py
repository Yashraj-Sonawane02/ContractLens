import os
import json
import time
import re
import logging
from typing import Dict, Any, List
from app.services.legal_knowledge_base import legal_kb
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def normalize_contract_text(text: str) -> str:
    """
    Normalizes contract text by converting to lowercase and stripping parenthetical spelled-out numbers.
    E.g. '7 (seven) days' -> '7 days', '60 (sixty) days' -> '60 days', 'Rs. 2,000/-' -> 'rs. 2,000'.
    """
    text_lower = text.lower()
    clean = re.sub(r'(\d+)\s*\([a-z\s\-]+\)', r'\1', text_lower)
    return clean

def classify_clause_risk_by_rules(clause: Dict[str, Any]) -> Dict[str, Any]:
    text = clause["text"]
    topic = clause.get("topic", "")
    text_lower = text.lower()
    norm_text = normalize_contract_text(text)

    # Default Rule: LOW RISK
    risk_level = "LOW"
    legal_status = "Statutorily Compliant"
    confidence = "High"
    reason = "Standard routine contractual covenant adhering to standard legal practice."
    explanation = "This provision aligns with customary contractual rights under the Transfer of Property Act, 1882 and Maharashtra Leave & License standards."
    simple_explanation = "This is a standard routine term commonly found in balanced rental agreements."
    recommendation = "No action required. Clause appears balanced and standard."
    suggested_wording = None

    # =========================================================================
    # RULE SET 0: PRO-LICENSEE / COMPLIANT WARRANTY EXEMPTIONS (LOW RISK)
    # =========================================================================
    is_pro_tenant_warranty = any(k in text_lower for k in [
        "sole and absolute owner", "represents and warrants that he is the sole owner",
        "quiet enjoyment", "peacefully hold and enjoy", "indemnify the licensee against any claim",
        "indemnify the licensee against any claim of any third party arising out of any defect in the title",
        "free from all encumbrances"
    ]) and not any(bad in text_lower for bad in ["cut off", "disconnect", "forfeit", "lock out", "sole discretion", "waive", "irrevocably waives"])

    if is_pro_tenant_warranty:
        risk_level = "LOW"
        reason = "Standard warranty of title and authority protecting the licensee."
        explanation = "This provision provides customary pro-licensee warranties of title, authority, and quiet enjoyment protecting against third-party claims."
        simple_explanation = "This standard term protects you by confirming the landlord actually owns the property and will cover you if any title dispute arises."
        recommendation = "No action required. Clause is pro-licensee."
        return {
            "clause_id": clause.get("clause_id"),
            "section_number": clause.get("section_number"),
            "title": clause.get("title"),
            "original_text": text,
            "topic": topic,
            "risk_level": risk_level,
            "legal_status": legal_status,
            "confidence_score": confidence,
            "reason": reason,
            "legal_explanation": explanation,
            "simple_explanation": simple_explanation,
            "relevant_statutes": legal_kb.search_legal_context(text, top_k=2),
            "recommendation": recommendation,
            "suggested_wording": None
        }

    # =========================================================================
    # RULE SET 1: CRITICAL RISK (Deduction: -20 Points)
    # =========================================================================
    
    # C1: Unlawful Essential Service / Utility Disconnection Threat (Sec 29 MRCA 1999)
    cut_off_keywords = ["cut off", "disconnect", "withhold", "stop supply", "interrupt", "suspend", "deactivate"]
    utility_keywords = ["water", "electricity", "power", "utility", "utilities", "amenities", "lift", "gas", "essential service"]
    is_negated_cut_off = any(n in norm_text for n in ["shall not disconnect", "not to disconnect", "shall not interfere", "not disconnect", "shall not cut off"])

    if any(k in norm_text for k in cut_off_keywords) and any(u in norm_text for u in utility_keywords) and not is_negated_cut_off:
        risk_level = "CRITICAL"
        reason = "Unlawful threat to cut off or disconnect essential water, electricity, or utility supplies."
        explanation = "Section 29 of the Maharashtra Rent Control Act, 1999 strictly prohibits landlords from cutting off, withholding, or interrupting essential water, electricity, or utility services under any circumstances, even during rent defaults."
        simple_explanation = "The contract threatens to cut off your electricity or water if there is a dispute. In Maharashtra, cutting off essential utilities is strictly illegal."
        recommendation = "Remove any reference to utility disconnection."
        suggested_wording = "The Licensor shall ensure continuous and uninterrupted access to essential utility services including electricity and water, in accordance with Section 29 of the Maharashtra Rent Control Act, 1999."

    # C2: Unconstitutional Court Waiver / Restraint of Proceedings (Sec 28 ICA 1872)
    elif any(k in norm_text for k in [
        "irrevocably waives all rights to approach any court", "waives court", "no right to approach court",
        "waives all rights to file any suit", "waives all rights to approach civil courts",
        "waives right to approach civil court", "waives right to file suit", "cannot file lawsuit",
        "shall not approach court", "restraint of legal proceedings", "decision of the licensor on any dispute shall be final"
    ]):
        risk_level = "CRITICAL"
        reason = "Unlawful total waiver of court access and restraint of legal proceedings."
        explanation = "Under Section 28 of the Indian Contract Act, 1872, agreements restricting a party from enforcing legal rights in ordinary courts are void."
        simple_explanation = "This clause tries to stop you from going to court. Under Indian law, clauses blocking court access are void."
        recommendation = "Remove court waiver clause and preserve access to civil courts."
        suggested_wording = "Any dispute arising out of this Agreement shall be submitted to the jurisdiction of competent civil courts in Maharashtra."

    # C3: Forcible Eviction / Unannounced Lock-out Entry (Sec 15 & 24 MRCA 1999, Sec 108 TPA 1882)
    elif any(k in norm_text for k in [
        "without recourse to any court", "change the locks", "forcibly evicted", "forcible eviction",
        "take forcible possession", "re-enter without court", "lock the premises"
    ]):
        risk_level = "CRITICAL"
        reason = "Illegal self-help eviction, changing locks, or forcible possession without court process."
        explanation = "Section 15 & 24 of the Maharashtra Rent Control Act, 1999 and Section 108 of the Transfer of Property Act, 1882 mandate due process of law. Landlords cannot take forcible possession or change locks without court orders."
        simple_explanation = "The landlord claims they can lock you out forcibly. Under Maharashtra law, landlords cannot forcibly evict anyone without proper court process."
        recommendation = "Remove self-help eviction terms."
        suggested_wording = "The Licensor may initiate legal eviction proceedings strictly in accordance with the Maharashtra Rent Control Act, 1999."

    # C4: Forfeiture of Deposit for Minor Breaches (Pets, Food, Nails, Key loss) (Sec 74 ICA 1872)
    elif (any(k in norm_text for k in ["pet", "nail", "wall mark", "guest stay", "key loss"]) and 
          any(k in norm_text for k in ["forfeit", "keep entire deposit", "confiscate", "deduct full deposit"])):
        risk_level = "CRITICAL"
        reason = "Forfeiture of full security deposit for minor lifestyle or technical infractions."
        explanation = "Under Section 74 of the Indian Contract Act, 1872, forfeiting an entire security deposit for minor infractions (like hanging picture frames or pet presence) is an oppressive, unenforceable penalty."
        simple_explanation = "The contract threatens to keep all your money for minor things like putting a nail in the wall. This is an excessive penalty under Indian law."
        recommendation = "Remove deposit forfeiture for minor technical breaches."
        suggested_wording = "The Licensee shall maintain the premises cleanly and repair any minor wall damage upon vacation."

    # =========================================================================
    # RULE SET 2: HIGH RISK (Deduction: -10 Points)
    # =========================================================================

    # H1: Sole Arbitrator Nominated Exclusively by Licensor (Sec 12(5) Arbitration Act 1996)
    elif (any(k in norm_text for k in [
        "appointed by the licensor alone", "solely appointed by the licensor", "sole arbitrator appointed by the licensor",
        "nominated exclusively by the licensor", "sole arbitrator nominated exclusively", "appointed by the licensor"
    ]) or ("sole arbitrator" in norm_text and "appointed by the licensor" in norm_text)) and not "mutually" in norm_text:
        risk_level = "HIGH"
        reason = "Unilateral appointment of sole arbitrator by licensor."
        explanation = "Unilateral nomination of a sole arbitrator by one party is legally invalid under Section 12(5) of the Arbitration & Conciliation Act 1996 and Supreme Court rulings (TRF Ltd & Perkins Eastman)."
        simple_explanation = "The landlord claims the right to pick their own sole judge for disputes. Under Indian law, arbitrators must be mutually agreed upon."
        recommendation = "Replace with mutual arbitrator appointment."
        suggested_wording = "Any dispute shall be referred to arbitration by a mutually agreed sole arbitrator."

    # H2: Unilateral Rent Hike at Sole Discretion (Sec 10 & 11 MRCA 1999)
    elif any(k in norm_text for k in [
        "sole discretion", "revise the license fee upward", "revise rent unilaterally",
        "increase rent at any time", "increase rent via notice", "unilateral rent escalation",
        "automatically escalate by 25%"
    ]) and any(w in norm_text for w in ["rent", "license fee", "fee", "escalat", "revise"]):
        risk_level = "HIGH"
        reason = "Unilateral rent escalation at licensor's sole discretion."
        explanation = "Under Section 10 & 11 of the Maharashtra Rent Control Act, 1999, rent increases cannot be made unilaterally at sole discretion without mutual consent."
        simple_explanation = "The landlord claims they can raise the rent whenever they want at their sole discretion. Rent increases must be capped and agreed in writing."
        recommendation = "Require written mutual consent for rent increases."
        suggested_wording = "Any revision in the License Fee shall be made strictly by mutual written consent of both parties."

    # H3: Asymmetric / One-Sided Notice Period (Sec 106 TPA 1882)
    elif ("notice" in norm_text or "terminate" in norm_text) and ("licensor" in norm_text and "licensee" in norm_text) and (
        ("15 days" in norm_text or "7 days" in norm_text or "14 days" in norm_text) and ("60 days" in norm_text or "90 days" in norm_text or "3 months" in norm_text)
    ):
        risk_level = "HIGH"
        reason = "Asymmetric notice period heavily favoring licensor."
        explanation = "Giving the licensor a short notice period (e.g. 7-15 days) while requiring the licensee to give a long notice period (e.g. 60–90 days) creates a severe contractual imbalance."
        simple_explanation = "The landlord can kick you out with short notice, but forces you to give 2–3 months notice. Notice periods should be equal for both parties."
        recommendation = "Standardize notice period equally (e.g. 30 days for both parties)."
        suggested_wording = "Either party may terminate this Agreement by giving thirty (30) days prior written notice to the other party."

    # H4: Exorbitant Daily Penalty (Sec 74 ICA 1872)
    elif any(k in norm_text for k in ["per day", "daily fine", "daily penalty", "per diem"]) and any(k in norm_text for k in ["2,000", "1,000", "2000", "1000", "rs 1000", "rs 2000", "rs. 1000", "rs. 2000", "₹1,000", "₹2,000"]):
        risk_level = "HIGH"
        reason = "Exorbitant daily penalty fine for delayed payments."
        explanation = "Under Section 74 of the Indian Contract Act, 1872, daily penalty fines of Rs 1,000–2,000 per day are unenforceable penalty clauses. Courts award only reasonable compensation."
        simple_explanation = "Charging a high daily fine for late rent is an unenforceable penalty under Indian contract law."
        recommendation = "Replace daily fines with reasonable annual interest."
        suggested_wording = "Delayed payments shall attract simple interest at 10% per annum for the actual days of delay."

    # H5: Deposit Forfeiture + Remaining Rent on Lock-in Exit (Sec 74 ICA 1872)
    elif ("lock-in" in norm_text or "lock in" in norm_text) and ("forfeit" in norm_text or "forfeiture" in norm_text) and any(k in norm_text for k in ["balance", "remaining", "in addition pay"]):
        risk_level = "HIGH"
        reason = "Entire deposit forfeiture plus full remaining rent penalty on early exit."
        explanation = "Under Section 74 of the Indian Contract Act 1872, forfeiting 100% of the deposit AND demanding remaining term rent for early exit is an unenforceable penalty."
        simple_explanation = "If you leave early, the landlord wants to keep your full deposit AND make you pay all remaining months. This double penalty is illegal."
        recommendation = "Cap early exit damages to 1 month's fee."
        suggested_wording = "In the event of early termination, licensee shall pay 1 month's license fee as reasonable compensation."

    # =========================================================================
    # RULE SET 3: MEDIUM RISK (Deduction: -4 Points)
    # =========================================================================

    # M1: Tax Gross-Up / Shifting Licensor's Net Tax (TDS / Income-Tax Act)
    elif any(k in norm_text for k in ["net of all taxes", "gross-up", "net of taxes", "full license fee net of"]):
        risk_level = "MEDIUM"
        reason = "Tax gross-up clause shifting licensor's income tax burden onto licensee."
        explanation = "Shifting the licensor's income-tax or TDS gross-up burden onto the licensee imposes unexpected tax liabilities."
        simple_explanation = "This clause requires you to pay extra money to cover the landlord's personal income taxes."
        recommendation = "Specify that licensee shall deduct TDS as required by law and licensor bears income tax."
        suggested_wording = "The Licensee shall deduct TDS from the License Fee as mandated by the Income-tax Act, and the Licensor shall bear all income tax liabilities."

    # M2: Discriminatory Food / Lifestyle Restrictions (Art 14 & ICA Sec 23)
    elif any(k in norm_text for k in ["non-vegetarian", "non vegetarian", "cooking of meat", "dietary restrictions", "eggs"]):
        risk_level = "MEDIUM"
        reason = "Discriminatory lifestyle or dietary restriction."
        explanation = "Restrictions on food habits or non-vegetarian cooking in residential tenancy contracts are legally questionable and overly restrictive."
        simple_explanation = "The contract restricts what food you can cook in your rented home."
        recommendation = "Remove food choice restrictions."
        suggested_wording = "The Licensee shall use the premises peacefully for residential purposes."

    # M3: Inspection Notice < 24 Hours / Invasive Access (Sec 108 TPA 1882)
    elif ("inspect" in norm_text or "inspection" in norm_text) and any(k in norm_text for k in [" 2 hours", "2-hour", "4 hours", "4-hour", "at any time of the day or night", "without prior notice", "without notice"]) and not "24 hours" in norm_text:
        risk_level = "MEDIUM"
        reason = "Invasive landlord inspection rights without adequate 24-hour notice."
        explanation = "Allowing inspection on very short notice (e.g. 2 hours) or at any time of night intrudes on the licensee's privacy and right to peaceful possession under Section 108 of TPA 1882."
        simple_explanation = "The landlord can enter on short 2-hour notice at any time. You should request 24 hours prior notice."
        recommendation = "Require 24 hours prior written notice for inspection."
        suggested_wording = "The Licensor may inspect the premises once a month between 10 a.m. and 6 p.m. upon giving 24 hours prior written notice."

    # M4: Unilateral Indemnity Covering Licensor's Own Negligence (Sec 124-125 ICA 1872)
    elif "indemnify" in norm_text and "licensor" in norm_text and any(k in norm_text for k in ["negligence of the licensor", "licensor's negligence", "omission or negligence of the licensor"]):
        risk_level = "MEDIUM"
        reason = "One-sided indemnity covering losses caused by licensor's own negligence."
        explanation = "Forcing the licensee to indemnify the licensor for losses caused by the licensor's own negligence or omission is an unreasonable contractual burden."
        simple_explanation = "This clause makes you pay for damages even if the landlord caused them by their own negligence."
        recommendation = "Limit indemnity to losses directly caused by licensee's default."
        suggested_wording = "The Licensee shall indemnify the Licensor only for direct losses caused by the Licensee's breach or negligence."

    # M5: Delayed Security Deposit Refund > 30 Days (ICA 1872)
    elif "deposit" in norm_text and any(k in norm_text for k in ["within 60 days", "within 90 days", "after 30 days", "refund after 30", "within 45 days"]):
        risk_level = "MEDIUM"
        reason = "Delayed security deposit refund terms beyond 30 days."
        explanation = "Security deposit refunds delayed beyond 30 days allow the licensor to hold tenant funds interest-free for an unreasonable duration."
        simple_explanation = "The landlord takes up to 60-90 days to return your deposit after you move out."
        recommendation = "Require deposit refund within 30 days or upon key handover."
        suggested_wording = "The Security Deposit shall be refunded within 30 days of handing over vacant possession."

    # M6: Fixed Non-Evidentiary Deductions from Deposit
    elif "deduct" in norm_text and any(k in norm_text for k in ["irrespective of the actual condition", "fixed sum", "irrespective of actual condition"]):
        risk_level = "MEDIUM"
        reason = "Mandatory fixed deposit deduction regardless of actual premises condition."
        explanation = "Deducting fixed sums (e.g. for painting) without proving actual damage or providing bills violates Section 74 of the Indian Contract Act."
        simple_explanation = "The landlord automatically deducts a flat fee from your deposit even if you return the flat spotless."
        recommendation = "Require deductions to be based on actual bills and damage beyond wear and tear."
        suggested_wording = "Deductions from the deposit shall be limited to actual documented repairs supported by bills, fair wear and tear excepted."

    # M7: Unreasonable Holding Over Rate (200%+) (Sec 74 ICA 1872)
    elif any(k in norm_text for k in ["holding over", "hold over"]) and any(k in norm_text for k in ["200%", "double fee", "double rate"]):
        risk_level = "MEDIUM"
        reason = "Elevated 200% holding over compensation rate for delay in vacating."
        explanation = "Imposing a 200% daily rate for holding over requires reasonable capping."
        simple_explanation = "Double daily rent applies if you fail to hand over keys immediately on expiry."
        recommendation = "Cap holding over compensation at 125% of daily rate."
        suggested_wording = "Holding over beyond expiry shall be charged at 125% of the pro-rata daily License Fee."

    # M8: Commercial Sharing / Monetization of Personal Data (DPDP Act 2023)
    elif ("personal data" in norm_text or "identity documents" in norm_text or "contact details" in norm_text) and any(k in norm_text for k in ["for any purpose", "sharing them with brokers", "third parties as the licensor thinks fit", "third-party advertisers", "monetize"]):
        risk_level = "MEDIUM"
        reason = "Unrestricted collection and third-party sharing of personal data."
        explanation = "Collecting identity documents for 'any purpose' and sharing with third parties violates purpose limitation under the Digital Personal Data Protection Act, 2023."
        simple_explanation = "The landlord claims the right to share or sell your personal details to third parties or brokers."
        recommendation = "Limit data usage strictly to police verification and agreement execution."
        suggested_wording = "Personal data shall be used strictly for police verification and legal compliance under this Agreement, and shall not be shared with third parties."

    # M9: Shifting Structural Repairs onto Licensee (MRCA Sec 13)
    elif "repair" in norm_text and any(k in norm_text for k in ["structural repair", "all repairs, replacements", "irrespective of cause or cost"]) and not "licensor shall bear" in norm_text:
        risk_level = "MEDIUM"
        reason = "Shifting landlord's structural repair duty onto licensee."
        explanation = "Under Section 13 of the Maharashtra Rent Control Act, 1999, structural repairs remain the statutory obligation of the landlord."
        simple_explanation = "The landlord shifts major structural repair costs onto you."
        recommendation = "Landlord must remain responsible for structural repairs."
        suggested_wording = "The Licensor shall be responsible for all major and structural repairs."

    # =========================================================================
    # RULE SET 4: ROUTINE / LOW RISK
    # =========================================================================
    else:
        risk_level = "LOW"
        reason = "Standard routine contractual covenant adhering to standard legal practice."
        explanation = "This provision aligns with customary contractual rights under the Transfer of Property Act, 1882 and Maharashtra Leave & License standards."
        simple_explanation = "This is a standard routine term commonly found in balanced rental agreements."
        recommendation = "No action required. Clause appears balanced and standard."

    return {
        "clause_id": clause.get("clause_id"),
        "section_number": clause.get("section_number"),
        "title": clause.get("title"),
        "original_text": text,
        "topic": topic,
        "risk_level": risk_level,
        "legal_status": legal_status,
        "confidence_score": confidence,
        "reason": reason,
        "legal_explanation": explanation,
        "simple_explanation": simple_explanation,
        "relevant_statutes": legal_kb.search_legal_context(text, top_k=2),
        "recommendation": recommendation,
        "suggested_wording": suggested_wording
    }

def analyze_clause_with_rag(clause: Dict[str, Any], language: str = "English") -> Dict[str, Any]:
    """
    Analyzes a contract clause using Retrieval-Augmented Generation (RAG) with Google Gemini LLM,
    grounded in Maharashtra statutory legal knowledge base (MRCA 1999, TPA 1882, ICA 1872, Arbitration Act 1996, DPDP Act 2023).
    Falls back gracefully to deterministic statutory rule engine if LLM API key is unavailable or fails.
    """
    text = clause.get("text", "")
    sec_num = clause.get("section_number", "")
    title = clause.get("title", "")

    # 1. RETRIEVAL STEP: Fetch relevant statutory context from Legal Knowledge Base
    retrieved_statutes = legal_kb.search_legal_context(text, top_k=3)
    kb_context_str = "\n".join([
        f"- {s.get('act_short')} {s.get('section')}: {s.get('title')} - {s.get('content_snippet')}"
        for s in retrieved_statutes
    ])

    # 2. Check for Gemini API key
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or getattr(settings, "GEMINI_API_KEY", "").strip()
    use_llm = HAS_GENAI and api_key and len(api_key) > 15 and "your_" not in api_key.lower()

    if use_llm:
        models_to_try = ["gemini-flash-latest", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash"]
        for m_name in models_to_try:
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""You are an expert Indian Property Lawyer specializing in Maharashtra Leave & License Agreements.
Analyze the following contract clause for statutory compliance and risk under Maharashtra property law.

CONTRACT CLAUSE TO ANALYZE:
Section Number: {sec_num}
Title: {title}
Clause Text: "{text}"

RETRIEVED STATUTORY LEGAL KNOWLEDGE BASE CONTEXT (Maharashtra Jurisdiction):
{kb_context_str}

RISK EVALUATION RUBRIC:
- CRITICAL: Essential utility disconnection threats (Sec 29 MRCA 1999), total waiver of court access (Sec 28 ICA 1872), self-help forcible eviction/changing locks, forfeiture of full deposit for minor breaches (pets, nails, guests).
- HIGH: Unilateral sole arbitrator appointed by licensor alone (Sec 12(5) Arbitration Act 1996), unilateral rent hike at sole discretion (Sec 10 MRCA), asymmetric notice periods (7-15d vs 60-90d), exorbitant daily penalty fines (Rs 1,000-2,000/day under Sec 74 ICA), deposit forfeiture PLUS remaining term rent for early exit.
- MEDIUM: Tax gross-up shifting licensor's income tax, discriminatory dietary restrictions (non-veg/eggs), inspection notice < 24 hrs, indemnity covering licensor's own negligence, delayed deposit refund beyond 30 days, flat unevidenced painting deductions, holding over rate > 125%, commercial personal data sharing (DPDP Act 2023), shifting landlord's structural repair duty.
- LOW: Standard routine balanced covenants adhering to Maharashtra Leave & License practices.

OUTPUT FORMAT:
Respond strictly with a JSON object:
{{
  "risk_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "reason": "Short 1-sentence concise reason for assigned risk level",
  "legal_explanation": "Detailed legal analysis referencing specific statutory sections",
  "simple_explanation": "Plain English explanation for non-lawyers",
  "recommendation": "Actionable advice to fix or negotiate",
  "suggested_wording": "Safer balanced alternative clause text"
}}
"""
                response = client.models.generate_content(
                    model=m_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )

                if response and response.text:
                    clean_json = response.text.strip()
                    if clean_json.startswith("```json"):
                        clean_json = clean_json[7:]
                    if clean_json.endswith("```"):
                        clean_json = clean_json[:-3]
                    clean_json = clean_json.strip()

                    parsed = json.loads(clean_json)

                    # Statutory rule verification & alignment
                    rule_res = classify_clause_risk_by_rules(clause)
                    final_risk = parsed.get("risk_level", rule_res["risk_level"]).upper()
                    if final_risk not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                        final_risk = rule_res["risk_level"]

                    return {
                        "clause_id": clause.get("clause_id"),
                        "section_number": sec_num,
                        "title": title,
                        "original_text": text,
                        "topic": clause.get("topic", "General"),
                        "risk_level": final_risk,
                        "legal_status": "Statutorily Non-Compliant" if final_risk != "LOW" else "Statutorily Compliant",
                        "confidence_score": 0.95,
                        "reason": parsed.get("reason") or rule_res["reason"],
                        "legal_explanation": parsed.get("legal_explanation") or rule_res["legal_explanation"],
                        "simple_explanation": parsed.get("simple_explanation") or rule_res["simple_explanation"],
                        "relevant_statutes": retrieved_statutes,
                        "recommendation": parsed.get("recommendation") or rule_res["recommendation"],
                        "suggested_wording": parsed.get("suggested_wording") or rule_res["suggested_wording"],
                        "analyzer_type": f"LLM_RAG_{m_name}"
                    }
            except Exception as ex:
                err_str = str(ex)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    logger.warning(f"LLM API quota/rate-limit hit ({m_name}). Using instant statutory rule engine.")
                    break
                logger.warning(f"LLM RAG model {m_name} error: {ex}. Retrying next model.")
                continue

    # FALLBACK: Deterministic statutory rule engine
    rule_result = classify_clause_risk_by_rules(clause)
    rule_result["analyzer_type"] = "Statutory_Rule_RAG"
    return rule_result
