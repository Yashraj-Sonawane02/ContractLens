import io
import datetime
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def generate_formal_legal_pdf(analysis_data: Dict[str, Any]) -> bytes:
    """
    Generates a formal, law-firm grade Legal Vetting Opinion & Statutory Compliance PDF report.
    No web graphics, no dark background, no rounded cards — strictly formal legal formatting.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=54,  # 0.75 in
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Formal Legal Typography Styles
    title_style = ParagraphStyle(
        'LegalTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'LegalSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    meta_val_style = ParagraphStyle(
        'MetaValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    section_heading = ParagraphStyle(
        'LegalSectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'LegalBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=8
    )

    quote_style = ParagraphStyle(
        'LegalQuote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        rightIndent=15,
        spaceBefore=4,
        spaceAfter=6
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=TA_LEFT
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )

    # Extract Data
    doc_name = analysis_data.get("document_name", "Agreement Document")
    doc_type = analysis_data.get("document_type", "Leave & License Agreement")
    health_score = analysis_data.get("health_score", 70)
    clauses = analysis_data.get("analyzed_clauses", [])
    risk_summary = analysis_data.get("risk_summary", {})
    masked_count = analysis_data.get("total_items_masked", 0)
    audit_date = datetime.datetime.now().strftime("%d %B %Y")
    audit_ref = f"CL/AUDIT/{datetime.datetime.now().strftime('%Y%m%d')}-{hash(doc_name) % 8999 + 1000}"

    # Determine Compliance Rating Label
    if health_score >= 85:
        vetting_status = "APPROVED — SATISFACTORY STATUTORY COMPLIANCE"
        status_color = colors.HexColor('#15803D')
    elif health_score >= 65:
        vetting_status = "CONDITIONAL APPROVAL — SUBJECT TO MANDATORY REVISION"
        status_color = colors.HexColor('#B45309')
    else:
        vetting_status = "NOT RECOMMENDED — CRITICAL STATUTORY NON-COMPLIANCE"
        status_color = colors.HexColor('#B91C1C')

    # 1. DOCUMENT HEADER & LETTERHEAD LINE
    story.append(Paragraph("FORMAL LEGAL VETTING OPINION & COMPLIANCE AUDIT", title_style))
    story.append(Paragraph("CONTRACTLENS STATUTORY COMPLIANCE ENGINE • JURISDICTION: MAHARASHTRA, INDIA", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceBefore=2, spaceAfter=12))

    # 2. DOCUMENT CONTROL METADATA TABLE
    meta_data = [
        [
            Paragraph("AUDIT REF NO:", meta_label_style),
            Paragraph(audit_ref, meta_val_style),
            Paragraph("DATE OF EXAMINATION:", meta_label_style),
            Paragraph(audit_date, meta_val_style)
        ],
        [
            Paragraph("SUBJECT INSTRUMENT:", meta_label_style),
            Paragraph(doc_name, meta_val_style),
            Paragraph("INSTRUMENT TYPE:", meta_label_style),
            Paragraph(doc_type, meta_val_style)
        ],
        [
            Paragraph("APPLICABLE LAWS:", meta_label_style),
            Paragraph("MRCA 1999 • TPA 1882 • ICA 1872", meta_val_style),
            Paragraph("PRIVACY SHIELD:", meta_label_style),
            Paragraph(f"DPDP Act 2023 ({masked_count} Items Redacted)", meta_val_style)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[1.3*inch, 2.3*inch, 1.4*inch, 2.2*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. EXECUTIVE LEGAL OPINION
    story.append(Paragraph("I. EXECUTIVE LEGAL OPINION & VETTING STATUS", section_heading))
    
    # Status Banner Table
    status_text = f"<b>STATUTORY COMPLIANCE SCORE:</b> {health_score}/100 &nbsp;&nbsp;|&nbsp;&nbsp; <b>VETTING STATUS:</b> {vetting_status}"
    status_p = Paragraph(status_text, ParagraphStyle('StatusBanner', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.white))
    status_table = Table([[status_p]], colWidths=[7.2*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), status_color),
        ('PADDING', (0,0), (-1,-1), 7),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 8))

    crit_cnt = risk_summary.get("CRITICAL", 0)
    high_cnt = risk_summary.get("HIGH", 0)
    med_cnt = risk_summary.get("MEDIUM", 0)
    low_cnt = risk_summary.get("LOW", 0)

    exec_summary_text = (
        f"Following a rigorous statutory examination under the <b>Maharashtra Rent Control Act, 1999 (MRCA)</b>, "
        f"<b>Transfer of Property Act, 1882 (TPA)</b>, and <b>Indian Contract Act, 1872 (ICA)</b>, the subject instrument "
        f"contains a total of <b>{len(clauses)} analyzed provisions</b>, resulting in <b>{crit_cnt} Critical Statutory Violations</b>, "
        f"<b>{high_cnt} High-Risk Commercial Imbalances</b>, <b>{med_cnt} Moderate Risks</b>, and <b>{low_cnt} Compliant Clauses</b>.<br/><br/>"
        f"Any covenants violating non-waivable statutory protections (such as Section 29 utility cut-offs or Section 10/11 rent escalation caps under MRCA 1999) "
        f"are <i>void ab initio</i> under Section 23 of the Indian Contract Act, 1872. Execution in current form is non-advisable prior to incorporating the "
        f"redline counter-provisions set forth in Section III of this opinion."
    )
    story.append(Paragraph(exec_summary_text, body_style))
    story.append(Spacer(1, 10))

    # 4. STATUTORY RISK & NON-COMPLIANCE MATRIX
    story.append(Paragraph("II. STATUTORY NON-COMPLIANCE & RISK MATRIX", section_heading))
    
    matrix_headers = ["Clause Ref & Subject", "Risk Rating", "Statutory Authority / Act", "Legal Enforceability", "Action Required"]
    matrix_rows = [[Paragraph(h, table_header_style) for h in matrix_headers]]

    for c in clauses:
        sec = c.get("section_number", "N/A")
        title = c.get("title", "Untitled Provision")
        risk = c.get("risk_level", "LOW")
        reason = c.get("reason", "")
        
        rel_stats = c.get("relevant_statutes", [])
        stat_cite = rel_stats[0].get("act_short", "") + " " + rel_stats[0].get("section", "") if rel_stats else "Indian Law Principles"

        enforceability = "Void & Unenforceable" if risk in ["CRITICAL", "HIGH"] else "Conditionally Valid" if risk == "MEDIUM" else "Statutorily Valid"
        action = "Mandatory Deletion / Redline" if risk in ["CRITICAL", "HIGH"] else "Recommended Revision" if risk == "MEDIUM" else "Maintain As Is"

        # Cell styling by risk
        risk_color_hex = "#B91C1C" if risk == "CRITICAL" else "#B45309" if risk == "HIGH" else "#D97706" if risk == "MEDIUM" else "#15803D"
        risk_p = Paragraph(f"<font color='{risk_color_hex}'><b>{risk}</b></font>", table_cell_bold)

        matrix_rows.append([
            Paragraph(f"<b>Clause {sec}</b><br/>{title}", table_cell_style),
            risk_p,
            Paragraph(stat_cite, table_cell_style),
            Paragraph(enforceability, table_cell_style),
            Paragraph(action, table_cell_style)
        ])

    matrix_table = Table(matrix_rows, colWidths=[1.8*inch, 1.0*inch, 1.6*inch, 1.4*inch, 1.4*inch])
    matrix_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(matrix_table)
    story.append(Spacer(1, 14))

    # 5. DETAILED CLAUSE-BY-CLAUSE VETTING & REDLINE COUNTER-PROPOSALS
    story.append(Paragraph("III. DETAILED CLAUSE-BY-CLAUSE VETTING & REDLINE COUNTER-PROPOSALS", section_heading))

    for idx, c in enumerate(clauses, 1):
        sec = c.get("section_number", "N/A")
        title = c.get("title", "Untitled Clause")
        risk = c.get("risk_level", "LOW")
        orig_text = c.get("original_text", "")
        explanation = c.get("legal_explanation", "")
        reason = c.get("reason", "")
        recommendation = c.get("recommendation", "")
        suggested = c.get("suggested_wording", "")

        clause_elements = []

        # Clause Sub-Header
        c_header = f"<b>{idx}. Clause {sec}: {title}</b> [Risk Rating: {risk}]"
        clause_elements.append(Paragraph(c_header, ParagraphStyle('ClauseHead', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#0F172A'), spaceBefore=8, spaceAfter=4)))

        # Original Text Quote
        clause_elements.append(Paragraph(f"<b>Original Provision Text:</b>", ParagraphStyle('SubHead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11)))
        clause_elements.append(Paragraph(f"\"{orig_text}\"", quote_style))

        # Statutory Finding & Rationale
        clause_elements.append(Paragraph(f"<b>Statutory Vetting Finding & Enforceability:</b>", ParagraphStyle('SubHead2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11)))
        clause_elements.append(Paragraph(explanation, body_style))

        # Redline Counter-Proposal if risk is critical/high/medium
        if suggested and risk in ["CRITICAL", "HIGH", "MEDIUM"]:
            clause_elements.append(Paragraph(f"<b>Proposed Redline Counter-Provision (Mandatory Amendment):</b>", ParagraphStyle('SubHead3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#15803D'))))
            redline_text = f"<b>AMENDED TEXT:</b> \"{suggested}\""
            
            redline_box = Table([[Paragraph(redline_text, ParagraphStyle('RedlineText', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#064E3B')))]], colWidths=[7.0*inch])
            redline_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ECFDF5')),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#A7F3D0')),
                ('PADDING', (0,0), (-1,-1), 6)
            ]))
            clause_elements.append(redline_box)

        clause_elements.append(Spacer(1, 10))
        story.append(KeepTogether(clause_elements))

    # 6. MANDATORY PRE-EXECUTION CHECKLIST & DISCLAIMER
    story.append(Paragraph("IV. STATUTORY PRE-EXECUTION CHECKLIST & SIGN-OFF", section_heading))
    checklist_items = [
        "<b>1. Mandatory Registration:</b> This instrument must be dually registered at the Sub-Registrar Office under Section 55 of the Maharashtra Rent Control Act, 1999. The statutory responsibility rests upon the Licensor.",
        "<b>2. Stamp Duty Adjudication:</b> Ensure proper stamp duty payment under Article 36A of the Maharashtra Stamp Act, 1958.",
        "<b>3. Police Intimation:</b> Tenant verification details must be formally submitted to the jurisdictional police station under Section 188 of the Indian Penal Code."
    ]

    for item in checklist_items:
        story.append(Paragraph(item, body_style))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=6, spaceAfter=8))
    
    disclaimer_text = (
        "<b>FORMAL LEGAL DISCLAIMER:</b> This Legal Vetting Opinion is generated by ContractLens Statutory Legal Engine "
        "grounded in Indian legislation (MRCA 1999, TPA 1882, ICA 1872). It serves as an authoritative legal compliance audit. "
        "For court filing or litigation representation, consult a registered advocate of the High Court of Judicature at Bombay."
    )
    story.append(Paragraph(disclaimer_text, ParagraphStyle('Disclaimer', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10, textColor=colors.HexColor('#64748B'))))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
