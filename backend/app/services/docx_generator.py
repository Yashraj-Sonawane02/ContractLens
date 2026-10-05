import io
import datetime
from typing import Dict, Any, List
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def generate_revised_contract_docx(analysis_data: Dict[str, Any]) -> bytes:
    """
    Generates a formal, law-firm grade revised legal contract Word (.docx) document
    with tracked changes (redlines) for critical & high risk clauses.
    """
    doc = docx.Document()

    # Set Margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Document Header Title
    doc_name = analysis_data.get("document_name", "Agreement Document")
    doc_type = analysis_data.get("document_type", "Leave & License Agreement")
    clauses = analysis_data.get("analyzed_clauses", [])

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run(f"REVISED & REDLINED INSTRUMENT: {doc_type.upper()}")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42) # Slate dark

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run(f"Statutorily Compliant Counter-Draft Prepared by ContractLens Legal AI\nJurisdiction: State of Maharashtra, India | Date: {datetime.datetime.now().strftime('%d %B %Y')}")
    sub_run.font.name = 'Times New Roman'
    sub_run.font.size = Pt(9.5)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph() # Divider spacing

    # Redline Legend Box Table
    legend_table = doc.add_table(rows=1, cols=1)
    legend_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = legend_table.cell(0, 0)
    cell.width = Inches(6.5)
    
    # Set cell shading & border
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
    tcPr.append(shd)

    lp = cell.paragraphs[0]
    lp.paragraph_format.space_before = Pt(4)
    lp.paragraph_format.space_after = Pt(4)
    
    l_run1 = lp.add_run("LEGAL REDLINE LEGEND: ")
    l_run1.font.bold = True
    l_run1.font.size = Pt(9)
    l_run1.font.name = 'Times New Roman'

    l_run2 = lp.add_run("[Strikethrough Red Text] ")
    l_run2.font.strike = True
    l_run2.font.color.rgb = RGBColor(185, 28, 28)
    l_run2.font.size = Pt(9)
    l_run2.font.name = 'Times New Roman'

    l_run3 = lp.add_run("indicates original clause text deleted due to statutory non-compliance. ")
    l_run3.font.size = Pt(9)
    l_run3.font.name = 'Times New Roman'

    l_run4 = lp.add_run("[Green Underlined Bold Text] ")
    l_run4.font.underline = True
    l_run4.font.bold = True
    l_run4.font.color.rgb = RGBColor(21, 128, 61)
    l_run4.font.size = Pt(9)
    l_run4.font.name = 'Times New Roman'

    l_run5 = lp.add_run("indicates statutorily compliant counter-proposal inserted.")
    l_run5.font.size = Pt(9)
    l_run5.font.name = 'Times New Roman'

    doc.add_paragraph()

    # Iterate Clauses and Add Formatted Paragraphs
    for idx, c in enumerate(clauses, 1):
        sec_num = c.get("section_number", idx)
        title = c.get("title", f"Clause {sec_num}")
        risk = c.get("risk_level", "LOW")
        orig_text = c.get("original_text", "")
        suggested = c.get("suggested_wording", "")
        reason = c.get("reason", "")

        # Heading
        head_p = doc.add_paragraph()
        head_p.paragraph_format.space_before = Pt(10)
        head_p.paragraph_format.space_after = Pt(2)
        head_run = head_p.add_run(f"CLAUSE {sec_num}: {title.upper()}")
        head_run.font.name = 'Times New Roman'
        head_run.font.size = Pt(11)
        head_run.font.bold = True

        # Clause Text Body
        body_p = doc.add_paragraph()
        body_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        body_p.paragraph_format.space_after = Pt(8)
        body_p.paragraph_format.line_spacing = 1.15

        if risk in ["CRITICAL", "HIGH", "MEDIUM"] and suggested and suggested.strip() != orig_text.strip():
            # Show Redlined Strikethrough of Original Text
            del_run = body_p.add_run(f"\"{orig_text}\" ")
            del_run.font.name = 'Times New Roman'
            del_run.font.size = Pt(10.5)
            del_run.font.strike = True
            del_run.font.color.rgb = RGBColor(185, 28, 28) # Red

            # Show Statutorily Compliant Inserted Wording
            ins_run = body_p.add_run(f"\n[STATUTORY COUNTER-PROPOSAL]: \"{suggested}\"")
            ins_run.font.name = 'Times New Roman'
            ins_run.font.size = Pt(10.5)
            ins_run.font.bold = True
            ins_run.font.underline = True
            ins_run.font.color.rgb = RGBColor(21, 128, 61) # Green

            # Statutory Note
            note_p = doc.add_paragraph()
            note_p.paragraph_format.left_indent = Inches(0.4)
            note_p.paragraph_format.space_after = Pt(12)
            n_run = note_p.add_run(f"Legal Rationale: {reason}")
            n_run.font.name = 'Times New Roman'
            n_run.font.size = Pt(9)
            n_run.font.italic = True
            n_run.font.color.rgb = RGBColor(100, 116, 139)
        else:
            # Low Risk / Standard Clause - Keep Original
            keep_run = body_p.add_run(f"\"{orig_text}\"")
            keep_run.font.name = 'Times New Roman'
            keep_run.font.size = Pt(10.5)
            keep_run.font.color.rgb = RGBColor(15, 23, 42)

    # Formal Execution Block
    doc.add_paragraph()
    sig_p = doc.add_paragraph()
    sig_p.paragraph_format.space_before = Pt(20)
    sig_run = sig_p.add_run("IN WITNESS WHEREOF, THE PARTIES HERETO HAVE EXECUTED THIS REVISED INSTRUMENT.")
    sig_run.font.name = 'Times New Roman'
    sig_run.font.size = Pt(10)
    sig_run.font.bold = True

    sig_table = doc.add_table(rows=2, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    cell_l1 = sig_table.cell(0, 0)
    cell_l1.paragraphs[0].add_run("_____________________________\nLICENSOR / LANDLORD\nDate:").font.name = 'Times New Roman'
    
    cell_r1 = sig_table.cell(0, 1)
    cell_r1.paragraphs[0].add_run("_____________________________\nLICENSEE / TENANT\nDate:").font.name = 'Times New Roman'

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
