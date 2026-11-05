"""
Script: scripts/sync_docx.py
Converts HERM4AI_Doc.md into a beautifully formatted Microsoft Word (.docx) document,
ensuring 100% substantive synchronization between Markdown and Word counterparts.
"""

import re
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def build_docx_from_markdown(md_path: str = "HERM4AI_Doc.md", docx_path: str = "HERM4AI_Doc.docx"):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = docx.Document()

    # Set standard margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Configure default styles
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)

    lines = md_text.split("\n")
    in_code_block = False
    code_buffer = []
    in_table = False
    table_lines = []

    def flush_table(tbl_lines):
        if not tbl_lines:
            return
        rows = [
            [c.strip() for c in line.strip().strip("|").split("|")]
            for line in tbl_lines
            if not re.match(r"^\|?[\s\-:|]+\|?$", line.strip())
        ]
        if not rows:
            return
        table = doc.add_table(rows=len(rows), cols=len(rows[0]))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"

        for r_idx, row in enumerate(rows):
            for c_idx, cell_text in enumerate(row):
                if c_idx < len(table.columns):
                    cell = table.cell(r_idx, c_idx)
                    cell.text = cell_text
                    # Header formatting
                    if r_idx == 0:
                        shading_elm = parse_xml(r'<w:shd {} w:fill="0F172A"/>'.format(nsdecls('w')))
                        cell._tc.get_or_add_tcPr().append(shading_elm)
                        for p in cell.paragraphs:
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            for run in p.runs:
                                run.font.bold = True
                                run.font.color.rgb = RGBColor(255, 255, 255)
                                run.font.size = Pt(9.5)
                    else:
                        for p in cell.paragraphs:
                            for run in p.runs:
                                run.font.size = Pt(9.5)
        doc.add_paragraph()  # Spacing

    for line in lines:
        stripped = line.strip()

        # Handle code blocks
        if stripped.startswith("```"):
            if in_code_block:
                # Flush code block
                code_text = "\n".join(code_buffer)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.5)
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(6)
                run = p.add_run(code_text)
                run.font.name = "Consolas"
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(51, 65, 85)
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        # Handle tables
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            table_lines.append(stripped)
            continue
        elif in_table:
            flush_table(table_lines)
            table_lines = []
            in_table = False

        if not stripped:
            continue

        # Title and Subtitle
        if stripped.startswith("# HERM4AI"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run("HERM4AI")
            run.font.size = Pt(26)
            run.font.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)
            continue

        if stripped.startswith("## Human-inspired"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(stripped.replace("## ", ""))
            run.font.size = Pt(14)
            run.font.italic = True
            run.font.color.rgb = RGBColor(71, 85, 105)
            continue

        if stripped.startswith("### Research Proposal"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(18)
            run = p.add_run(stripped.replace("### ", ""))
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = RGBColor(100, 116, 139)
            continue

        if stripped == "---":
            continue

        # Headings
        if stripped.startswith("# "):
            h_text = stripped[2:].strip()
            h = doc.add_heading(h_text, level=1)
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
            for r in h.runs:
                r.font.name = "Calibri"
                r.font.color.rgb = RGBColor(15, 23, 42)
            continue

        if stripped.startswith("## "):
            h_text = stripped[3:].strip()
            h = doc.add_heading(h_text, level=2)
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(3)
            for r in h.runs:
                r.font.name = "Calibri"
                r.font.color.rgb = RGBColor(30, 41, 59)
            continue

        if stripped.startswith("### "):
            h_text = stripped[4:].strip()
            h = doc.add_heading(h_text, level=3)
            h.paragraph_format.space_before = Pt(6)
            h.paragraph_format.space_after = Pt(2)
            for r in h.runs:
                r.font.name = "Calibri"
                r.font.color.rgb = RGBColor(51, 65, 85)
            continue

        # Bullet lists
        if stripped.startswith("- ") or stripped.startswith("* "):
            bullet_text = stripped[2:].strip()
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            # Process bold runs inside bullets
            parts = re.split(r"(\*\*.*?\*\*)", bullet_text)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.font.bold = True
                else:
                    p.add_run(part)
            continue

        # Standard Paragraphs
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        parts = re.split(r"(\*\*.*?\*\*|\*.*?\*|`.*?`)", stripped)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                r = p.add_run(part[2:-2])
                r.font.bold = True
            elif part.startswith("*") and part.endswith("*") and not part.startswith("**"):
                r = p.add_run(part[1:-1])
                r.font.italic = True
            elif part.startswith("`") and part.endswith("`"):
                r = p.add_run(part[1:-1])
                r.font.name = "Consolas"
                r.font.size = Pt(10)
                r.font.color.rgb = RGBColor(37, 99, 235)
            else:
                p.add_run(part)

    if in_table:
        flush_table(table_lines)

    doc.save(docx_path)
    print(f"Successfully generated and synchronized Word document: {docx_path}")


if __name__ == "__main__":
    build_docx_from_markdown()
