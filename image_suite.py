"""
Smart Image Enhancement Studio
================================
Spatial domain image processing tool for IPV/DIP coursework.
Features: Brightness, Contrast, Histogram EQ, Blur, Sharpen, Before/After view.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


# ─────────────────────────────────────────────
#  THEME / PALETTE
# ─────────────────────────────────────────────
BG_DARK   = "#0f1117"
BG_PANEL  = "#1a1d27"
BG_CARD   = "#22263a"
ACCENT    = "#6c63ff"
ACCENT2   = "#a78bfa"
TEXT_PRI  = "#e2e8f0"
TEXT_SEC  = "#94a3b8"
SUCCESS   = "#22d3ee"
WARN      = "#f59e0b"
DANGER    = "#f87171"
BTN_HOVER = "#7c73ff"


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class ImageSuite:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Image Enhancement Studio")
        self.root.geometry("1280x820")
        self.root.minsize(960, 680)
        self.root.configure(bg=BG_DARK)

        # State
        self.original_bgr  = None   # NumPy BGR (from OpenCV)
        self.processed_bgr = None
        self.tk_original   = None
        self.tk_processed  = None
        self._slider_job   = None   # debounce handle
        self.hist_canvas_widget = None

        self._build_styles()
        self._build_ui()

    # ──────────────────────────────────────────
    #  STYLES
    # ──────────────────────────────────────────
    def _build_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("TFrame",       background=BG_DARK)
        style.configure("Card.TFrame",  background=BG_CARD)
        style.configure("Panel.TFrame", background=BG_PANEL)

        style.configure("TLabel",
                        background=BG_DARK, foreground=TEXT_PRI,
                        font=("Segoe UI", 10))
        style.configure("Title.TLabel",
                        background=BG_DARK, foreground=TEXT_PRI,
                        font=("Segoe UI", 18, "bold"))
        style.configure("Sub.TLabel",
                        background=BG_DARK, foreground=TEXT_SEC,
                        font=("Segoe UI", 9))
        style.configure("Card.TLabel",
                        background=BG_CARD, foreground=TEXT_PRI,
                        font=("Segoe UI", 10))
        style.configure("CardSub.TLabel",
                        background=BG_CARD, foreground=TEXT_SEC,
                        font=("Segoe UI", 8))
        style.configure("SectionHead.TLabel",
                        background=BG_PANEL, foreground=ACCENT2,
                        font=("Segoe UI", 10, "bold"))
        style.configure("Panel.TLabel",
                        background=BG_PANEL, foreground=TEXT_SEC,
                        font=("Segoe UI", 9))
        style.configure("Status.TLabel",
                        background=BG_DARK, foreground=TEXT_SEC,
                        font=("Segoe UI", 9))
        style.configure("Value.TLabel",
                        background=BG_CARD, foreground=ACCENT2,
                        font=("Segoe UI", 9, "bold"))

        style.configure("Horizontal.TScale",
                        background=BG_CARD, troughcolor="#2d3148",
                        sliderlength=18, sliderrelief="flat")

        style.configure("TScrollbar",
                        background=BG_PANEL, troughcolor=BG_DARK,
                        arrowcolor=TEXT_SEC)

    # ──────────────────────────────────────────
    #  UI LAYOUT
    # ──────────────────────────────────────────
    def _build_ui(self):
        # ── Header ──────────────────────────────────
        header = tk.Frame(self.root, bg=BG_PANEL, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="⬡", bg=BG_PANEL, fg=ACCENT,
                 font=("Segoe UI", 22, "bold")).pack(side="left", padx=(20,8), pady=8)
        tk.Label(header, text="Smart Image Enhancement Studio",
                 bg=BG_PANEL, fg=TEXT_PRI,
                 font=("Segoe UI", 15, "bold")).pack(side="left", pady=8)
        tk.Label(header, text="— Spatial Domain Processing",
                 bg=BG_PANEL, fg=TEXT_SEC,
                 font=("Segoe UI", 10)).pack(side="left", padx=6, pady=8)

        # Upload button in header
        self._make_btn(header, "📂  Load Image", self._load_image,
                       ACCENT, side="right", padx=(0,20))

        # ── Status bar ──────────────────────────────
        self.status_var = tk.StringVar(value="No image loaded — click Load Image to begin.")
        statusbar = tk.Frame(self.root, bg=BG_PANEL, height=26)
        statusbar.pack(fill="x", side="bottom")
        statusbar.pack_propagate(False)
        tk.Label(statusbar, textvariable=self.status_var,
                 bg=BG_PANEL, fg=TEXT_SEC,
                 font=("Segoe UI", 8)).pack(side="left", padx=12)

        # ── Main body ───────────────────────────────
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=10, pady=(6, 4))

        # Left sidebar (controls)
        sidebar = tk.Frame(body, bg=BG_PANEL, width=260)
        sidebar.pack(fill="y", side="left", padx=(0, 8))
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        # Center — image canvas
        center = tk.Frame(body, bg=BG_DARK)
        center.pack(fill="both", expand=True, side="left")
        self._build_canvas_area(center)

    # ── Sidebar ──────────────────────────────────────
    def _build_sidebar(self, parent):
        pad = dict(padx=12, pady=4)

        # ── Intensity ──────────────────────────────
        self._section_head(parent, "🎛️  Intensity Controls")


        # Brightness
        self._slider_row(parent, "Brightness", -100, 100, 0,
                         "bright_val", "bright_slider")
        # Contrast
        self._slider_row(parent, "Contrast", 10, 300, 100,
                         "cont_val", "cont_slider")

        apply_frame = tk.Frame(parent, bg=BG_PANEL)
        apply_frame.pack(fill="x", padx=12, pady=(2, 8))
        self._make_btn(apply_frame, "⚡ Apply", self._apply_brightness_contrast,
                       ACCENT, fill="x")

        self._divider(parent)

        # ── Filters ────────────────────────────────
        self._section_head(parent, "🔬  Spatial Filters")

        btn_pad = dict(padx=12, pady=3)
        self._make_btn(parent, "📊  Histogram Equalization",
                       self._apply_hist_eq, "#0e7490", fill="x", **btn_pad)
        self._make_btn(parent, "〜  Gaussian Blur",
                       self._apply_blur, "#065f46", fill="x", **btn_pad)
        self._make_btn(parent, "△  Sharpen (Laplacian)",
                       self._apply_sharpen, "#7c3aed", fill="x", **btn_pad)

        self._divider(parent)

        # ── Histogram ──────────────────────────────
        self._section_head(parent, "📈  Histogram View")

        hist_toggle_f = tk.Frame(parent, bg=BG_PANEL)
        hist_toggle_f.pack(fill="x", padx=12, pady=3)
        self._make_btn(hist_toggle_f, "Original", self._show_hist_original,
                       "#1e3a5f", side="left", expand=True, fill="x", padx=(0,2))
        self._make_btn(hist_toggle_f, "Processed", self._show_hist_processed,
                       "#1e3a5f", side="left", expand=True, fill="x", padx=(2,0))

        self.hist_frame = tk.Frame(parent, bg=BG_CARD, height=140)
        self.hist_frame.pack(fill="x", padx=12, pady=4)
        self.hist_frame.pack_propagate(False)
        tk.Label(self.hist_frame, text="Load an image to\nview histogram",
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 9)).pack(expand=True)

        self._divider(parent)

        # ── Reset ──────────────────────────────────
        self._make_btn(parent, "↺  Reset to Original", self._reset,
                       DANGER, fill="x", padx=12, pady=8)

    def _slider_row(self, parent, label, lo, hi, init,
                    val_attr, slider_attr):
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(fill="x", padx=12, pady=3)

        header = tk.Frame(row, bg=BG_CARD)
        header.pack(fill="x", padx=8, pady=(6,0))
        tk.Label(header, text=label, bg=BG_CARD, fg=TEXT_PRI,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        val_lbl = tk.Label(header, text=str(init), bg=BG_CARD, fg=ACCENT2,
                           font=("Segoe UI", 9, "bold"), width=5, anchor="e")
        val_lbl.pack(side="right")

        slider = ttk.Scale(row, from_=lo, to=hi, orient="horizontal",
                           style="Horizontal.TScale")
        slider.set(init)
        slider.pack(fill="x", padx=8, pady=(2, 8))

        setattr(self, val_attr, val_lbl)
        setattr(self, slider_attr, slider)

        def _update(e=None):
            v = int(getattr(self, slider_attr).get())
            getattr(self, val_attr).config(text=str(v))
        slider.bind("<Motion>", _update)
        slider.bind("<ButtonRelease-1>", _update)

    def _section_head(self, parent, text):
        tk.Label(parent, text=text,
                 bg=BG_PANEL, fg=ACCENT2,
                 font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(fill="x", padx=12, pady=(10, 2))

    def _divider(self, parent):
        tk.Frame(parent, bg="#2d3148", height=1).pack(fill="x", padx=12, pady=4)

    def _make_btn(self, parent, text, cmd, color,
                  side=None, fill=None, expand=False,
                  padx=0, pady=0):
        """Generic flat button."""
        btn = tk.Button(parent, text=text, command=cmd,
                        bg=color, fg=TEXT_PRI, relief="flat",
                        activebackground=BTN_HOVER, activeforeground=TEXT_PRI,
                        font=("Segoe UI", 9, "bold"),
                        cursor="hand2", padx=10, pady=5,
                        bd=0, highlightthickness=0)
        if side:
            btn.pack(side=side, fill=fill, expand=expand, padx=padx, pady=pady)
        else:
            btn.pack(fill=fill, expand=expand, padx=padx, pady=pady)
        # Hover effect
        btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=self._lighten(c)))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
        return btn

    @staticmethod
    def _lighten(hex_color):
        """Lighten a hex color by ~15%."""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            r = min(255, int(r * 1.25))
            g = min(255, int(g * 1.25))
            b = min(255, int(b * 1.25))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    # ── Canvas Area ──────────────────────────────────
    def _build_canvas_area(self, parent):
        # Labels row
        label_row = tk.Frame(parent, bg=BG_DARK)
        label_row.pack(fill="x", pady=(0, 4))
        tk.Label(label_row, text="ORIGINAL",
                 bg=BG_DARK, fg=TEXT_SEC,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(4,0))
        tk.Label(label_row, text="PROCESSED",
                 bg=BG_DARK, fg=SUCCESS,
                 font=("Segoe UI", 9, "bold")).pack(side="right", padx=(0,4))

        # Image panels
        img_row = tk.Frame(parent, bg=BG_DARK)
        img_row.pack(fill="both", expand=True)

        left_card = tk.Frame(img_row, bg=BG_CARD, bd=0)
        left_card.pack(fill="both", expand=True, side="left", padx=(0,4))
        self.canvas_orig = tk.Label(left_card,
                                    bg=BG_CARD, text="No image loaded",
                                    fg=TEXT_SEC, font=("Segoe UI", 11),
                                    anchor="center")
        self.canvas_orig.pack(fill="both", expand=True, padx=6, pady=6)

        right_card = tk.Frame(img_row, bg=BG_CARD, bd=0)
        right_card.pack(fill="both", expand=True, side="left", padx=(4,0))
        self.canvas_proc = tk.Label(right_card,
                                    bg=BG_CARD, text="Apply a filter to\nsee result here",
                                    fg=TEXT_SEC, font=("Segoe UI", 11),
                                    anchor="center")
        self.canvas_proc.pack(fill="both", expand=True, padx=6, pady=6)

        # Save button row
        save_row = tk.Frame(parent, bg=BG_DARK)
        save_row.pack(fill="x", pady=(4,0))
        self._make_btn(save_row, "💾  Save Processed Image", self._save_image,
                       "#064e3b", side="right", padx=(0,4))

    # ──────────────────────────────────────────
    #  IMAGE LOAD / DISPLAY
    # ──────────────────────────────────────────
    def _load_image(self):
        path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                       ("All Files", "*.*")]
        )
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error", "Could not read the selected file.")
            return
        self.original_bgr  = img.copy()
        self.processed_bgr = img.copy()
        self._display(self.canvas_orig, img)
        self._display(self.canvas_proc, img)
        h, w = img.shape[:2]
        self.status_var.set(f"Loaded: {path.split('/')[-1]}  |  {w}×{h} px  |  Ready")
        # Reset sliders
        self.bright_slider.set(0)
        self.cont_slider.set(100)
        self.bright_val.config(text="0")
        self.cont_val.config(text="100")

    def _display(self, label_widget, bgr_img):
        """Fit-to-widget display of a BGR numpy array."""
        label_widget.update_idletasks()
        w = label_widget.winfo_width()  or 480
        h = label_widget.winfo_height() or 380
        if w < 10: w = 480
        if h < 10: h = 380

        rgb   = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        pil   = Image.fromarray(rgb)
        pil.thumbnail((w - 12, h - 12), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil)
        label_widget.config(image=tk_img, text="")
        label_widget.image = tk_img  # prevent GC

    def _update_processed(self):
        if self.processed_bgr is not None:
            self._display(self.canvas_proc, self.processed_bgr)

    def _require_image(self):
        if self.original_bgr is None:
            messagebox.showwarning("No Image", "Please load an image first.")
            return False
        return True

    # ──────────────────────────────────────────
    #  PROCESSING OPERATIONS
    # ──────────────────────────────────────────
    def _apply_brightness_contrast(self):
        if not self._require_image(): return
        alpha = int(self.cont_slider.get()) / 100.0    # 0.1 – 3.0
        beta  = int(self.bright_slider.get())           # -100 – +100
        self.processed_bgr = cv2.convertScaleAbs(self.original_bgr,
                                                  alpha=alpha, beta=beta)
        self._update_processed()
        self.status_var.set(
            f"Brightness: {beta:+d}  |  Contrast: {alpha:.2f}×  |  Applied")

    def _apply_hist_eq(self):
        if not self._require_image(): return
        # Convert to YCrCb, equalize Y channel (keeps color)
        ycr = cv2.cvtColor(self.original_bgr, cv2.COLOR_BGR2YCrCb)
        ycr[:, :, 0] = cv2.equalizeHist(ycr[:, :, 0])
        self.processed_bgr = cv2.cvtColor(ycr, cv2.COLOR_YCrCb2BGR)
        self._update_processed()
        self.status_var.set("Histogram Equalization applied (YCrCb colour-safe)")

    def _apply_blur(self):
        if not self._require_image(): return
        self.processed_bgr = cv2.GaussianBlur(self.original_bgr, (7, 7), 0)
        self._update_processed()
        self.status_var.set("Gaussian Blur applied  (kernel 7×7, σ=auto)")

    def _apply_sharpen(self):
        if not self._require_image(): return
        kernel = np.array([[0, -1,  0],
                           [-1,  5, -1],
                           [0, -1,  0]], dtype=np.float32)
        self.processed_bgr = cv2.filter2D(self.original_bgr, -1, kernel)
        self._update_processed()
        self.status_var.set("Laplacian Sharpen applied  (high-pass 3×3 kernel)")

    def _reset(self):
        if not self._require_image(): return
        self.processed_bgr = self.original_bgr.copy()
        self._display(self.canvas_orig,  self.original_bgr)
        self._display(self.canvas_proc,  self.processed_bgr)
        self.bright_slider.set(0)
        self.cont_slider.set(100)
        self.bright_val.config(text="0")
        self.cont_val.config(text="100")
        self.status_var.set("Reset — showing original image.")

    # ──────────────────────────────────────────
    #  HISTOGRAM DISPLAY
    # ──────────────────────────────────────────
    def _draw_histogram(self, bgr_img, title="Histogram"):
        # Clear old plot widget
        for w in self.hist_frame.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(2.6, 1.5), dpi=72)
        fig.patch.set_facecolor(BG_CARD)
        ax.set_facecolor("#131722")

        colors = ("#f87171", "#4ade80", "#60a5fa")  # R, G, B in display
        labels = ("R", "G", "B")
        for i, (col, lbl) in enumerate(zip(colors, labels)):
            hist = cv2.calcHist([bgr_img], [i], None, [256], [0, 256])
            ax.plot(hist, color=col, linewidth=0.8, label=lbl)

        ax.set_xlim([0, 256])
        ax.tick_params(colors=TEXT_SEC, labelsize=5)
        ax.spines[:].set_color("#2d3148")
        ax.set_title(title, color=ACCENT2, fontsize=7, pad=3)
        ax.legend(fontsize=5, loc="upper right",
                  facecolor=BG_CARD, labelcolor=TEXT_PRI)
        fig.tight_layout(pad=0.4)

        canvas = FigureCanvasTkAgg(fig, master=self.hist_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _show_hist_original(self):
        if not self._require_image(): return
        self._draw_histogram(self.original_bgr, "Original Histogram")
        self.status_var.set("Histogram: Original image")

    def _show_hist_processed(self):
        if not self._require_image(): return
        self._draw_histogram(self.processed_bgr, "Processed Histogram")
        self.status_var.set("Histogram: Processed image")

    # ──────────────────────────────────────────
    #  SAVE
    # ──────────────────────────────────────────
    def _save_image(self):
        if self.processed_bgr is None:
            messagebox.showwarning("Nothing to Save", "Process an image first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Processed Image",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if not path: return
        cv2.imwrite(path, self.processed_bgr)
        self.status_var.set(f"✔ Saved → {path.split('/')[-1]}")
        messagebox.showinfo("Saved", f"Image saved to:\n{path}")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = ImageSuite(root)
    root.mainloop()
