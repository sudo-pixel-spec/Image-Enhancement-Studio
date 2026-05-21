from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from studio.processing import ApplySource


@dataclass
class ImageDocument:
    """Holds original/processed arrays and edit history."""

    original_bgr: Optional[np.ndarray] = None
    processed_bgr: Optional[np.ndarray] = None
    apply_source: ApplySource = ApplySource.ORIGINAL
    _undo: List[np.ndarray] = field(default_factory=list)
    _redo: List[np.ndarray] = field(default_factory=list)
    max_history: int = 30

    @property
    def has_image(self) -> bool:
        return self.original_bgr is not None

    @property
    def dimensions(self) -> Optional[tuple[int, int]]:
        if self.original_bgr is None:
            return None
        h, w = self.original_bgr.shape[:2]
        return w, h

    def load(self, bgr: np.ndarray) -> None:
        self.original_bgr = bgr.copy()
        self.processed_bgr = bgr.copy()
        self._undo.clear()
        self._redo.clear()

    def working_copy(self) -> np.ndarray:
        if self.apply_source == ApplySource.PROCESSED and self.processed_bgr is not None:
            return self.processed_bgr.copy()
        if self.original_bgr is None:
            raise RuntimeError("No image loaded")
        return self.original_bgr.copy()

    def commit(self, result: np.ndarray, *, push_history: bool = True) -> None:
        if self.processed_bgr is not None and push_history:
            self._undo.append(self.processed_bgr.copy())
            if len(self._undo) > self.max_history:
                self._undo.pop(0)
            self._redo.clear()
        self.processed_bgr = result

    def undo(self) -> bool:
        if not self._undo or self.processed_bgr is None:
            return False
        self._redo.append(self.processed_bgr.copy())
        self.processed_bgr = self._undo.pop()
        return True

    def redo(self) -> bool:
        if not self._redo or self.processed_bgr is None:
            return False
        self._undo.append(self.processed_bgr.copy())
        self.processed_bgr = self._redo.pop()
        return True

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)

    def reset_processed(self) -> None:
        if self.original_bgr is None:
            return
        self.processed_bgr = self.original_bgr.copy()
        self._undo.clear()
        self._redo.clear()

    def sync_original_after_geometry(self, bgr: np.ndarray) -> None:
        """After rotate/flip, update both views to the new geometry."""
        self.original_bgr = bgr.copy()
        self.processed_bgr = bgr.copy()
        self._undo.clear()
        self._redo.clear()
