# Rubric Compliance Checklist
## Image Processing & Computer Vision — Project Evaluation Rubric

This document maps every **rubric criterion** and **student instruction** from `Image_Processing_Project_Rubric.pdf` to completed deliverables in this repository.

---

## Evaluation Criteria (25 marks total)

| Criterion | Max | Requirement | Completed deliverable | Location |
|-----------|-----|-------------|----------------------|----------|
| **Problem Definition & Understanding** | 4 | Clarity, relevance, objectives | §3 Introduction + §2 Abstract with defined problem, motivation, 5 objectives | `IPV_Project_Report.md` §2–3 |
| **Methodology & Technical Approach** | 5 | Algorithm selection, justification, workflow | §5 full algorithm descriptions, equations, flowchart, pipeline diagram, justification table | `IPV_Project_Report.md` §5; `METHODOLOGY_FLOWCHARTS.md`; `output/figures/system_pipeline.png` |
| **Implementation & Coding** | 5 | Working code, correctness, tools | Modular `studio/` package, 16+ operations, metrics, GUI | `studio/`; `image_suite.py`; runnable via `.venv` |
| **Results & Analysis** | 5 | Output quality, evaluation, interpretation | 15 comparison figures, metrics CSV, Table 8.1, observations §8.4–8.6 | `output/comparisons/`; `output/metrics_table.csv`; Report §8 |
| **Innovation / Complexity** | 2 | Originality, advanced techniques | CLAHE, NLM denoise, bilateral, SSIM module, undo/chaining, asset generator | Report §9; `studio/metrics.py` |
| **Report & Documentation** | 3 | Structure, clarity, completeness | Full 11-section IPV report + README + this checklist | `IPV_Project_Report.md` |
| **Presentation / Viva** | 1 | Explanation and Q&A | Viva Q&A with code walkthrough | `VIVA_PREPARATION.md` |

---

## Student Instructions — Task Completion

| # | Instruction | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Clearly define the problem and motivation | ✅ Done | Report §2 Abstract, §3.1–3.2 |
| 2 | Explain methodology with flowchart/pipeline | ✅ Done | Report §5.2 Mermaid flowchart; `system_pipeline.png` |
| 3 | Show input-output images and comparisons | ✅ Done | 15 files in `output/comparisons/`; gallery figure |
| 4 | Use proper tools (Python, OpenCV, etc.) | ✅ Done | Python 3.14, OpenCV 4.13, Tkinter — Report §6.2 |
| 5 | Avoid plagiarism; originality evaluated | ✅ Done | Original implementation; references cited §11 |
| 6 | Be prepared to explain code during viva | ✅ Done | `VIVA_PREPARATION.md` with module map and sample Q&A |
| 7 | Penalty: copying without understanding | ✅ Addressed | Viva guide explains *why* for each algorithm |

---

## Submission Package Checklist

Before final submission, complete these steps:

- [ ] Replace `[Your Name]`, `[Roll No.]`, etc. on cover page (`IPV_Project_Report.md` §1)
- [ ] Export report to Word (Times New Roman 12pt, 1.5 spacing, page numbers)
- [ ] Insert GUI screenshots into §7.4
- [ ] Attach figure images from `Research/output/` with captions
- [ ] Run `python scripts/generate_report_assets.py` to refresh metrics if test image changes
- [ ] Demo live application (`python image_suite.py`) for viva
- [ ] Print or PDF this rubric checklist showing all items ✅

---

## Marks Self-Assessment (for practice)

| Criterion | Self-score (/max) | Notes |
|-----------|-------------------|-------|
| Problem Definition | /4 | |
| Methodology | /5 | |
| Implementation | /5 | |
| Results & Analysis | /5 | |
| Innovation | /2 | |
| Report | /3 | |
| Viva | /1 | |
| **Total** | **/25** | |

*Fill during rehearsal with your guide.*
