# ⬡ Smart Image Enhancement Studio

> An interactive **spatial domain image processing** tool built with Python, OpenCV, and Tkinter - designed for academic demonstration of foundational DIP/IPV concepts.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=flat-square&logo=opencv)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)
![UI](https://img.shields.io/badge/UI-Tkinter-orange?style=flat-square)

---

## 📌 Overview

**Smart Image Enhancement Studio** is a desktop GUI application that demonstrates core **spatial domain image processing** techniques through a clean, dark-themed interface. Load any image, apply filters and enhancements in real time, compare the before/after result side by side, and export the output - all without writing a single line of code.

Built for **Digital Image Processing (DIP) / Image Processing & Vision (IPV)** coursework.

---

## ✨ Features

| Feature | Technique | Description |
|---|---|---|
| **Brightness Control** | Intensity Transformation | Shifts all pixel values by a constant `β` |
| **Contrast Adjustment** | Intensity Transformation | Scales pixel values by a factor `α` |
| **Histogram Equalization** | Histogram Processing | Redistributes intensity values via YCrCb (colour-safe) |
| **Gaussian Blur** | Spatial Smoothing | Reduces noise using a 7×7 Gaussian kernel |
| **Laplacian Sharpen** | Spatial Sharpening | Enhances edges using a high-pass 3×3 kernel |
| **Histogram View** | Analysis | Plots R/G/B channel distributions in-app |
| **Before / After View** | Comparison | Side-by-side original vs. processed display |
| **Export** | Output | Save processed image as PNG / JPEG / BMP |

---

## 🖥️ UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  ⬡  Smart Image Enhancement Studio  - Spatial Domain  [Load]   │
├──────────────────┬──────────────────────────────────────────────┤
│  🎛️ Intensity    │  ORIGINAL              PROCESSED             │
│  ─────────────   │                                              │
│  Brightness  [0] │  ┌──────────────┐  ┌──────────────┐          │
│  [====|=====]    │  │              │  │              │          │
│  Contrast [100]  │  │   image.jpg  │  │  (filtered)  │          │
│  [========|=]    │  │              │  │              │          │
│  [⚡ Apply]      │  └──────────────┘  └──────────────┘          │
│                  │                                              │
│  🔬 Filters      │                          [💾 Save Processed] │
│  [📊 Hist EQ]    ├──────────────────────────────────────────────┤
│  [〜 Blur]       │  Status: Loaded photo.png | 1920×1080 px     │
│  [△ Sharpen]     └─────────────────────────────────────────────┘
│                  
│  📈 Histogram    
│  [Original][Proc]
│  ┌──────────┐   
│  │ R G B ~  │   
│  └──────────┘   
│                  
│  [↺ Reset]       
└──────────────────
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.8+**
- `tkinter` - Ships with Python (check below if missing)

### Install Dependencies

```bash
pip install opencv-python pillow matplotlib
```

> **Linux users:** If `tkinter` is missing, install it via:
> ```bash
> sudo pacman -S tk
> ```

### Run the App

```bash
python image_suite.py
```

---

## 🧠 Concepts Explained

### Intensity Transformations
The brightness and contrast controls use OpenCV's `convertScaleAbs`:

```
g(x, y) = α · f(x, y) + β
```

- `α` (contrast) - scales pixel intensity (range: `0.1×` to `3.0×`)
- `β` (brightness) - shifts pixel intensity (range: `-100` to `+100`)

---

### Histogram Equalization
Improves global contrast by redistributing pixel intensities:

```
s = T(r) = (L-1) · CDF(r)
```

Applied on the **Y (luminance) channel** in YCrCb colour space to avoid colour distortion.

---

### Gaussian Blur (Smoothing)
Convolves the image with a Gaussian kernel to suppress high-frequency noise:

```
G(x, y) = (1 / 2πσ²) · e^(-(x² + y²) / 2σ²)
```

Kernel size: **7×7**, σ computed automatically by OpenCV.

---

### Laplacian Sharpening
Enhances edges by amplifying high-frequency components using a high-pass kernel:

```
kernel = [[ 0, -1,  0],
          [-1,  5, -1],
          [ 0, -1,  0]]
```

Applied via `cv2.filter2D` (2D convolution in spatial domain).

---

## 📁 Project Structure

```
Image Suite/
├── image_suite.py   # Main application - all UI and processing logic
└── README.md        # This file
```

---

## 🛠️ Tech Stack

| Library | Role |
|---|---|
| `opencv-python` | Image I/O, processing operations, histogram computation |
| `Pillow` | Converting OpenCV arrays → Tkinter-compatible images |
| `matplotlib` | Rendering inline RGB channel histograms |
| `tkinter` | Native desktop GUI framework (built into Python) |
| `numpy` | Convolution kernel construction |

---

## 📄 License

MIT - free to use, modify, and distribute for academic or personal purposes.
