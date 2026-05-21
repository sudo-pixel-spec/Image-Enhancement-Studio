# Viva Voce Preparation Guide
## Smart Image Enhancement Studio

Use this document to prepare for the **Presentation / Viva (1 mark)** section of the evaluation rubric.

---

## 1. Elevator Pitch (30 seconds)

> "Smart Image Enhancement Studio is a Python-OpenCV desktop application for **spatial domain** image processing. Users load an image, apply classical filters—intensity transforms, histogram methods, smoothing, sharpening, and edge detection—and see **before/after comparison** with **PSNR and SSIM metrics** in real time. The code is modular: processing, state, metrics, and UI are separated for clarity and testing."

---

## 2. Code Walkthrough Map

| If examiner asks… | Open this file | Explain… |
|-------------------|----------------|----------|
| "Where does processing happen?" | `studio/processing.py` | Stateless `ImageProcessor` class; each method = one algorithm |
| "How is undo implemented?" | `studio/state.py` | `ImageDocument._undo` / `_redo` lists of numpy copies, max 30 |
| "How do you compute PSNR?" | `studio/metrics.py` | `PSNR = 10 log10(255²/MSE)`; SSIM uses Gaussian window |
| "How is UI built?" | `studio/app.py` | Tkinter frames; `ScrollableFrame` sidebar; debounced preview |
| "Entry point?" | `image_suite.py` | Creates `tk.Tk()`, runs `ImageSuite` |

---

## 3. Expected Questions & Answers

### Q1: What is spatial domain image processing?

**A:** Operations where output pixel values are computed from input pixels in the **same coordinate space**—either at the same location (point operations like brightness) or in a local neighbourhood (convolution masks for blur/sharpen/edges). Contrast with **frequency domain** where the image is transformed (e.g., FFT) and filters applied on spectrum.

### Q2: Why use YCrCb for histogram equalization?

**A:** Equalizing all BGR channels independently shifts colours unpredictably. The **Y channel** represents luminance; equalizing only Y expands contrast while **Cr/Cb** preserve chrominance → more natural results.

### Q3: Difference between histogram equalization and CLAHE?

**A:** Global HE uses the full image histogram—can over-amplify noise in flat regions. **CLAHE** divides the image into tiles, equalizes locally with a **clip limit** on histogram height, then interpolates—better for local contrast without extreme noise boost.

### Q4: What is PSNR? When is it misleading?

**A:** Peak Signal-to-Noise Ratio: \(10\log_{10}(255^2/\text{MSE})\). Higher = closer pixel values to reference. **Misleading** when intentional large changes are desired (edge maps, artistic colour grading) because large MSE does not mean "bad" output.

### Q5: What is SSIM?

**A:** Structural Similarity Index—compares luminance, contrast, and structure using local windows. Range ~[0,1]; 1 = identical. Better correlated with perceived quality than MSE for structural preservation (e.g., unsharp mask SSIM 0.83 on our test).

### Q6: Explain Laplacian sharpening kernel.

**A:** Kernel `[0,-1,0; -1,5,-1; 0,-1,0]` is a discrete Laplacian high-pass filter added back to the image. Centre weight 5 = original + 4×(original − blurred neighbour average) → edges enhanced.

### Q7: Gaussian vs. median vs. bilateral blur?

**A:**
- **Gaussian:** linear, smooth, reduces high-frequency noise; blurs edges.
- **Median:** non-linear order statistic; excellent for salt-and-pepper; preserves edges better than Gaussian.
- **Bilateral:** averages only similar-intensity neighbours; **edge-preserving**; slower but keeps boundaries sharp.

### Q8: How does Canny edge detection work?

**A:** (1) Gaussian smooth, (2) Sobel gradients, (3) non-maximum suppression thinning edges, (4) double threshold with hysteresis to link strong/weak edges—produces thin, connected binary edges.

### Q9: What is "apply from original vs. current result"?

**A:** **Original** — each filter uses the loaded source image (independent experiments). **Current result** — filter chains on the processed buffer (e.g., blur then sharpen the blurred image). Demonstrates pipeline composition.

### Q10: Why modular architecture?

**A:** Separates concerns for **testing** (`ImageProcessor` without GUI), **maintainability** (add filter in one file), and **viva clarity** (examiner can navigate small files). Matches software engineering practice beyond a single script.

---

## 4. Live Demo Script (3 minutes)

1. **Load** `Research/output/samples/input_test.png`
2. Show **original | processed** panels
3. Apply **CLAHE** → point to expanded contrast, PSNR ~27 dB in status bar
4. **Undo** → restored
5. Switch apply source to **Current result** → apply **Unsharp mask** on CLAHE output
6. Open **Processed histogram** → broader luminance spread
7. Apply **Canny** → explain low SSIM is expected
8. **Save** output → confirm file on disk

---

## 5. Technical Definitions Cheat Sheet

| Term | One-line definition |
|------|---------------------|
| α, β | Contrast scale and brightness offset in linear transform |
| γ | Gamma exponent for nonlinear tone mapping |
| MSE | Mean squared pixel difference between two images |
| NLM | Non-local means denoising using similar patches |
| Unsharp mask | Sharpen by adding scaled difference from blurred copy |
| Adaptive threshold | Threshold varies per pixel neighbourhood |
| BGR | OpenCV channel order (Blue, Green, Red) |

---

## 6. Honesty Points (if asked about limitations)

- No FFT/frequency filters in current version
- PSNR/SSIM always compare to **original**, not a ground-truth restored image
- Large images may lag with live preview enabled
- Test results used synthetic image; real photographs may show different metric ranges

---

## 7. Files to Have Open During Viva

1. `studio/processing.py` — algorithms
2. `studio/metrics.py` — PSNR/SSIM
3. `Research/output/metrics_table.csv` — numerical results
4. `Research/output/comparisons/05_clahe.png` — visual example
5. `IPV_Project_Report.md` — report sections for cross-reference

---

*Practice explaining each algorithm in your own words — the rubric penalizes copying without understanding.*
