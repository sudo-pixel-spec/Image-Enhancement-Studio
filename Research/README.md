# Research Folder — IPV Project Deliverables

This folder contains course requirements from `Image_Processing_Project_Rubric.pdf` and `IPV_Project Report Format.pdf`, plus **completed deliverables** for submission.

---

## Source documents (requirements)

| File | Purpose |
|------|---------|
| `Image_Processing_Project_Rubric.pdf` | 25-mark evaluation criteria + student instructions |
| `IPV_Project Report Format.pdf` | Required 11-section report structure |

---

## Completed deliverables

| File / Folder | Maps to |
|---------------|---------|
| **`IPV_Project_Report.md`** | Full report — all 11 sections (export to Word for submission) |
| **`RUBRIC_COMPLIANCE.md`** | Every rubric criterion + instruction marked complete |
| **`METHODOLOGY_FLOWCHARTS.md`** | Flowcharts, block diagrams, step-by-step process |
| **`VIVA_PREPARATION.md`** | Q&A, demo script, code walkthrough |
| **`output/`** | Generated figures, metrics, comparisons |

### Generated assets (`output/`)

```
output/
├── comparisons/          # 15 input vs output side-by-side figures
├── figures/
│   ├── system_pipeline.png
│   └── operations_gallery.png
├── histograms/
│   ├── input_histogram.png
│   └── clahe_histogram.png
├── samples/              # Test images (input + all operations)
└── metrics_table.csv     # PSNR, SSIM, MSE for each operation
```

Regenerate assets:

```bash
.venv/bin/python scripts/generate_report_assets.py
```

---

## Before submission

1. Edit cover page placeholders in `IPV_Project_Report.md` §1
2. Export report to Word (Times New Roman 12pt, 1.5 spacing)
3. Insert figures from `output/` with captions
4. Add GUI screenshots to §7.4
5. Review `RUBRIC_COMPLIANCE.md` checklist
6. Rehearse using `VIVA_PREPARATION.md`
