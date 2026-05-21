from __future__ import annotations

from typing import Any, Callable, Optional

import tkinter as tk
from tkinter import ttk

from studio.theme import Theme


def lighten(hex_color: str, factor: float = 1.25) -> str:
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, IndexError):
        return hex_color


def flat_button(
    parent: tk.Widget,
    text: str,
    command: Callable[[], None],
    color: str,
    *,
    side: Optional[str] = None,
    fill: Optional[str] = None,
    expand: bool = False,
    padx: int = 0,
    pady: int = 0,
) -> tk.Button:
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=Theme.TEXT_PRI.value,
        relief="flat",
        activebackground=Theme.BTN_HOVER.value,
        activeforeground=Theme.TEXT_PRI.value,
        font=(Theme.FONT.value, 9, "bold"),
        cursor="hand2",
        padx=10,
        pady=5,
        bd=0,
        highlightthickness=0,
    )
    if side:
        btn.pack(side=side, fill=fill, expand=expand, padx=padx, pady=pady)
    else:
        btn.pack(fill=fill, expand=expand, padx=padx, pady=pady)
    btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=lighten(c)))
    btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
    return btn


def section_head(parent: tk.Widget, text: str) -> tk.Label:
    return tk.Label(
        parent,
        text=text,
        bg=Theme.BG_PANEL.value,
        fg=Theme.ACCENT2.value,
        font=(Theme.FONT.value, 10, "bold"),
        anchor="w",
    )


def divider(parent: tk.Widget) -> tk.Frame:
    f = tk.Frame(parent, bg=Theme.DIVIDER.value, height=1)
    f.pack(fill="x", padx=12, pady=4)
    return f


def build_ttk_styles(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background=Theme.BG_DARK.value)
    style.configure("Card.TFrame", background=Theme.BG_CARD.value)
    style.configure("Panel.TFrame", background=Theme.BG_PANEL.value)
    style.configure(
        "Horizontal.TScale",
        background=Theme.BG_CARD.value,
        troughcolor=Theme.DIVIDER.value,
        sliderlength=18,
        sliderrelief="flat",
    )


class ScrollableFrame(tk.Frame):
    """Vertically scrollable panel for dense control sidebars."""

    def __init__(self, parent: tk.Widget, width: int = 280, **kwargs: Any) -> None:
        super().__init__(parent, bg=Theme.BG_PANEL.value, **kwargs)
        self.canvas = tk.Canvas(
            self,
            bg=Theme.BG_PANEL.value,
            highlightthickness=0,
            width=width,
        )
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=Theme.BG_PANEL.value)

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<Enter>", self._bind_wheel)
        self.canvas.bind("<Leave>", self._unbind_wheel)

    def _on_canvas_resize(self, event: tk.Event) -> None:
        self.canvas.itemconfig(self._win, width=event.width)

    def _bind_wheel(self, _event: tk.Event) -> None:
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_wheel(self, _event: tk.Event) -> None:
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event: tk.Event) -> None:
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class SliderRow:
    """Label + value + horizontal scale."""

    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        lo: float,
        hi: float,
        init: float,
        *,
        resolution: float = 1.0,
        on_change: Optional[Callable[[float], None]] = None,
    ) -> None:
        self.on_change = on_change
        row = tk.Frame(parent, bg=Theme.BG_CARD.value)
        row.pack(fill="x", padx=12, pady=3)

        header = tk.Frame(row, bg=Theme.BG_CARD.value)
        header.pack(fill="x", padx=8, pady=(6, 0))
        tk.Label(
            header,
            text=label,
            bg=Theme.BG_CARD.value,
            fg=Theme.TEXT_PRI.value,
            font=(Theme.FONT.value, 9, "bold"),
        ).pack(side="left")
        self.value_label = tk.Label(
            header,
            text=str(init),
            bg=Theme.BG_CARD.value,
            fg=Theme.ACCENT2.value,
            font=(Theme.FONT.value, 9, "bold"),
            width=6,
            anchor="e",
        )
        self.value_label.pack(side="right")

        self.slider = ttk.Scale(
            row, from_=lo, to=hi, orient="horizontal", style="Horizontal.TScale"
        )
        self.slider.set(init)
        self.slider.pack(fill="x", padx=8, pady=(2, 8))
        self._resolution = resolution
        self._format = ".0f" if resolution >= 1 else ".2f"

        self.slider.bind("<Motion>", self._update)
        self.slider.bind("<ButtonRelease-1>", self._update)

    def get(self) -> float:
        return float(self.slider.get())

    def set(self, value: float) -> None:
        self.slider.set(value)
        self.value_label.config(text=format(value, self._format))

    def _update(self, _event: Optional[tk.Event] = None) -> None:
        raw = self.get()
        if self._resolution >= 1:
            v = int(round(raw / self._resolution) * self._resolution)
        else:
            v = round(raw, 2)
        self.value_label.config(text=format(v, self._format))
        if self.on_change:
            self.on_change(v)
