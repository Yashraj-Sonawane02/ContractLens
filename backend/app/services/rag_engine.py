import time
import re
from typing import Dict, Any, List
from app.services.legal_knowledge_base import legal_kb

def classify_clause_risk_by_rules(clause: Dict[str, Any]) -> Dict[str, Any]:
    text = clause["text"]
    topic = clause["topic"]
    text_lower = text.lower()

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
    # RULE SET 1: CRITICAL RISK (Deduction: -20 Points)
    # =========================================================================
    
    # C1: Unlawful Essential Service / Utility Disconnection Threat (Sec 29 MRCA 1999)
    cut_off_keywords = ["cut off", "disconnect", "withhold", "stop supply", "interrupt", "suspend"]
    utility_keywords = ["water", "electricity", "power", "utility", "utilities", "amenities", "lift", "gas", "essential service"]
    if any(k in text_lower for k in cut_off_keywords) and any(u in text_lower for u in utility_keywords):
        risk_level = "CRITICAL"
        reason = "Unlawful threat to cut off or disconnect essential water, electricity, or utility supplies."
        explanation = "Section 29 of the Maharashtra Rent Control Act, 1999 strictly prohibits landlords from cutting off, withholding, or interrupting essential water, electricity, or utility services under any circumstances, even during rent defaults."
        simple_explanation = "The contract threatens to cut off your electricity or water if there is a dispute. In Maharashtra, cutting off essential utilities is strictly illegal."
        recommendation = "Remove any reference to utility disconnection."
        suggested_wording = "The Licensor shall ensure continuous and uninterrupted access to essential utility services including electricity and water, in accordance with Section 29 of the Maharashtra Rent Control Act, 1999."

    # C2: Unconstitutional Court Waiver or Sole Arbitrator (Sec 28 ICA 1872)
    elif any(k in text_lower for k in [
        "waives any right to approach any court", "waives court", "no right to approach court",
        "solely appointed by the licensor", "solely appointed by the landlord", "sole arbitrator appointed by",
        "unilateral arbitrator", "waives all rights to challenge", "cannot file lawsuit", "shall not approach court"
    ]):
        risk_level = "CRITICAL"
        reason = "Unlawful total waiver of court access and unilateral sole arbitrator appointment."
        explanation = "Under Section 28 of the Indian Contract Act, 1872, agreements restricting a party from enforcing legal rights in ordinary courts are void. Unilateral appointment of a sole arbitrator violates Supreme Court precedents (TRF Ltd & Perkins Eastman)."
        simple_explanation = "This clause tries to stop you from going to court and lets the landlord pick their own sole judge. Under Indian law, blocking court access or picking a one-sided arbitrator is void."
        recommendation = "Replace with a mutual arbitration clause or standard civil court jurisdiction."
        suggested_wording = "Any dispute arising out of this Agreement shall be referred to arbitration by a mutually agreed sole arbitrator, or submitted to competent civil courts in Mumbai."

    # C3: Forcible Eviction / Unannounced Lock-out Entry (Sec 15 & 24 MRCA 1999, Sec 108 TPA 1882)
    elif any(k in text_lower for k in [
        "lock the premises", "forcibly evicted", "forcible eviction", "take forcible possession",
        "change the locks", "re-enter without court", "without prior notice"
    ]) and any(k in text_lower for k in ["enter", "possess", "lock", "evict", "premises"]):
        risk_level = "CRITICAL"
        reason = "Illegal self-help eviction, changing locks, or unannounced entry without court process."
        explanation = "Section 15 & 24 of the Maharashtra Rent Control Act, 1999 and Section 108 of the Transfer of Property Act, 1882 mandate due process of law. Landlords cannot take forcible possession, change locks, or enter without notice."
        simple_explanation = "The landlord claims they can lock you out or enter without notice. Under Maharashtra law, landlords cannot forcibly evict anyone without proper court process."
        recommendation = "Require minimum 48 hours notice for entry and remove self-help eviction terms."
        suggested_wording = "The Licensor may inspect the premises upon providing at least 48 hours prior written notice to the Licensee at reasonable working hours."

    # C4: Invasive CCTV Surveillance / Bedroom Intrusion / Privacy Breach (Art 21 & DPDP Act 2023)
    elif any(k in text_lower for k in [
        "cctv inside", "camera inside", "bedroom camera", "surveillance inside", "biometric data share", "financial credentials share"
    ]):
        risk_level = "CRITICAL"
        reason = "Severe violation of privacy rights via bedroom surveillance or coerced personal data sharing."
        explanation = "Installing CCTV cameras inside private residential areas or coercively sharing personal financial/biometric data violates Article 21 Right to Privacy and the Digital Personal Data Protection Act, 2023."
        simple_explanation = "This clause allows installing cameras inside private rooms or sharing your personal bank data. This is a severe violation of your legal privacy rights."
        recommendation = "Remove CCTV inside private residential quarters and restrict tenant data sharing."
        suggested_wording = "Tenant personal verification data shall be used strictly for police verification and kept confidential in accordance with data privacy laws."

    # C5: Forfeiture of Deposit for Minor Breaches (Pets, Food, Nails, Key loss) (Sec 74 ICA 1872)
    elif (any(k in text_lower for k in ["pet", "non-vegetarian", "dietary", "nail", "wall mark", "guest stay", "key loss"]) and 
          any(k in text_lower for k in ["forfeit", "keep entire deposit", "confiscate", "deduct full deposit"])):
        risk_level = "CRITICAL"
        reason = "Forfeiture of full security deposit for minor lifestyle or technical infractions."
        explanation = "Under Section 74 of the Indian Contract Act, 1872, forfeiting an entire security deposit for minor infractions (like hanging picture frames or pet presence) is an oppressive, unenforceable penalty."
        simple_explanation = "The contract threatens to keep all your money for minor things like putting a nail in the wall or having a pet. This is an excessive penalty under Indian law."
        recommendation = "Remove deposit forfeiture for minor technical breaches."
        suggested_wording = "The Licensee shall maintain the premises cleanly and repair any minor wall damage upon vacation."

    # =========================================================================
    # RULE SET 2: HIGH RISK (Deduction: -10 Points)
    # =========================================================================

    # H1: Exorbitant Daily Penalty / High Delayed Payment Interest (>= ₹500/day or >= 12% p.a.) (Sec 74 ICA 1872)
    elif (any(k in text_lower for k in ["per day", "daily fine", "daily penalty", "per diem", "₹500", "₹1,000", "₹2,000", "rs 500", "rs 1000", "rs 2000", "rs. 500", "rs. 1000", "rs. 2000"]) or
          ("interest" in text_lower and any(rate in text for rate in ["12%", "15%", "18%", "24%", "36%"]))):
        risk_level = "HIGH"
        if any(k in text_lower for k in ["₹2,000", "rs. 2,000", "rs 2000", "2000 per day"]):
            risk_level = "CRITICAL"

        reason = "Extremely high daily penalty fine or exorbitant interest rate on delayed payments."
        explanation = "Under Section 74 of the Indian Contract Act, 1872, contractual stipulations imposing oppressive daily fines or excessive interest rates are treated as unenforceable penalties. Courts award only reasonable compensation for actual loss suffered."
        simple_explanation = "This clause charges a very high daily extra fee if rent is slightly delayed. Indian law does not allow landlords to charge extreme fines—they can only claim reasonable actual losses."
        recommendation = "Cap interest for delayed payment at a reasonable rate (e.g. 10% per annum) and remove per-day fines."
        suggested_wording = "The Licensee shall pay interest at the rate of 10% per annum on any delayed license fee for the actual period of delay, subject to applicable Indian law."

    # H2: Total Security Deposit Forfeiture during Lock-in (Sec 74 ICA 1872)
    elif ("lock-in" in text_lower or "lock in" in text_lower) and any(k in text_lower for k in ["forfeit", "liquidated damages", "keep deposit", "entire deposit"]):
        risk_level = "HIGH"
        if "entire" in text_lower or "full deposit" in text_lower or "100%" in text_lower:
            risk_level = "CRITICAL"

        reason = "Total security deposit forfeiture and heavy penalty during lock-in period exit."
        explanation = "Under Section 74 of the Indian Contract Act, 1872, forfeiting 100% of a large security deposit without proving equivalent actual rental loss is legally objectionable as an excessive penalty."
        simple_explanation = "If you leave early during lock-in, the landlord wants to keep your entire deposit. Under law, they can only deduct actual lost rent while finding a new tenant."
        recommendation = "Limit early termination damages to actual loss of rent up to a maximum of 1 month's fee."
        suggested_wording = "In the event of early exit during the lock-in period, the Licensee shall compensate the Licensor for actual loss of rent up to a maximum of one (1) month's license fee, after which the balance security deposit shall be refunded."

    # H3: Unilateral / Uncapped Rent Escalation (Sec 10 & 11 MRCA 1999)
    elif any(k in text_lower for k in [
        "rent escalation", "rent revision", "increase rent at any time", "revise rent unilaterally",
        "increase rent via whatsapp", "increase rent via notice", "unilateral rent"
    ]):
        risk_level = "HIGH"
        reason = "Unilateral rent escalation or unnegotiated rent increase during tenure."
        explanation = "Under Section 10 & 11 of the Maharashtra Rent Control Act, 1999, rent increases are capped at 4% per annum for residential premises unless structural improvements are made with concurrence."
        simple_explanation = "The landlord claims they can raise the rent at any point by sending a message. In Maharashtra, rent increases are regulated and require mutual agreement."
        recommendation = "Fix rent escalation at a standard mutual rate (e.g., 5% upon renewal)."
        suggested_wording = "The monthly licence fee shall remain fixed during the term, and any escalation upon renewal shall be mutually agreed upon in writing up to a maximum of 5%."

    # H4: Severe Notice Period Imbalance (Sec 106 & 108 TPA 1882)
    elif (any(k in text_lower for k in ["90 days", "3 months", "60 days", "2 months"]) and any(k in text_lower for k in ["7 days", "15 days", "1 week"])) or "notice imbalance" in text_lower:
        risk_level = "HIGH"
        reason = "Severe notice period imbalance restricting tenant termination rights."
        explanation = "Requiring 90 days / 3 months notice from tenant while allowing landlord only 7 to 15 days notice violates Section 106 & 108 of the Transfer of Property Act, 1882 regarding balanced termination covenants."
        simple_explanation = "You must give 3 months notice to leave, but the landlord can ask you to leave in 7 days. This notice period is very unfair."
        recommendation = "Establish a balanced 30-day notice period for both parties."
        suggested_wording = "Either party may terminate this Agreement by serving thirty (30) days prior written notice to the other party."

    # H5: Broad Tenant Indemnity Overreach (Sec 108 TPA 1882)
    elif "indemnify" in text_lower and any(k in text_lower for k in ["all losses", "building damage", "structural", "third party", "force majeure", "fire"]):
        risk_level = "HIGH"
        reason = "Overbroad indemnity clause shifting landlord structural and building risks to tenant."
        explanation = "Under Section 108 of the Transfer of Property Act, 1882, the lessor (landlord) is responsible for maintaining structural integrity and building insurance. Forcing the tenant to indemnify against structural or natural disaster losses is inequitable."
        simple_explanation = "This clause makes you pay for building damage, fires, or structural problems that are the landlord's responsibility."
        recommendation = "Limit tenant indemnity strictly to tenant's own willful misconduct or gross negligence."
        suggested_wording = "The Licensee shall indemnify the Licensor only against direct loss or damage caused to the premises due to the Licensee's proven willful misconduct or gross negligence."

    # =========================================================================
    # RULE SET 3: MEDIUM RISK (Deduction: -4 Points)
    # =========================================================================

    # M1: Restrictive Sub-letting & Assignment Bans (Sec 108(j) TPA 1882)
    elif any(k in text_lower for k in ["sub-let", "sublet", "assign", "transfer possession", "third party guest"]):
        risk_level = "MEDIUM"
        reason = "Restrictive guest or sub-letting covenant requiring prior written permission."
        explanation = "Standard restrictive covenant under Section 108(j) of the Transfer of Property Act, 1882 requiring landlord consent for sub-letting or transferring occupation rights."
        simple_explanation = "This clause limits sub-letting or hosting long-term guests without landlord permission."
        recommendation = "Ensure reasonable guest permissions for immediate family members."
        suggested_wording = "The Licensee shall not sub-let or assign the premises to any third party without the Licensor's prior written consent, except for temporary visits by immediate family members."

    # M2: Maintenance & Repair Responsibility Ambiguity (Sec 108(m) TPA 1882)
    elif any(k in text_lower for k in ["structural repair", "major repair", "plumbing", "painting", "society maintenance"]):
        risk_level = "MEDIUM"
        reason = "Potential ambiguity regarding major structural repair responsibilities."
        explanation = "Under Section 108(m) of the Transfer of Property Act, 1882, tenants are responsible for minor tenantable repairs while landlords remain responsible for major structural repairs and wear-and-tear."
        simple_explanation = "This clause deals with repairs. Major structural or pipe repairs should be paid by the landlord, while minor day-to-day repairs are paid by you."
        recommendation = "Clarify that major repairs exceeding ₹2,000 are borne by the Licensor."
        suggested_wording = "Minor routine repairs up to ₹2,000 shall be borne by the Licensee, while major structural, plumbing, and electrical repairs shall be promptly rectified by the Licensor."

    # M3: Short Inspection Notice Timeline
    elif "inspect" in text_lower or "entry" in text_lower or "visit" in text_lower:
        risk_level = "MEDIUM"
        reason = "Inspection covenant requiring adequate advance notification."
        explanation = "Under standard tenancy laws, landlord inspection rights must be bounded by reasonable prior notice (minimum 24-48 hours) during normal daytime hours."
        simple_explanation = "The landlord can visit to inspect the flat, but should give you reasonable advance notice first."
        recommendation = "Ensure inspection window is restricted to daytime hours with 24 hours notice."
        suggested_wording = "The Licensor or authorized representatives may inspect the premises upon providing at least 24 hours prior written notice during reasonable daytime hours."

    # M4: Extended Security Deposit Refund Timeline (>30 days)
    elif "deposit" in text_lower and any(k in text_lower for k in ["45 days", "60 days", "90 days", "2 months"]):
        risk_level = "MEDIUM"
        reason = "Extended timeline for security deposit refund after agreement expiry."
        explanation = "Holding security deposits beyond 15–30 days post-vacating without valid damage claims is customarily unreasonable."
        simple_explanation = "The landlord wants up to 45–60 days to return your deposit after you vacate. Standard practice is return within 7–15 days."
        recommendation = "Request deposit refund within 7 to 15 days of key handover."
        suggested_wording = "The security deposit shall be refunded to the Licensee within seven (7) business days of handing over vacant peaceful possession of the premises."

    return {
        "clause_id": clause["clause_id"],
        "section_number": clause["section_number"],
        "title": clause["title"],
        "original_text": text,
        "topic": topic,
        "risk_level": risk_level,
        "legal_status": legal_status,
        "confidence": confidence,
        "reason": reason,
        "legal_explanation": explanation,
        "simple_explanation": simple_explanation,
        "relevant_statutes": legal_kb.search_legal_context(text, topic=topic, top_k=2),
        "recommendation": recommendation,
        "suggested_wording": suggested_wording
    }

from app.services.translator import translate_clause_analysis

def analyze_clause_with_rag(clause: Dict[str, Any], language: str = "English") -> Dict[str, Any]:
    base_result = classify_clause_risk_by_rules(clause)
    if language and language.lower() != "english":
        return translate_clause_analysis(base_result, target_language=language)
    return base_result
