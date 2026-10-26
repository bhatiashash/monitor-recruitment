#!/usr/bin/env python3
"""Build the submission PDF from report-draft.md, following the Apart
sprint template structure: title, author block, With Apart Research,
sprint footnote, Abstract, numbered sections, References, Appendix.
Reports the page on which References begins (the 8-page cap excludes
references and appendices)."""
import re
import sys

from fpdf import FPDF

SRC = "/home/hatch/workspace/sprint/monitor/report-draft.md"
OUT = "/home/hatch/workspace/sprint/monitor/report.pdf"

TRANS = {
    "’": "'", "‘": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "×": "x", "−": "-",
    " ": " ",
}


def clean(s):
    for k, v in TRANS.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "replace").decode("latin-1")


def parse(text):
    """Return (title, author_lines, blocks) where blocks are tuples:
    ('abstract', [paras]), ('h2', text), ('h3', text), ('p', text),
    ('bullets', [items]), ('table', [[cells], ...])."""
    lines = text.split("\n")
    title = None
    author = []
    blocks = []
    i = 0
    mode = "front"
    para = []
    bullets = []
    table = []

    def flush():
        nonlocal para, bullets, table
        if para:
            blocks.append(("p", " ".join(para)))
            para = []
        if bullets:
            blocks.append(("bullets", bullets))
            bullets = []
        if table:
            blocks.append(("table", table))
            table = []

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# ") and title is None:
            title = ln[2:].strip()
            i += 1
            continue
        if ln.startswith("## Abstract"):
            mode = "body"
            flush()
            blocks.append(("abstract_head", "Abstract"))
            i += 1
            continue
        if ln.startswith("## "):
            mode = "body"
            flush()
            blocks.append(("h2", ln[3:].strip()))
            i += 1
            continue
        if ln.startswith("### "):
            flush()
            blocks.append(("h3", ln[4:].strip()))
            i += 1
            continue
        if mode == "front":
            if ln.strip():
                author.append(ln.strip())
            i += 1
            continue
        if ln.strip().startswith("|"):
            if para or bullets:
                flush()
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if not all(set(c) <= set("-: ") for c in cells):
                table.append(cells)
            i += 1
            continue
        if table:
            flush()
        if ln.startswith("- "):
            if para:
                flush()
            bullets.append(ln[2:].strip())
            i += 1
            continue
        if ln.startswith("  ") and bullets and ln.strip():
            bullets[-1] += " " + ln.strip()
            i += 1
            continue
        if ln.startswith("  ") and para and ln.strip():
            para.append(ln.strip())
            i += 1
            continue
        if not ln.strip():
            flush()
            i += 1
            continue
        if bullets:
            flush()
        para.append(ln.strip())
        i += 1
    flush()
    return title, author, blocks


class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def main():
    text = open(SRC).read()
    title, author, blocks = parse(text)
    pdf = PDF(format="letter")
    pdf.set_margins(22, 20, 22)
    pdf.set_auto_page_break(True, margin=20)
    pdf.add_page()

    pdf.set_font("helvetica", "B", 16)
    pdf.multi_cell(0, 8.5, clean(title), align="C")
    pdf.ln(4)
    pdf.set_font("helvetica", "", 11)
    for a in author:
        pdf.cell(0, 6, clean(a), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("helvetica", "I", 9)
    pdf.cell(0, 5, "Research conducted at the AI Collusion Research Sprint, October 2026",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    ref_start_page = None
    for kind, payload in blocks:
        if kind == "abstract_head":
            pdf.set_font("helvetica", "B", 13)
            pdf.cell(0, 8, payload, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif kind == "h2":
            if payload.startswith("References") and ref_start_page is None:
                ref_start_page = pdf.page_no()
            pdf.ln(3)
            pdf.set_font("helvetica", "B", 13)
            pdf.multi_cell(0, 7.5, clean(payload))
            pdf.ln(1)
        elif kind == "h3":
            pdf.ln(2)
            pdf.set_font("helvetica", "B", 11.5)
            pdf.multi_cell(0, 6.5, clean(payload))
            pdf.ln(1)
        elif kind == "p":
            pdf.set_font("helvetica", "", 10.8)
            pdf.multi_cell(0, 5.6, clean(payload), align="J")
            pdf.ln(1.6)
        elif kind == "bullets":
            pdf.set_font("helvetica", "", 10.8)
            for item in payload:
                x = pdf.get_x()
                pdf.set_x(x + 6)
                pdf.multi_cell(0, 5.6, clean("- " + item), align="J")
                pdf.ln(0.8)
            pdf.ln(1)
        elif kind == "table":
            rows = payload
            ncols = max(len(r) for r in rows)
            widths = []
            for c in range(ncols):
                m = max(len(r[c]) if c < len(r) else 0 for r in rows)
                widths.append(max(m, 4))
            total = sum(widths)
            avail = 210 - 44 + 28  # letter width 216mm - margins 44 -> 172; use 166
            avail = 166
            col_mm = tuple(w / total * avail for w in widths)
            pdf.set_font("helvetica", "", 9.3)
            with pdf.table(col_widths=col_mm, first_row_as_headings=True,
                           line_height=4.8, text_align="LEFT") as t:
                for ri, r in enumerate(rows):
                    row = t.row()
                    for c in range(ncols):
                        row.cell(clean(r[c]) if c < len(r) else "")
            pdf.ln(2.5)
    pdf.output(OUT)
    print(f"built {OUT}: total pages={pdf.page_no()}, "
          f"References begin on page {ref_start_page} "
          f"(body pages before references: {ref_start_page - 1 if ref_start_page else '?'})")


if __name__ == "__main__":
    main()
