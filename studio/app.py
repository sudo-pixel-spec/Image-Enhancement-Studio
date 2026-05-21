from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Optional

import cv2
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox, ttk

from studio.metrics import compute_metrics
from studio.processing import ApplySource, ImageProcessor
from studio.state import ImageDocument
from studio.theme import Theme
from studio.widgets import (
    ScrollableFrame,
    SliderRow,
    build_ttk_styles,
    divider,
    flat_button,
    section_head,
)


class ImageSuite:
    """Smart Image Enhancement Studio — desktop spatial-domain editor."""

    DEBOUNCE_MS = 120

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Smart Image Enhancement Studio")
        self.root.geometry("1360x880")
        self.root.minsize(1024, 720)
        self.root.configure(bg=Theme.BG_DARK.value)

        self.doc = ImageDocument()
        self._preview_job: Optional[str] = None
        self._live_preview = tk.BooleanVar(value=True)

        build_ttk_styles(root)
        self._build_ui()
        self._bind_shortcuts()

    # --------- UI --------------------------------------------------------------

    def _build_ui(self) -> None:
        self._build_header()
        self._build_statusbar()

        body = tk.Frame(self.root, bg=Theme.BG_DARK.value)
        body.pack(fill="both", expand=True, padx=10, pady=(6, 4))

        scroll = ScrollableFrame(body, width=300)
        scroll.pack(fill="y", side="left", padx=(0, 8))
        self._build_sidebar(scroll.inner)

        center = tk.Frame(body, bg=Theme.BG_DARK.value)
        center.pack(fill="both", expand=True, side="left")
        self._build_canvas_area(center)

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=Theme.BG_PANEL.value, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⬡",
            bg=Theme.BG_PANEL.value,
            fg=Theme.ACCENT.value,
            font=(Theme.FONT.value, 22, "bold"),
        ).pack(side="left", padx=(20, 8), pady=8)
        tk.Label(
            header,
            text="Smart Image Enhancement Studio",
            bg=Theme.BG_PANEL.value,
            fg=Theme.TEXT_PRI.value,
            font=(Theme.FONT.value, 15, "bold"),
        ).pack(side="left", pady=8)
        tk.Label(
            header,
            text="Spatial Domain · v2",
            bg=Theme.BG_PANEL.value,
            fg=Theme.TEXT_SEC.value,
            font=(Theme.FONT.value, 10),
        ).pack(side="left", padx=6, pady=8)

        btn_frame = tk.Frame(header, bg=Theme.BG_PANEL.value)
        btn_frame.pack(side="right", padx=12)
        flat_button(btn_frame, "↶ Undo", self._undo, "#334155", side="left", padx=4)
        flat_button(btn_frame, "↷ Redo", self._redo, "#334155", side="left", padx=4)
        flat_button(
            btn_frame, "📂 Load", self._load_image, Theme.ACCENT.value, side="left", padx=4
        )

    def _build_statusbar(self) -> None:
        self.status_var = tk.StringVar(
            value="No image loaded — Load Image or press Ctrl+O"
        )
        bar = tk.Frame(self.root, bg=Theme.BG_PANEL.value, height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        tk.Label(
            bar,
            textvariable=self.status_var,
            bg=Theme.BG_PANEL.value,
            fg=Theme.TEXT_SEC.value,
            font=(Theme.FONT.value, 8),
        ).pack(side="left", padx=12)
        self.hist_info = tk.StringVar(value="")
        tk.Label(
            bar,
            textvariable=self.hist_info,
            bg=Theme.BG_PANEL.value,
            fg=Theme.ACCENT2.value,
            font=(Theme.FONT_MONO.value, 8),
        ).pack(side="right", padx=12)

    def _build_sidebar(self, parent: tk.Widget) -> None:
        section_head(parent, "⚙️  Apply From").pack(fill="x", padx=12, pady=(10, 2))
        src_frame = tk.Frame(parent, bg=Theme.BG_PANEL.value)
        src_frame.pack(fill="x", padx=12, pady=2)
        self._apply_src_var = tk.StringVar(value="original")
        for text, val in (("Original", "original"), ("Current result", "processed")):
            tk.Radiobutton(
                src_frame,
                text=text,
                variable=self._apply_src_var,
                value=val,
                command=self._on_apply_source_changed,
                bg=Theme.BG_PANEL.value,
                fg=Theme.TEXT_PRI.value,
                selectcolor=Theme.BG_CARD.value,
                activebackground=Theme.BG_PANEL.value,
                font=(Theme.FONT.value, 9),
            ).pack(anchor="w")

        tk.Checkbutton(
            parent,
            text="Live preview (intensity)",
            variable=self._live_preview,
            bg=Theme.BG_PANEL.value,
            fg=Theme.TEXT_SEC.value,
            selectcolor=Theme.BG_CARD.value,
            activebackground=Theme.BG_PANEL.value,
            font=(Theme.FONT.value, 8),
        ).pack(anchor="w", padx=12, pady=2)

        divider(parent)
        section_head(parent, "🎛️  Intensity").pack(fill="x", padx=12, pady=(4, 2))

        self.bright = SliderRow(
            parent, "Brightness", -100, 100, 0, on_change=self._schedule_intensity_preview
        )
        self.contrast = SliderRow(
            parent, "Contrast %", 10, 300, 100, on_change=self._schedule_intensity_preview
        )
        self.gamma = SliderRow(
            parent,
            "Gamma",
            10,
            300,
            100,
            resolution=1,
            on_change=self._schedule_intensity_preview,
        )
        self.saturation = SliderRow(
            parent,
            "Saturation %",
            0,
            200,
            100,
            on_change=self._schedule_intensity_preview,
        )

        apply_f = tk.Frame(parent, bg=Theme.BG_PANEL.value)
        apply_f.pack(fill="x", padx=12, pady=(2, 6))
        flat_button(
            apply_f, "⚡ Apply Intensity", self._apply_intensity, Theme.ACCENT.value, fill="x"
        )

        divider(parent)
        section_head(parent, "🔬  Enhancement").pack(fill="x", padx=12, pady=(4, 2))
        pad = dict(padx=12, pady=2)
        self._filter_btn(parent, "📊 Hist Equalize", self._hist_eq, "#0e7490", **pad)
        self._filter_btn(parent, "📊 CLAHE (adaptive)", self._clahe, "#155e75", **pad)
        self._filter_btn(parent, "✨ Unsharp Mask", self._unsharp, "#7c3aed", **pad)
        self._filter_btn(parent, "△ Laplacian Sharpen", self._sharpen, "#6d28d9", **pad)
        self._filter_btn(parent, "🔇 Denoise (NLM)", self._denoise, "#0369a1", **pad)

        divider(parent)
        section_head(parent, "〜  Smoothing").pack(fill="x", padx=12, pady=(4, 2))
        self.blur_k = SliderRow(parent, "Blur kernel", 3, 21, 7)
        self._filter_btn(parent, "Gaussian Blur", self._blur, "#065f46", **pad)
        self._filter_btn(parent, "Median Blur", self._median, "#047857", **pad)
        self._filter_btn(parent, "Bilateral (edge-safe)", self._bilateral, "#059669", **pad)

        divider(parent)
        section_head(parent, "🎨  Color & Tone").pack(fill="x", padx=12, pady=(4, 2))
        self._filter_btn(parent, "Grayscale", self._grayscale, "#475569", **pad)
        self._filter_btn(parent, "Sepia", self._sepia, "#78350f", **pad)
        self._filter_btn(parent, "Invert", self._invert, "#1e293b", **pad)

        divider(parent)
        section_head(parent, "📐  Geometry").pack(fill="x", padx=12, pady=(4, 2))
        geo = tk.Frame(parent, bg=Theme.BG_PANEL.value)
        geo.pack(fill="x", padx=12, pady=2)
        flat_button(geo, "↻ 90° CW", lambda: self._rotate(True), "#334155", side="left", expand=True, fill="x", padx=(0, 2))
        flat_button(geo, "↺ 90° CCW", lambda: self._rotate(False), "#334155", side="left", expand=True, fill="x", padx=2)
        geo2 = tk.Frame(parent, bg=Theme.BG_PANEL.value)
        geo2.pack(fill="x", padx=12, pady=2)
        flat_button(geo2, "↔ Flip H", lambda: self._flip(True), "#334155", side="left", expand=True, fill="x", padx=(0, 2))
        flat_button(geo2, "↕ Flip V", lambda: self._flip(False), "#334155", side="left", expand=True, fill="x", padx=2)

        divider(parent)
        section_head(parent, "🔍  Analysis").pack(fill="x", padx=12, pady=(4, 2))
        self._filter_btn(parent, "Canny Edges", self._canny, "#4c1d95", **pad)
        self._filter_btn(parent, "Sobel Magnitude", self._sobel, "#5b21b6", **pad)
        self._filter_btn(parent, "Adaptive Threshold", self._threshold, "#312e81", **pad)

        divider(parent)
        section_head(parent, "📈  Histogram").pack(fill="x", padx=12, pady=(4, 2))
        hist_t = tk.Frame(parent, bg=Theme.BG_PANEL.value)
        hist_t.pack(fill="x", padx=12, pady=3)
        flat_button(
            hist_t, "Original", self._show_hist_original, "#1e3a5f", side="left", expand=True, fill="x", padx=(0, 2)
        )
        flat_button(
            hist_t, "Processed", self._show_hist_processed, "#1e3a5f", side="left", expand=True, fill="x", padx=(2, 0)
        )
        self.hist_frame = tk.Frame(parent, bg=Theme.BG_CARD.value, height=150)
        self.hist_frame.pack(fill="x", padx=12, pady=4)
        self.hist_frame.pack_propagate(False)
        tk.Label(
            self.hist_frame,
            text="Load an image to view histogram",
            bg=Theme.BG_CARD.value,
            fg=Theme.TEXT_SEC.value,
            font=(Theme.FONT.value, 9),
        ).pack(expand=True)

        divider(parent)
        flat_button(
            parent, "↺ Reset to Original", self._reset, Theme.DANGER.value, fill="x", padx=12, pady=10
        )

    def _filter_btn(
        self, parent: tk.Widget, text: str, cmd: Callable[[], None], color: str, **pack
    ) -> None:
        flat_button(parent, text, cmd, color, fill="x", **pack)

    def _build_canvas_area(self, parent: tk.Widget) -> None:
        label_row = tk.Frame(parent, bg=Theme.BG_DARK.value)
        label_row.pack(fill="x", pady=(0, 4))
        tk.Label(
            label_row,
            text="ORIGINAL",
            bg=Theme.BG_DARK.value,
            fg=Theme.TEXT_SEC.value,
            font=(Theme.FONT.value, 9, "bold"),
        ).pack(side="left", padx=(4, 0))
        tk.Label(
            label_row,
            text="PROCESSED",
            bg=Theme.BG_DARK.value,
            fg=Theme.SUCCESS.value,
            font=(Theme.FONT.value, 9, "bold"),
        ).pack(side="right", padx=(0, 4))

        img_row = tk.Frame(parent, bg=Theme.BG_DARK.value)
        img_row.pack(fill="both", expand=True)

        left = tk.Frame(img_row, bg=Theme.BG_CARD.value)
        left.pack(fill="both", expand=True, side="left", padx=(0, 4))
        self.canvas_orig = tk.Label(
            left,
            bg=Theme.BG_CARD.value,
            text="No image loaded\n\nCtrl+O to open",
            fg=Theme.TEXT_SEC.value,
            font=(Theme.FONT.value, 11),
            anchor="center",
        )
        self.canvas_orig.pack(fill="both", expand=True, padx=6, pady=6)

        right = tk.Frame(img_row, bg=Theme.BG_CARD.value)
        right.pack(fill="both", expand=True, side="left", padx=(4, 0))
        self.canvas_proc = tk.Label(
            right,
            bg=Theme.BG_CARD.value,
            text="Apply a filter or adjust intensity",
            fg=Theme.TEXT_SEC.value,
            font=(Theme.FONT.value, 11),
            anchor="center",
        )
        self.canvas_proc.pack(fill="both", expand=True, padx=6, pady=6)

        actions = tk.Frame(parent, bg=Theme.BG_DARK.value)
        actions.pack(fill="x", pady=(4, 0))
        flat_button(
            actions,
            "💾 Save Processed",
            self._save_image,
            "#064e3b",
            side="right",
            padx=4,
        )
        flat_button(
            actions,
            "📋 Copy settings → Original",
            self._promote_processed_to_original,
            "#1e40af",
            side="right",
            padx=4,
        )

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-o>", lambda e: self._load_image())
        self.root.bind("<Control-s>", lambda e: self._save_image())
        self.root.bind("<Control-z>", lambda e: self._undo())
        self.root.bind("<Control-y>", lambda e: self._redo())
        self.root.bind("<Control-Shift-Z>", lambda e: self._redo())
        self.root.bind("<Control-r>", lambda e: self._reset())



    # ------------- Apply source & intensity preview ---------------------------------

    def _on_apply_source_changed(self) -> None:
        src = (
            ApplySource.PROCESSED
            if self._apply_src_var.get() == "processed"
            else ApplySource.ORIGINAL
        )
        self.doc.apply_source = src
        self.status_var.set(
            f"Apply from: {'current result' if src == ApplySource.PROCESSED else 'original'}"
        )

    def _schedule_intensity_preview(self, _value: float) -> None:
        if not self._live_preview.get() or not self.doc.has_image:
            return
        if self._preview_job:
            self.root.after_cancel(self._preview_job)
        self._preview_job = self.root.after(self.DEBOUNCE_MS, self._preview_intensity)

    def _preview_intensity(self) -> None:
        self._preview_job = None
        if not self.doc.has_image:
            return
        result = self._compute_intensity(self.doc.working_copy())
        self._display(self.canvas_proc, result)

    def _compute_intensity(self, base: np.ndarray) -> np.ndarray:
        alpha = self.contrast.get() / 100.0
        beta = int(self.bright.get())
        out = ImageProcessor.brightness_contrast(base, alpha, beta)
        gamma = max(self.gamma.get() / 100.0, 0.1)
        out = ImageProcessor.gamma(out, gamma)
        sat = self.saturation.get() / 100.0
        return ImageProcessor.saturation(out, sat)

    # ------------- Image I/O -------------------------------------------------------------------

    def _load_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp"),
                ("All", "*.*"),
            ],
        )
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error", "Could not read the selected file.")
            return

        self.doc.load(img)
        self._refresh_views()
        w, h = self.doc.dimensions or (0, 0)
        name = Path(path).name
        size_kb = os.path.getsize(path) / 1024
        self.status_var.set(f"Loaded: {name}  |  {w}×{h} px  |  {size_kb:.0f} KB")
        self._reset_intensity_sliders()

    def _display(self, label: tk.Label, bgr: np.ndarray) -> None:
        label.update_idletasks()
        w = max(label.winfo_width(), 400)
        h = max(label.winfo_height(), 320)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil.thumbnail((w - 12, h - 12), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil)
        label.config(image=tk_img, text="")
        label.image = tk_img  # type: ignore[attr-defined]

    def _refresh_views(self) -> None:
        if self.doc.original_bgr is not None:
            self._display(self.canvas_orig, self.doc.original_bgr)
        if self.doc.processed_bgr is not None:
            self._display(self.canvas_proc, self.doc.processed_bgr)

    def _require_image(self) -> bool:
        if not self.doc.has_image:
            messagebox.showwarning("No Image", "Please load an image first (Ctrl+O).")
            return False
        return True

    def _apply_op(self, fn: Callable[[np.ndarray], np.ndarray], status: str) -> None:
        if not self._require_image():
            return
        base = self.doc.working_copy()
        self.doc.commit(fn(base))
        self._refresh_views()
        self.status_var.set(status)
        self._update_hist_info()

    # -------------- Operations ---------------------------------------------

    def _apply_intensity(self) -> None:
        if not self._require_image():
            return
        result = self._compute_intensity(self.doc.working_copy())
        self.doc.commit(result)
        self._refresh_views()
        self.status_var.set("Intensity pipeline applied (brightness, contrast, gamma, saturation)")

    def _hist_eq(self) -> None:
        self._apply_op(ImageProcessor.histogram_equalize, "Histogram equalization (YCrCb)")

    def _clahe(self) -> None:
        self._apply_op(
            lambda img: ImageProcessor.clahe(img, 2.0, 8),
            "CLAHE applied (clip=2.0, tile=8×8)",
        )

    def _unsharp(self) -> None:
        self._apply_op(
            lambda img: ImageProcessor.unsharp_mask(img, 1.2, 1.0),
            "Unsharp mask sharpening",
        )

    def _sharpen(self) -> None:
        self._apply_op(ImageProcessor.laplacian_sharpen, "Laplacian sharpen (3×3)")

    def _denoise(self) -> None:
        self._apply_op(lambda img: ImageProcessor.denoise(img, 8), "Non-local means denoise")

    def _blur(self) -> None:
        k = int(self.blur_k.get())
        self._apply_op(
            lambda img: ImageProcessor.gaussian_blur(img, k),
            f"Gaussian blur (kernel {k}×{k})",
        )

    def _median(self) -> None:
        k = int(self.blur_k.get())
        self._apply_op(
            lambda img: ImageProcessor.median_blur(img, k),
            f"Median blur (kernel {k}×{k})",
        )

    def _bilateral(self) -> None:
        self._apply_op(ImageProcessor.bilateral, "Bilateral filter (edge-preserving)")

    def _grayscale(self) -> None:
        self._apply_op(ImageProcessor.grayscale, "Grayscale")

    def _sepia(self) -> None:
        self._apply_op(ImageProcessor.sepia, "Sepia tone")

    def _invert(self) -> None:
        self._apply_op(ImageProcessor.invert, "Colors inverted")

    def _rotate(self, clockwise: bool) -> None:
        if not self._require_image() or self.doc.processed_bgr is None:
            return
        result = ImageProcessor.rotate_90(self.doc.processed_bgr, clockwise)
        self.doc.sync_original_after_geometry(result)
        self._refresh_views()
        self.status_var.set("Rotated 90° (original updated)")

    def _flip(self, horizontal: bool) -> None:
        if not self._require_image() or self.doc.processed_bgr is None:
            return
        result = ImageProcessor.flip(self.doc.processed_bgr, horizontal)
        self.doc.sync_original_after_geometry(result)
        self._refresh_views()
        self.status_var.set("Flipped (original updated)")

    def _canny(self) -> None:
        self._apply_op(
            lambda img: ImageProcessor.canny_edges(img, 50, 150),
            "Canny edge detection",
        )

    def _sobel(self) -> None:
        self._apply_op(ImageProcessor.sobel_edges, "Sobel gradient magnitude")

    def _threshold(self) -> None:
        self._apply_op(
            lambda img: ImageProcessor.adaptive_threshold(img, 11, 2),
            "Adaptive threshold (Gaussian)",
        )

    def _undo(self) -> None:
        if self.doc.undo():
            self._refresh_views()
            self.status_var.set("Undo")

        elif self.doc.has_image:
            self.status_var.set("Nothing to undo")

    def _redo(self) -> None:
        if self.doc.redo():
            self._refresh_views()
            self.status_var.set("Redo")
        elif self.doc.has_image:
            self.status_var.set("Nothing to redo")

    def _reset(self) -> None:
        if not self._require_image():
            return
        self.doc.reset_processed()
        self._refresh_views()
        self._reset_intensity_sliders()
        self.status_var.set("Reset to original")

    def _reset_intensity_sliders(self) -> None:
        self.bright.set(0)
        self.contrast.set(100)
        self.gamma.set(100)
        self.saturation.set(100)

    def _promote_processed_to_original(self) -> None:
        if not self._require_image() or self.doc.processed_bgr is None:
            return
        if messagebox.askyesno(
            "Promote Result",
            "Replace the original image with the current processed result?\n"
            "This clears undo history.",
        ):
            self.doc.load(self.doc.processed_bgr)
            self._refresh_views()
            self.status_var.set("Processed image promoted to original")

    # ------------- Histogram ----------------------------------------------------------

    def _draw_histogram(self, bgr: np.ndarray, title: str) -> None:
        for w in self.hist_frame.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(2.8, 1.6), dpi=80)
        fig.patch.set_facecolor(Theme.BG_CARD.value)
        ax.set_facecolor("#131722")

        for i, (col, lbl) in enumerate(
            zip(("#f87171", "#4ade80", "#60a5fa"), ("R", "G", "B"))
        ):
            hist = cv2.calcHist([bgr], [i], None, [256], [0, 256])
            ax.plot(hist, color=col, linewidth=0.9, label=lbl)

        ax.set_xlim(0, 256)
        ax.tick_params(colors=Theme.TEXT_SEC.value, labelsize=5)
        for spine in ax.spines.values():
            spine.set_color(Theme.DIVIDER.value)
        ax.set_title(title, color=Theme.ACCENT2.value, fontsize=7, pad=3)
        ax.legend(
            fontsize=5,
            loc="upper right",
            facecolor=Theme.BG_CARD.value,
            labelcolor=Theme.TEXT_PRI.value,
        )
        fig.tight_layout(pad=0.4)

        canvas = FigureCanvasTkAgg(fig, master=self.hist_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _show_hist_original(self) -> None:
        if self._require_image() and self.doc.original_bgr is not None:
            self._draw_histogram(self.doc.original_bgr, "Original")
            self.status_var.set("Histogram: original")

    def _show_hist_processed(self) -> None:
        if self._require_image() and self.doc.processed_bgr is not None:
            self._draw_histogram(self.doc.processed_bgr, "Processed")
            self.status_var.set("Histogram: processed")

    def _update_hist_info(self) -> None:
        if self.doc.processed_bgr is None or self.doc.original_bgr is None:
            return
        m = compute_metrics(self.doc.original_bgr, self.doc.processed_bgr)
        psnr = f"{m.psnr_db:.1f} dB" if m.psnr_db != float("inf") else "∞"
        self.hist_info.set(
            f"PSNR={psnr}  SSIM={m.ssim:.3f}  μ={m.mean_intensity:.1f}  σ={m.std_intensity:.1f}"
        )



    # ---- Save ---------------------------------------------------------------

    def _save_image(self) -> None:
        if self.doc.processed_bgr is None:
            messagebox.showwarning("Nothing to Save", "Process an image first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Processed Image",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("WebP", "*.webp"),
                ("BMP", "*.bmp"),
            ],
        )
        if not path:
            return
        ext = Path(path).suffix.lower()
        params = []
        if ext in (".jpg", ".jpeg"):
            params = [cv2.IMWRITE_JPEG_QUALITY, 95]
        elif ext == ".webp":
            params = [cv2.IMWRITE_WEBP_QUALITY, 90]
        cv2.imwrite(path, self.doc.processed_bgr, params)
        self.status_var.set(f"Saved → {Path(path).name}")
        messagebox.showinfo("Saved", f"Image saved to:\n{path}")
