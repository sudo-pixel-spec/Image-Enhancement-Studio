"""
Smart Image Enhancement Studio
================================
Spatial domain image processing tool for IPV/DIP coursework.
Features: Brightness, Contrast, Histogram EQ, Blur, Sharpen, Before/After view.
"""
# ─────────────────────────────────────────────
#   The Comments are just I dont Mess Up. I Promise to Refactor it in Proper Files.
# ─────────────────────────────────────────────

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from enum import Enum
from typing import Optional, Any
import cv2
import numpy as np
from PIL import Image, ImageTk
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ─────────────────────────────────────────────
#  THEME / PALETTE
# ─────────────────────────────────────────────
class Theme(Enum):
    """Hex color codes and UI configuration constants."""
    BG_DARK = "#0f1117"
    BG_PANEL = "#1a1d27"
    BG_CARD = "#22263a"
    ACCENT = "#6c63ff"
    ACCENT2 = "#a78bfa"
    TEXT_PRI = "#e2e8f0"
    TEXT_SEC = "#94a3b8"
    SUCCESS = "#22d3ee"
    WARN = "#f59e0b"
    DANGER = "#f87171"
    BTN_HOVER = "#7c73ff"
    DIVIDER = "#2d3148"


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class ImageSuite:
    """Main application class for Smart Image Enhancement Studio."""

    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the application.

        Args:
            root (tk.Tk): The root tkinter window.
        """
        self.root = root
        self.root.title("Smart Image Enhancement Studio")
        self.root.geometry("1280x820")
        self.root.minsize(960, 680)
        self.root.configure(bg=Theme.BG_DARK.value)

        # State
        self.original_bgr: Optional[np.ndarray] = None  # NumPy BGR (from OpenCV)
        self.processed_bgr: Optional[np.ndarray] = None
        self.tk_original: Optional[ImageTk.PhotoImage] = None
        self.tk_processed: Optional[ImageTk.PhotoImage] = None
        self._slider_job: Optional[str] = None  # debounce handle
        self.hist_canvas_widget: Optional[tk.Widget] = None

        self._build_styles()
        self._build_ui()

    # ──────────────────────────────────────────
    #  STYLES
    # ──────────────────────────────────────────
    def _build_styles(self) -> None:
        """Configure ttk styles for application components."""
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("TFrame",       background=Theme.BG_DARK.value)
        style.configure("Card.TFrame",  background=Theme.BG_CARD.value)
        style.configure("Panel.TFrame", background=Theme.BG_PANEL.value)

        style.configure("TLabel",
                        background=Theme.BG_DARK.value, foreground=Theme.TEXT_PRI.value,
                        font=("Segoe UI", 10))
        style.configure("Title.TLabel",
                        background=Theme.BG_DARK.value, foreground=Theme.TEXT_PRI.value,
                        font=("Segoe UI", 18, "bold"))
        style.configure("Sub.TLabel",
                        background=Theme.BG_DARK.value, foreground=Theme.TEXT_SEC.value,
                        font=("Segoe UI", 9))
        style.configure("Card.TLabel",
                        background=Theme.BG_CARD.value, foreground=Theme.TEXT_PRI.value,
                        font=("Segoe UI", 10))
        style.configure("CardSub.TLabel",
                        background=Theme.BG_CARD.value, foreground=Theme.TEXT_SEC.value,
                        font=("Segoe UI", 8))
        style.configure("SectionHead.TLabel",
                        background=Theme.BG_PANEL.value, foreground=Theme.ACCENT2.value,
                        font=("Segoe UI", 10, "bold"))
        style.configure("Panel.TLabel",
                        background=Theme.BG_PANEL.value, foreground=Theme.TEXT_SEC.value,
                        font=("Segoe UI", 9))
        style.configure("Status.TLabel",
                        background=Theme.BG_DARK.value, foreground=Theme.TEXT_SEC.value,
                        font=("Segoe UI", 9))
        style.configure("Value.TLabel",
                        background=Theme.BG_CARD.value, foreground=Theme.ACCENT2.value,
                        font=("Segoe UI", 9, "bold"))

        style.configure("Horizontal.TScale",
                        background=Theme.BG_CARD.value, troughcolor="#2d3148",
                        sliderlength=18, sliderrelief="flat")

        style.configure("TScrollbar",
                        background=Theme.BG_PANEL.value, troughcolor=Theme.BG_DARK.value,
                        arrowcolor=Theme.TEXT_SEC.value)

    # ──────────────────────────────────────────
    #  UI LAYOUT
    # ──────────────────────────────────────────
    def _build_ui(self) -> None:
        """Construct the main user interface."""
        # ── Header ──────────────────────────────────
        header = tk.Frame(self.root, bg=Theme.BG_PANEL.value, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="⬡", bg=Theme.BG_PANEL.value, fg=Theme.ACCENT.value,
                 font=("Segoe UI", 22, "bold")).pack(side="left", padx=(20, 8), pady=8)
        tk.Label(header, text="Smart Image Enhancement Studio",
                 bg=Theme.BG_PANEL.value, fg=Theme.TEXT_PRI.value,
                 font=("Segoe UI", 15, "bold")).pack(side="left", pady=8)
        tk.Label(header, text="- Spatial Domain Processing",
                 bg=Theme.BG_PANEL.value, fg=Theme.TEXT_SEC.value,
                 font=("Segoe UI", 10)).pack(side="left", padx=6, pady=8)

        # Upload button in header
        self._make_btn(header, "📂  Load Image", self._load_image,
                       Theme.ACCENT.value, side="right", padx=(0, 20))

        # ── Status bar ──────────────────────────────
        self.status_var = tk.StringVar(value="No image loaded - click Load Image to begin.")
        statusbar = tk.Frame(self.root, bg=Theme.BG_PANEL.value, height=26)
        statusbar.pack(fill="x", side="bottom")
        statusbar.pack_propagate(False)
        tk.Label(statusbar, textvariable=self.status_var,
                 bg=Theme.BG_PANEL.value, fg=Theme.TEXT_SEC.value,
                 font=("Segoe UI", 8)).pack(side="left", padx=12)

        # ── Main body ───────────────────────────────
        body = tk.Frame(self.root, bg=Theme.BG_DARK.value)
        body.pack(fill="both", expand=True, padx=10, pady=(6, 4))

        # Left sidebar (controls)
        sidebar = tk.Frame(body, bg=Theme.BG_PANEL.value, width=260)
        sidebar.pack(fill="y", side="left", padx=(0, 8))
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        # Center - image canvas
        center = tk.Frame(body, bg=Theme.BG_DARK.value)
        center.pack(fill="both", expand=True, side="left")
        self._build_canvas_area(center)

    # ── Sidebar ──────────────────────────────────────
    def _build_sidebar(self, parent: tk.Frame) -> None:
        """
        Build the left sidebar with controls.

        Args:
            parent (tk.Frame): The parent frame.
        """
        # ── Intensity ──────────────────────────────
        self._section_head(parent, "🎛️  Intensity Controls")

        # Brightness
        self._slider_row(parent, "Brightness", -100, 100, 0,
                         "bright_val", "bright_slider")
        # Contrast
        self._slider_row(parent, "Contrast", 10, 300, 100,
                         "cont_val", "cont_slider")

        apply_frame = tk.Frame(parent, bg=Theme.BG_PANEL.value)
        apply_frame.pack(fill="x", padx=12, pady=(2, 8))
        self._make_btn(apply_frame, "⚡ Apply", self._apply_brightness_contrast,
                       Theme.ACCENT.value, fill="x")

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

        hist_toggle_f = tk.Frame(parent, bg=Theme.BG_PANEL.value)
        hist_toggle_f.pack(fill="x", padx=12, pady=3)
        self._make_btn(hist_toggle_f, "Original", self._show_hist_original,
                       "#1e3a5f", side="left", expand=True, fill="x", padx=(0, 2))
        self._make_btn(hist_toggle_f, "Processed", self._show_hist_processed,
                       "#1e3a5f", side="left", expand=True, fill="x", padx=(2, 0))

        self.hist_frame = tk.Frame(parent, bg=Theme.BG_CARD.value, height=140)
        self.hist_frame.pack(fill="x", padx=12, pady=4)
        self.hist_frame.pack_propagate(False)
        tk.Label(self.hist_frame, text="Load an image to\nview histogram",
                 bg=Theme.BG_CARD.value, fg=Theme.TEXT_SEC.value,
                 font=("Segoe UI", 9)).pack(expand=True)

        self._divider(parent)

        # ── Reset ──────────────────────────────────
        self._make_btn(parent, "↺  Reset to Original", self._reset,
                       Theme.DANGER.value, fill="x", padx=12, pady=8)

    def _slider_row(self, parent: tk.Widget, label: str, lo: int, hi: int, init: int,
                    val_attr: str, slider_attr: str) -> None:
        """
        Create a row with a label and a slider.

        Args:
            parent (tk.Widget): The parent widget.
            label (str): Label text.
            lo (int): Minimum value.
            hi (int): Maximum value.
            init (int): Initial value.
            val_attr (str): Attribute name to store the value label.
            slider_attr (str): Attribute name to store the slider.
        """
        row = tk.Frame(parent, bg=Theme.BG_CARD.value)
        row.pack(fill="x", padx=12, pady=3)

        header = tk.Frame(row, bg=Theme.BG_CARD.value)
        header.pack(fill="x", padx=8, pady=(6, 0))
        tk.Label(header, text=label, bg=Theme.BG_CARD.value, fg=Theme.TEXT_PRI.value,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        val_lbl = tk.Label(header, text=str(init), bg=Theme.BG_CARD.value, fg=Theme.ACCENT2.value,
                           font=("Segoe UI", 9, "bold"), width=5, anchor="e")
        val_lbl.pack(side="right")

        slider = ttk.Scale(row, from_=lo, to=hi, orient="horizontal",
                           style="Horizontal.TScale")
        slider.set(init)
        slider.pack(fill="x", padx=8, pady=(2, 8))

        setattr(self, val_attr, val_lbl)
        setattr(self, slider_attr, slider)

        def _update(e: Optional[tk.Event] = None) -> None:
            v = int(getattr(self, slider_attr).get())
            getattr(self, val_attr).config(text=str(v))

        slider.bind("<Motion>", _update)
        slider.bind("<ButtonRelease-1>", _update)

    def _section_head(self, parent: tk.Widget, text: str) -> None:
        """
        Create a section header label.

        Args:
            parent (tk.Widget): The parent widget.
            text (str): Header text.
        """
        tk.Label(parent, text=text,
                 bg=Theme.BG_PANEL.value, fg=Theme.ACCENT2.value,
                 font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(fill="x", padx=12, pady=(10, 2))

    def _divider(self, parent: tk.Widget) -> None:
        """
        Create a visual divider line.

        Args:
            parent (tk.Widget): The parent widget.
        """
        tk.Frame(parent, bg=Theme.DIVIDER.value, height=1) \
            .pack(fill="x", padx=12, pady=4)

    def _make_btn(self, parent: tk.Widget, text: str, cmd: Any, color: str,
                  side: Optional[str] = None, fill: Optional[str] = None,
                  expand: bool = False, padx: int = 0, pady: int = 0) -> tk.Button:
        """
        Generic flat button creator.

        Args:
            parent (tk.Widget): The parent widget.
            text (str): Button text.
            cmd (Callable): Command function.
            color (str): Background hex color.
            side (str, optional): Packing side.
            fill (str, optional): Packing fill.
            expand (bool): Packing expand.
            padx (int): Horizontal padding.
            pady (int): Vertical padding.

        Returns:
            tk.Button: The created button.
        """
        btn = tk.Button(parent, text=text, command=cmd,
                        bg=color, fg=Theme.TEXT_PRI.value, relief="flat",
                        activebackground=Theme.BTN_HOVER.value, activeforeground=Theme.TEXT_PRI.value,
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
    def _lighten(hex_color: str) -> str:
        """
        Lighten a hex color by ~15%.

        Args:
            hex_color (str): Original hex color.

        Returns:
            str: Lightened hex color.
        """
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
    def _build_canvas_area(self, parent: tk.Widget) -> None:
        """
        Build the image display area with side-by-side labels.

        Args:
            parent (tk.Widget): The parent widget.
        """
        # Labels row
        label_row = tk.Frame(parent, bg=Theme.BG_DARK.value)
        label_row.pack(fill="x", pady=(0, 4))
        tk.Label(label_row, text="ORIGINAL",
                 bg=Theme.BG_DARK.value, fg=Theme.TEXT_SEC.value,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(4, 0))
        tk.Label(label_row, text="PROCESSED",
                 bg=Theme.BG_DARK.value, fg=Theme.SUCCESS.value,
                 font=("Segoe UI", 9, "bold")).pack(side="right", padx=(0, 4))

        # Image panels
        img_row = tk.Frame(parent, bg=Theme.BG_DARK.value)
        img_row.pack(fill="both", expand=True)

        left_card = tk.Frame(img_row, bg=Theme.BG_CARD.value, bd=0)
        left_card.pack(fill="both", expand=True, side="left", padx=(0, 4))
        self.canvas_orig = tk.Label(left_card,
                                    bg=Theme.BG_CARD.value, text="No image loaded",
                                    fg=Theme.TEXT_SEC.value, font=("Segoe UI", 11),
                                    anchor="center")
        self.canvas_orig.pack(fill="both", expand=True, padx=6, pady=6)

        right_card = tk.Frame(img_row, bg=Theme.BG_CARD.value, bd=0)
        right_card.pack(fill="both", expand=True, side="left", padx=(4, 0))
        self.canvas_proc = tk.Label(right_card,
                                    bg=Theme.BG_CARD.value, text="Apply a filter to\nsee result here",
                                    fg=Theme.TEXT_SEC.value, font=("Segoe UI", 11),
                                    anchor="center")
        self.canvas_proc.pack(fill="both", expand=True, padx=6, pady=6)

        # Save button row
        save_row = tk.Frame(parent, bg=Theme.BG_DARK.value)
        save_row.pack(fill="x", pady=(4, 0))
        self._make_btn(save_row, "💾  Save Processed Image", self._save_image,
                       "#064e3b", side="right", padx=(0, 4))

    # ──────────────────────────────────────────
    #  IMAGE LOAD / DISPLAY
    # ──────────────────────────────────────────
    def _load_image(self) -> None:
        """Open a file dialog to load an image and update the UI."""
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

        self.original_bgr = img.copy()
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

    def _display(self, label_widget: tk.Label, bgr_img: np.ndarray) -> None:
        """
        Fit-to-widget display of a BGR numpy array.

        Args:
            label_widget (tk.Label): The label widget to display the image in.
            bgr_img (np.ndarray): The image in BGR format.
        """
        label_widget.update_idletasks()
        w = label_widget.winfo_width() or 480
        h = label_widget.winfo_height() or 380
        if w < 10:
            w = 480
        if h < 10:
            h = 380

        rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil.thumbnail((w - 12, h - 12), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil)
        label_widget.config(image=tk_img, text="")
        label_widget.image = tk_img  # type: ignore # prevent GC

    def _update_processed(self) -> None:
        """Update the processed image view if an image exists."""
        if self.processed_bgr is not None:
            self._display(self.canvas_proc, self.processed_bgr)

    def _require_image(self) -> bool:
        """
        Check if an image is loaded, showing a warning if not.

        Returns:
            bool: True if image is loaded, False otherwise.
        """
        if self.original_bgr is None:
            messagebox.showwarning("No Image", "Please load an image first.")
            return False
        return True

    # ──────────────────────────────────────────
    #  PROCESSING OPERATIONS
    # ──────────────────────────────────────────
    def _apply_brightness_contrast(self) -> None:
        """Apply brightness and contrast adjustments based on slider values."""
        if not self._require_image() or self.original_bgr is None:
            return
        alpha = int(self.cont_slider.get()) / 100.0  # 0.1 – 3.0
        beta = int(self.bright_slider.get())         # -100 – +100
        self.processed_bgr = cv2.convertScaleAbs(self.original_bgr,
                                                 alpha=alpha, beta=beta)
        self._update_processed()
        self.status_var.set(
            f"Brightness: {beta:+d}  |  Contrast: {alpha:.2f}×  |  Applied")

    def _apply_hist_eq(self) -> None:
        """Apply color-safe (YCrCb) histogram equalization."""
        if not self._require_image() or self.original_bgr is None:
            return
        # Convert to YCrCb, equalize Y channel (keeps color)
        ycr = cv2.cvtColor(self.original_bgr, cv2.COLOR_BGR2YCrCb)
        ycr[:, :, 0] = cv2.equalizeHist(ycr[:, :, 0])
        self.processed_bgr = cv2.cvtColor(ycr, cv2.COLOR_YCrCb2BGR)
        self._update_processed()
        self.status_var.set("Histogram Equalization applied (YCrCb colour-safe)")

    def _apply_blur(self) -> None:
        """Apply Gaussian blur to the image."""
        if not self._require_image() or self.original_bgr is None:
            return
        self.processed_bgr = cv2.GaussianBlur(self.original_bgr, (7, 7), 0)
        self._update_processed()
        self.status_var.set("Gaussian Blur applied  (kernel 7×7, σ=auto)")

    def _apply_sharpen(self) -> None:
        """Apply Laplacian sharpening filter."""
        if not self._require_image() or self.original_bgr is None:
            return
        kernel = np.array([[0, -1,  0],
                           [-1,  5, -1],
                           [0, -1,  0]], dtype=np.float32)
        self.processed_bgr = cv2.filter2D(self.original_bgr, -1, kernel)
        self._update_processed()
        self.status_var.set("Laplacian Sharpen applied  (high-pass 3×3 kernel)")

    def _reset(self) -> None:
        """Reset the processed image and sliders to their original state."""
        if not self._require_image() or self.original_bgr is None:
            return
        self.processed_bgr = self.original_bgr.copy()
        self._display(self.canvas_orig, self.original_bgr)
        self._display(self.canvas_proc, self.processed_bgr)
        self.bright_slider.set(0)
        self.cont_slider.set(100)
        self.bright_val.config(text="0")
        self.cont_val.config(text="100")
        self.status_var.set("Reset - showing original image.")

    # ──────────────────────────────────────────
    #  HISTOGRAM DISPLAY
    # ──────────────────────────────────────────
    def _draw_histogram(self, bgr_img: np.ndarray, title: str = "Histogram") -> None:
        """
        Calculate and draw RGB histogram using Matplotlib.

        Args:
            bgr_img (np.ndarray): Image to calculate histogram for.
            title (str): Title of the histogram plot.
        """
        # Clear old plot widget
        for w in self.hist_frame.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(2.6, 1.5), dpi=72)
        fig.patch.set_facecolor(Theme.BG_CARD.value)
        ax.set_facecolor("#131722")

        colors = ("#f87171", "#4ade80", "#60a5fa")  # R, G, B in display
        labels = ("R", "G", "B")
        for i, (col, lbl) in enumerate(zip(colors, labels)):
            hist = cv2.calcHist([bgr_img], [i], None, [256], [0, 256])
            ax.plot(hist, color=col, linewidth=0.8, label=lbl)

        ax.set_xlim([0, 256])
        ax.tick_params(colors=Theme.TEXT_SEC.value, labelsize=5)
        ax.spines[:].set_color(Theme.DIVIDER.value)
        ax.set_title(title, color=Theme.ACCENT2.value, fontsize=7, pad=3)
        ax.legend(fontsize=5, loc="upper right",
                  facecolor=Theme.BG_CARD.value, labelcolor=Theme.TEXT_PRI.value)
        fig.tight_layout(pad=0.4)

        canvas = FigureCanvasTkAgg(fig, master=self.hist_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _show_hist_original(self) -> None:
        """Show histogram for the original image."""
        if not self._require_image() or self.original_bgr is None:
            return
        self._draw_histogram(self.original_bgr, "Original Histogram")
        self.status_var.set("Histogram: Original image")

    def _show_hist_processed(self) -> None:
        """Show histogram for the processed image."""
        if not self._require_image() or self.processed_bgr is None:
            return
        self._draw_histogram(self.processed_bgr, "Processed Histogram")
        self.status_var.set("Histogram: Processed image")

    # ──────────────────────────────────────────
    #  SAVE
    # ──────────────────────────────────────────
    def _save_image(self) -> None:
        """Save the processed image to a file."""
        if self.processed_bgr is None:
            messagebox.showwarning("Nothing to Save", "Process an image first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Processed Image",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if not path:
            return
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
