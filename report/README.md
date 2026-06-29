# Final Report Workspace

This folder contains the LaTeX final report and report-only assets.

Generate figures and data-flow diagrams:

```bash
MPLCONFIGDIR=.matplotlib-cache \
  ../.venv/bin/python scripts/generate_report_assets.py
```

Compile the report:

```bash
pdflatex huatuo_medical_qa_report.tex
bibtex huatuo_medical_qa_report
pdflatex huatuo_medical_qa_report.tex
pdflatex huatuo_medical_qa_report.tex
```

Main file:

```text
huatuo_medical_qa_report.tex
```

Generated figures:

```text
figures/
```
