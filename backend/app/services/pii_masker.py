import re
from typing import Dict, Any, List, Tuple

def mask_pii_content(text: str) -> Dict[str, Any]:
    masked_text = text
    mask_summary = {
        "persons": 0,
        "addresses": 0,
        "emails": 0,
        "phones": 0,
        "govt_ids": 0,
        "bank_details": 0,
        "organizations": 0
    }

    # 1. Mask Email Addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails_found = list(set([m.group(0) for m in re.finditer(email_pattern, masked_text)]))
    for idx, email in enumerate(emails_found, start=1):
        placeholder = f"[EMAIL_{idx}]"
        masked_text = masked_text.replace(email, placeholder)
        mask_summary["emails"] += 1

    # 2. Mask Phone Numbers
    phone_pattern = r'\b(?:\+?91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}\b|\b(?:\+?91[\-\s]?)?[6-9]\d{9}\b|\b0\d{2,4}[\-\s]?\d{6,8}\b'
    phones_found = list(set([m.group(0) for m in re.finditer(phone_pattern, masked_text)]))
    for idx, phone in enumerate(phones_found, start=1):
        placeholder = f"[PHONE_{idx}]"
        masked_text = masked_text.replace(phone, placeholder)
        mask_summary["phones"] += 1

    # 3. Mask Govt IDs (PAN Card & Aadhaar)
    pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
    aadhaar_pattern = r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}\b'
    
    pan_found = list(set([m.group(0) for m in re.finditer(pan_pattern, masked_text)]))
    for idx, pan in enumerate(pan_found, start=1):
        placeholder = f"[GOVT_ID_PAN_{idx}]"
        masked_text = masked_text.replace(pan, placeholder)
        mask_summary["govt_ids"] += 1

    aadhaar_found = list(set([m.group(0) for m in re.finditer(aadhaar_pattern, masked_text)]))
    for idx, aadhaar in enumerate(aadhaar_found, start=1):
        placeholder = f"[GOVT_ID_AADHAAR_{idx}]"
        masked_text = masked_text.replace(aadhaar, placeholder)
        mask_summary["govt_ids"] += 1

    # 4. Mask Bank Details (IFSC Code & Bank Account Numbers)
    ifsc_pattern = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
    bank_acc_pattern = r'(?:A/c|Account|Acc|A/C)\s*(?:No\.?)?\s*:?\s*\d{9,18}'

    ifsc_found = list(set([m.group(0) for m in re.finditer(ifsc_pattern, masked_text)]))
    for idx, ifsc in enumerate(ifsc_found, start=1):
        placeholder = f"[IFSC_CODE_{idx}]"
        masked_text = masked_text.replace(ifsc, placeholder)
        mask_summary["bank_details"] += 1

    acc_found = list(set([m.group(0) for m in re.finditer(bank_acc_pattern, masked_text, re.IGNORECASE)]))
    for idx, acc in enumerate(acc_found, start=1):
        placeholder = f"[BANK_ACCOUNT_{idx}]"
        masked_text = masked_text.replace(acc, placeholder)
        mask_summary["bank_details"] += 1

    # 5. Mask Organizations (Pvt Ltd, LLP, Private Limited, CHS)
    org_pattern = r'\b[A-Z][A-Za-z0-9\s\&]+(?:Pvt\.?\s*Ltd\.?|Private\s+Limited|LLP|Corporation|Inc\.?|CHS|Co-operative\s+Housing\s+Society)\b'
    orgs_found = list(set([m.group(0) for m in re.finditer(org_pattern, masked_text)]))
    for idx, org in enumerate(orgs_found, start=1):
        placeholder = f"[ORGANIZATION_{idx}]"
        masked_text = masked_text.replace(org, placeholder)
        mask_summary["organizations"] += 1

    # 6. Contextual Name Extraction
    person_patterns = [
        r'(?:Landlord|Lessor|Licensor|Tenant|Lessee|Licensee|Employer|Employee|Name)\s*[:/]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'between\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
    ]

    person_names = set()
    for pattern in person_patterns:
        for match in re.finditer(pattern, text):
            full_match = match.group(1) if match.groups() else match.group(0)
            if full_match and len(full_match.strip()) > 3:
                person_names.add(full_match.strip())

    for idx, name in enumerate(sorted(list(person_names)), start=1):
        placeholder = f"[PERSON_{idx}]"
        masked_text = re.sub(rf'\b{re.escape(name)}\b', placeholder, masked_text)
        mask_summary["persons"] += 1

    # 7. Contextual Address Redaction
    address_patterns = [
        r'residing\s+at\s+([^,\.\n]+(?:,[^,\.\n]+){1,3})',
        r'premises\s+(?:located\s+)?at\s+([^,\.\n]+(?:,[^,\.\n]+){1,3})',
        r'Address\s*:\s*([^,\.\n]+(?:,[^,\.\n]+){1,3})'
    ]

    address_count = 0
    for pattern in address_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            full_match = match.group(1) if match.groups() else match.group(0)
            if full_match and len(full_match.strip()) > 5:
                address_count += 1
                placeholder = f"[ADDRESS_{address_count}]"
                masked_text = masked_text.replace(full_match, placeholder)

    mask_summary["addresses"] = address_count

    return {
        "original_text": text,
        "masked_text": masked_text,
        "mask_summary": mask_summary,
        "total_items_masked": sum(mask_summary.values())
    }
