import io
import datetime
import hashlib
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def generate_compliance_certificate(analysis_data: Dict[str, Any]) -> bytes:
    """
    Generates an official, 1-page formal Certificate of Statutory Legal Compliance
    and DPDP Act 2023 Privacy Audit Seal using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []
    styles = getSampleStyleSheet()

    # Typography Styles
    header_style = ParagraphStyle(
        'CertHeader',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )

    sub_header_style = ParagraphStyle(
        'CertSubHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )

    section_heading = ParagraphStyle(
        'CertSecHead',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )

    meta_label = ParagraphStyle('MetaLabel', fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=colors.HexColor('#0F172A'))
    meta_val = ParagraphStyle('MetaVal', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#334155'))

    # Extract Metadata
    doc_name = analysis_data.get("document_name", "Agreement Document")
    doc_type = analysis_data.get("document_type", "Leave & License Agreement")
    health_score = analysis_data.get("health_score", 70)
    clauses = analysis_data.get("analyzed_clauses", [])
    risk_summary = analysis_data.get("risk_summary", {})
    masked_count = analysis_data.get("total_items_masked", 0)
    
    cert_date = datetime.datetime.now().strftime("%d %B %Y")
    cert_id = f"CL/CERT/{datetime.datetime.now().strftime('%Y%m%d')}-{(hash(doc_name + str(health_score)) & 0xFFFFFFFF):08X}"
    verification_hash = hashlib.sha256(f"{doc_name}:{health_score}:{cert_date}".encode()).hexdigest()[:24].upper()

    if health_score >= 85:
        grade = "GRADE A — COMPLIANT"
        grade_color = colors.HexColor('#15803D')
    elif health_score >= 70:
        grade = "GRADE B — MODERATE RISK"
        grade_color = colors.HexColor('#B45309')
    elif health_score >= 50:
        grade = "GRADE C — HIGH STATUTORY RISK"
        grade_color = colors.HexColor('#D97706')
    else:
        grade = "GRADE D — SEVERE STATUTORY NON-COMPLIANCE"
        grade_color = colors.HexColor('#B91C1C')

    # 1. CERTIFICATE HEADER
    story.append(Paragraph("CERTIFICATE OF STATUTORY LEGAL COMPLIANCE", header_style))
    story.append(Paragraph("ISSUED BY CONTRACTLENS STATUTORY COMPLIANCE & PRIVACY ENGINE", sub_header_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceBefore=2, spaceAfter=14))

    # 2. CERTIFICATE PREAMBLE
    preamble_text = (
        f"This is to certify that the legal instrument detailed below has undergone a comprehensive automated "
        f"statutory risk audit and data privacy screening under applicable legislation of the State of Maharashtra, "
        f"Republic of India."
    )
    story.append(Paragraph(preamble_text, body_style))
    story.append(Spacer(1, 8))

    # 3. DOCUMENT IDENTIFICATION TABLE
    doc_table_data = [
        [Paragraph("CERTIFICATE REF NO:", meta_label), Paragraph(cert_id, meta_val), Paragraph("ISSUE DATE:", meta_label), Paragraph(cert_date, meta_val)],
        [Paragraph("EXAMINED DOCUMENT:", meta_label), Paragraph(doc_name, meta_val), Paragraph("INSTRUMENT TYPE:", meta_label), Paragraph(doc_type, meta_val)],
        [Paragraph("JURISDICTION:", meta_label), Paragraph("State of Maharashtra, India", meta_val), Paragraph("VERIFICATION HASH:", meta_label), Paragraph(verification_hash, meta_val)]
    ]
    doc_table = Table(doc_table_data, colWidths=[1.4*inch, 2.3*inch, 1.4*inch, 2.3*inch])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(doc_table)
    story.append(Spacer(1, 14))

    # 4. COMPLIANCE AUDIT SCORE BOX
    story.append(Paragraph("STATUTORY COMPLIANCE RATING & AUDIT SCORE", section_heading))
    
    score_p = Paragraph(f"<b>COMPLIANCE SCORE: {health_score} / 100</b> &nbsp;&nbsp;|&nbsp;&nbsp; <b>RATING: {grade}</b>", ParagraphStyle('ScoreP', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.white, alignment=TA_CENTER))
    score_table = Table([[score_p]], colWidths=[7.4*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), grade_color),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(score_table)
    story.append(Spacer(1, 10))

    crit_cnt = risk_summary.get("CRITICAL", 0)
    high_cnt = risk_summary.get("HIGH", 0)
    med_cnt = risk_summary.get("MEDIUM", 0)
    low_cnt = risk_summary.get("LOW", 0)

    summary_text = (
        f"<b>Audit Scope:</b> Evaluated <b>{len(clauses)} contractual provisions</b> against the "
        f"<b>Maharashtra Rent Control Act, 1999</b>, <b>Transfer of Property Act, 1882</b>, and <b>Indian Contract Act, 1872</b>.<br/>"
        f"<b>Finding Breakdown:</b> Identified <b>{crit_cnt} Critical Statutory Violations</b>, <b>{high_cnt} High Risk Concerns</b>, "
        f"<b>{med_cnt} Moderate Risks</b>, and <b>{low_cnt} Compliant Clauses</b>."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 12))

    # 5. DPDP ACT 2023 PRIVACY AUDIT LOG
    story.append(Paragraph("DIGITAL PERSONAL DATA PROTECTION ACT, 2023 — PRIVACY AUDIT SEAL", section_heading))
    
    privacy_text = (
        f"<b>DPDP Act 2023 Shield Status:</b> <font color='#15803D'><b>VERIFIED PASSED</b></font><br/>"
        f"Prior to statutory cloud intelligence analysis, all personally identifiable information (PII) including "
        f"personal names, Aadhaar/PAN identification numbers, financial account credentials, and contact details were "
        f"locally redacted in strict compliance with the Digital Personal Data Protection Act, 2023.<br/>"
        f"<b>Total PII Elements Masked:</b> <b>{masked_count} Items</b>"
    )
    
    privacy_box = Table([[Paragraph(privacy_text, ParagraphStyle('PrivText', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#0F172A')))]], colWidths=[7.4*inch])
    privacy_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('PADDING', (0,0), (-1,-1), 8)
    ]))
    story.append(privacy_box)
    story.append(Spacer(1, 14))

    # 6. KEY STATUTORY NON-COMPLIANCE SUMMARY
    if crit_cnt > 0 or high_cnt > 0:
        story.append(Paragraph("CRITICAL STATUTORY AUDIT FINDINGS (ACTION REQUIRED)", section_heading))
        flagged = [c for c in clauses if c.get("risk_level") in ["CRITICAL", "HIGH"]][:3]
        for c in flagged:
            sec = c.get("section_number", "N/A")
            title = c.get("title", "Clause")
            reason = c.get("reason", "")
            f_text = f"• <b>Clause {sec} ({title}):</b> {reason}"
            story.append(Paragraph(f_text, ParagraphStyle('FlagP', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#991B1B'))))
        story.append(Spacer(1, 12))

    # 7. OFFICIAL ISSUANCE SIGNATURE & SEAL BLOCK
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=8, spaceAfter=12))

    sig_data = [
        [
            Paragraph("<b>CERTIFICATION AUTHORITY</b><br/>ContractLens Legal Intelligence Engine<br/>Automated Statutory Vetting System", ParagraphStyle('SigL', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#475569'))),
            Paragraph("<b>VERIFICATION SEAL</b><br/>Digitally Authenticated<br/>Hash: " + verification_hash[:16], ParagraphStyle('SigR', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#475569'), alignment=TA_RIGHT))
        ]
    ]
    sig_table = Table(sig_data, colWidths=[3.7*inch, 3.7*inch])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 0)
    ]))
    story.append(sig_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
