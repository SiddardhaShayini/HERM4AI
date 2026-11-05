# HERM4AI Academic Paper — LaTeX Compilation Guide

This directory contains the complete, publication-ready LaTeX source and BibTeX bibliography for the HERM4AI research paper:
> **"Beyond Flat Vector Retrieval: Mitigating the Dual Collapse and In-Context Prompt Poisoning of RAG via Structured Valid-Time Cognitive Architectures"**

---

## File Registry

| File | Description |
|---|---|
| `docs/paper.tex` | Two-column LaTeX manuscript with a full-width title, abstract, and keywords |
| `docs/references.bib` | BibTeX bibliography with 18 references, including peer-reviewed papers, preprints, and books |
| `docs/PAPER_MANUSCRIPT.docx` | Formatted Word document counterpart (48.3 KB) |
| `docs/PAPER_MANUSCRIPT.md` | Markdown source manuscript |

---

## How to Compile `paper.tex` to PDF

### Method 1: Using Overleaf (Recommended for Frictionless Editing & Collaboration)
1. Open [Overleaf](https://www.overleaf.com) and create a **New Project $\to$ Upload Project**.
2. Upload `docs/paper.tex` and `docs/references.bib`.
3. Set the compiler to **pdfLaTeX**.
4. Click **Recompile** (allow all LaTeX/BibTeX passes to finish). Citations and the numbered reference list are resolved automatically.
5. The title, abstract, and keywords occupy a full-width block; the body is
   two-column. Figures and tables are single-column floats, with wide results
   tables reformatted to fit a column.

---

### Method 2: Local Command Line (TeX Live / MiKTeX / MacTeX)
Open a terminal in `D:\HERM4AI\docs` and execute standard 4-pass compilation:

```bash
# 1. First LaTeX pass (generates .aux and citation keys)
pdflatex paper.tex

# 2. BibTeX pass (resolves references from references.bib)
bibtex paper

# 3. Second LaTeX pass (inserts resolved citation numbers)
pdflatex paper.tex

# 4. Final LaTeX pass (resolves cross-references and page numbers)
pdflatex paper.tex
```

Or using `latexmk` (automatic multi-pass build):
```bash
latexmk -pdf paper.tex
```

The manuscript uses numeric citations and a numbered bibliography. If a
previous build still shows author-year citations or unresolved references,
clear the generated auxiliary files (or use Overleaf's **Recompile from
scratch**) and run the complete build sequence again.

---

## Required LaTeX Packages (All Standard in TeX Live / MiKTeX)

The manuscript relies exclusively on standard, widely supported CTAN packages:
- `geometry` (Standard 1-inch margins)
- `amsmath`, `amssymb`, `amsthm`, `mathtools` (Mathematical notation, operators, and theorem environments)
- `booktabs`, `array`, `tabularx`, `makecell` (Scientific tables)
- `natbib` (Numeric citations and numbered bibliography)
- `microtype` (High-quality optical font margin expansion)
- `graphicx`, `xcolor`, `tikz` (Figures, color, and the architecture diagram)
- `hyperref`, `cleveref` (Clickable links and formatted cross-references)
- `enumitem`, `parskip`, `inputenc`, `fontenc`, `lmodern` (Typography and document layout)

---

## Academic Rigor & Style Assurance
- **Original Prose:** All text is original, mathematically formal, and free of automated generative filler clichés (no "in recent years", "testament to", "delve", or repetitive generic phrasing).
- **Proper Attribution:** Accurately cites foundational literature:
  - RAG: Lewis et al. (NeurIPS 2020)
  - TempLAMA: Dhingra et al. (TACL 2022)
  - FreshQA: Vu et al. (2023)
  - MemGPT: Packer et al. (2023)
  - Generative Agents: Park et al. (UIST 2023)
  - Model Editing: Meng et al. (NeurIPS 2022)
  - Complementary Learning Systems: McClelland et al. (Psychological Review 1995)
  - Sleep Consolidation: Diekelmann & Born (Nature Reviews Neuroscience 2010)
  - ACT-R: Anderson (1993)
  - Working Memory: Miller (1956)
  - Sentence-BERT: Reimers & Gurevych (EMNLP 2019)
  - Flan-T5: Chung et al. (JMLR 2024)
  - Qwen2.5: Qwen Team (2024)
  - Continual learning survey: De Lange et al. (TPAMI 2022)
  - Elastic Weight Consolidation: Kirkpatrick et al. (PNAS 2017)
  - CoALA language-agent architecture: Yao et al. (arXiv 2023)
- **Empirical Reproducibility:** Before submission, trace each quantitative claim to the matching script, dataset, and recorded run output in `scripts/`, `data/`, `results/`, or `notebooks/`.
