#!/usr/bin/env python3
"""Convert report-draft.md into report.tex, following the official
Apart submission template: title with the sprint footnote, author
block, With Apart Research, Abstract, numbered sections 1 to 6, then
unnumbered Code and Data, Author Contributions, References,
Appendix, and LLM Usage Statement."""
import re
from pathlib import Path

import pypandoc

REPO = Path(__file__).resolve().parent.parent
SRC = str(REPO / "report" / "report-draft.md")
OUT = str(REPO / "report" / "report.tex")

text = open(SRC).read()
title = text.split("\n", 1)[0].removeprefix("# ").strip()
abstract_md = text.split("## Abstract", 1)[1].split("## Introduction", 1)[0].strip()
body_md = "## Introduction" + text.split("## Introduction", 1)[1]

abstract_tex = pypandoc.convert_text(abstract_md, "latex", format="md").strip()
body_tex = pypandoc.convert_text(body_md, "latex", format="md")

# Pandoc maps markdown h2 to \subsection and h3 to \subsubsection.
# The report body starts at h2, so promote every heading by one level.
body_tex = body_tex.replace("\\subsubsection", "\x00PROMOTE\x00")
body_tex = body_tex.replace("\\subsection", "\\section")
body_tex = body_tex.replace("\x00PROMOTE\x00", "\\subsection")

UNNUMBERED = [
    "Code and Data",
    "Author Contributions",
    "References",
    "LLM Usage Statement",
]
for name in UNNUMBERED:
    body_tex = body_tex.replace("\\section{" + name + "}",
                                "\\section*{" + name + "}")
body_tex = re.sub(
    r"\\section\{Appendix:[^}]*\}",
    r"\\section*{Appendix: Limitations and Dual-Use / Ethical Considerations}",
    body_tex, count=1, flags=re.S)

preamble = r"""\documentclass[11pt]{article}
\usepackage[letterpaper, margin=1in]{geometry}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{calc}
\usepackage{etoolbox}
\usepackage{hyperref}
\hypersetup{hidelinks}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setlength{\parskip}{4pt}
\setlength{\parindent}{0pt}
"""

front = (
    "\\title{" + title + "\\thanks{Research conducted at the AI Collusion Research Sprint, October 2026}}\n"
    "\\author{Shash Bhatia \\\\ Independent Researcher}\n"
    "\\date{}\n"
    "\\begin{document}\n"
    "\\maketitle\n"
    "\\begin{center}\nWith Apart Research\n\\end{center}\n"
    "\\begin{abstract}\n" + abstract_tex + "\n\\end{abstract}\n"
)

doc = preamble + front + body_tex + "\n\\end{document}\n"
open(OUT, "w").write(doc)
print(f"wrote {OUT}: {len(doc.splitlines())} lines")
