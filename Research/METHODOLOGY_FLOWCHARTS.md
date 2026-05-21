# Methodology Flowcharts & Block Diagrams
## Smart Image Enhancement Studio

Required by: **IPV Project Report Format** (§5) and **Evaluation Rubric** (methodology + workflow).

---

## 1. Overall System Pipeline

![System Pipeline](output/figures/system_pipeline.png)

**Caption (for report):** *Figure 1 — Block diagram of the Smart Image Enhancement Studio processing pipeline from image load to export.*

---

## 2. Main Application Flowchart

```mermaid
flowchart TD
    START([Application Start]) --> INIT[Initialize Tkinter UI<br/>ImageDocument, styles]
    INIT --> WAIT{User event}
    WAIT -->|Load Ctrl+O| LOAD[cv2.imread path]
    LOAD --> VALID{Valid image?}
    VALID -->|No| ERR[Show error dialog]
    ERR --> WAIT
    VALID -->|Yes| STORE[doc.load: copy to<br/>original + processed]
    STORE --> DISP[Display both panels]
    DISP --> WAIT
    WAIT -->|Slider move| LIVE{Live preview on?}
    LIVE -->|Yes| PREV[Debounce 120ms<br/>preview intensity only]
    PREV --> WAIT
    LIVE -->|No| WAIT
    WAIT -->|Apply / Filter| SRC{Apply source?}
    SRC -->|Original| BASE1[working_copy from original_bgr]
    SRC -->|Processed| BASE2[working_copy from processed_bgr]
    BASE1 --> OP[ImageProcessor operation]
    BASE2 --> OP
    OP --> COMMIT[doc.commit + undo stack]
    COMMIT --> MET[compute_metrics vs original]
    MET --> UPD[Refresh processed canvas<br/>Update PSNR/SSIM bar]
    UPD --> WAIT
    WAIT -->|Undo Ctrl+Z| UNDO[Pop undo stack]
    UNDO --> DISP
    WAIT -->|Save Ctrl+S| SAVE[cv2.imwrite]
    SAVE --> WAIT
    WAIT -->|Exit| END([Close application])
```

---

## 3. Intensity Processing Pipeline

```mermaid
flowchart LR
    IN[BGR Input] --> BC[convertScaleAbs<br/>α, β]
    BC --> G[Gamma LUT<br/>γ]
    G --> HSV[BGR → HSV]
    HSV --> SAT[Scale S channel]
    SAT --> BGR[BGR Output]
```

**Equations:**

1. \( g = \alpha f + \beta \)
2. \( s = 255 \cdot (r/255)^{1/\gamma} \)
3. \( S' = \text{clip}(s \cdot S, 0, 255) \)

---

## 4. Histogram Enhancement Pipeline

```mermaid
flowchart TD
    BGR1[BGR Image] --> YCC[cvtColor BGR2YCrCb]
    YCC --> Y[Extract Y channel]
    Y --> EQ{Method?}
    EQ -->|Global| HE[equalizeHist]
    EQ -->|Adaptive| CL[createCLAHE<br/>clip=2, tile=8×8]
    HE --> MERGE[Replace Y channel]
    CL --> MERGE
    MERGE --> BGR2[cvtColor YCrCb2BGR]
```

**Justification:** Chrominance (Cr, Cb) unchanged → natural colours.

---

## 5. Spatial Filtering Classification

```mermaid
flowchart TD
    F[Input f x,y] --> TYPE{Filter type?}
    TYPE -->|Linear smoothing| G[Gaussian / Mean]
    TYPE -->|Non-linear| M[Median]
    TYPE -->|Edge-preserving| B[Bilateral]
    TYPE -->|Sharpening| L[Laplacian kernel]
    TYPE -->|Sharpening| U[Unsharp mask]
    TYPE -->|Edge| C[Canny]
    TYPE -->|Edge| S[Sobel magnitude]
    G --> OUT[Output g x,y]
    M --> OUT
    B --> OUT
    L --> OUT
    U --> OUT
    C --> OUT
    S --> OUT
```

---

## 6. Undo/Redo State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Editing: load image
    Editing --> Editing: commit operation
    note right of Editing: undo stack grows<br/>redo stack cleared
    Editing --> Undoing: Ctrl+Z
    Undoing --> Editing: restore previous processed
    Editing --> Redoing: Ctrl+Y
    Redoing --> Editing: restore from redo stack
    Editing --> Idle: reset / new load
```

---

## 7. Metrics Computation Flow

```mermaid
flowchart LR
    REF[original_bgr] --> ALIGN{Same size?}
    PROC[processed_bgr] --> ALIGN
    ALIGN -->|Resize if needed| MSE[MSE]
    MSE --> PSNR[PSNR dB]
    REF --> SSIM[SSIM per channel<br/>Gaussian window 11]
    PROC --> SSIM
    MSE --> DISP[Status bar display]
    PSNR --> DISP
    SSIM --> DISP
```

---

## 8. Step-by-Step User Process (for report §5)

| Step | Action | Technical detail |
|------|--------|------------------|
| 1 | Launch app | `python image_suite.py` |
| 2 | Load image | `cv2.imread` → BGR NumPy array |
| 3 | Choose apply source | Original or processed buffer |
| 4 | Adjust sliders / click filter | Selected `ImageProcessor` method |
| 5 | View comparison | Left = original, right = processed |
| 6 | Read metrics | PSNR, SSIM, μ, σ in status bar |
| 7 | View histogram | Matplotlib RGB plot in sidebar |
| 8 | Undo if needed | 30-level history |
| 9 | Save result | PNG/JPEG/WebP/BMP export |

---

*Export diagrams: paste Mermaid into [mermaid.live](https://mermaid.live) for PNG/SVG, or use the generated `system_pipeline.png`.*
