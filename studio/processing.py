from __future__ import annotations

from enum import Enum
from typing import Tuple

import cv2
import numpy as np


class ApplySource(Enum):
    ORIGINAL = "original"
    PROCESSED = "processed"


class ImageProcessor:
    """Stateless OpenCV operations for the enhancement studio."""

    @staticmethod
    def brightness_contrast(
        bgr: np.ndarray, alpha: float, beta: int
    ) -> np.ndarray:
        return cv2.convertScaleAbs(bgr, alpha=alpha, beta=beta)

    @staticmethod
    def gamma(bgr: np.ndarray, gamma: float) -> np.ndarray:
        inv = 1.0 / max(gamma, 0.01)
        table = np.array(
            [((i / 255.0) ** inv) * 255 for i in range(256)]
        ).astype("uint8")
        return cv2.LUT(bgr, table)

    @staticmethod
    def saturation(bgr: np.ndarray, factor: float) -> np.ndarray:
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    @staticmethod
    def histogram_equalize(bgr: np.ndarray) -> np.ndarray:
        ycr = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
        ycr[:, :, 0] = cv2.equalizeHist(ycr[:, :, 0])
        return cv2.cvtColor(ycr, cv2.COLOR_YCrCb2BGR)

    @staticmethod
    def clahe(bgr: np.ndarray, clip_limit: float = 2.0, tile: int = 8) -> np.ndarray:
        ycr = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
        clahe_op = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile, tile))
        ycr[:, :, 0] = clahe_op.apply(ycr[:, :, 0])
        return cv2.cvtColor(ycr, cv2.COLOR_YCrCb2BGR)

    @staticmethod
    def gaussian_blur(bgr: np.ndarray, ksize: int = 7) -> np.ndarray:
        k = ksize if ksize % 2 == 1 else ksize + 1
        return cv2.GaussianBlur(bgr, (k, k), 0)

    @staticmethod
    def median_blur(bgr: np.ndarray, ksize: int = 5) -> np.ndarray:
        k = ksize if ksize % 2 == 1 else ksize + 1
        return cv2.medianBlur(bgr, k)

    @staticmethod
    def bilateral(bgr: np.ndarray, d: int = 9, sigma: int = 75) -> np.ndarray:
        return cv2.bilateralFilter(bgr, d, sigma, sigma)

    @staticmethod
    def laplacian_sharpen(bgr: np.ndarray) -> np.ndarray:
        kernel = np.array(
            [[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32
        )
        return cv2.filter2D(bgr, -1, kernel)

    @staticmethod
    def unsharp_mask(bgr: np.ndarray, amount: float = 1.5, sigma: float = 1.0) -> np.ndarray:
        blurred = cv2.GaussianBlur(bgr, (0, 0), sigma)
        sharp = cv2.addWeighted(bgr, 1.0 + amount, blurred, -amount, 0)
        return np.clip(sharp, 0, 255).astype(np.uint8)

    @staticmethod
    def grayscale(bgr: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def sepia(bgr: np.ndarray) -> np.ndarray:
        kernel = np.array(
            [[0.272, 0.534, 0.131],
             [0.349, 0.686, 0.168],
             [0.393, 0.769, 0.189]]
        )
        sepia = cv2.transform(bgr, kernel)
        return np.clip(sepia, 0, 255).astype(np.uint8)

    @staticmethod
    def invert(bgr: np.ndarray) -> np.ndarray:
        return cv2.bitwise_not(bgr)

    @staticmethod
    def rotate_90(bgr: np.ndarray, clockwise: bool = True) -> np.ndarray:
        code = cv2.ROTATE_90_CLOCKWISE if clockwise else cv2.ROTATE_90_COUNTERCLOCKWISE
        return cv2.rotate(bgr, code)

    @staticmethod
    def flip(bgr: np.ndarray, horizontal: bool = True) -> np.ndarray:
        code = 1 if horizontal else 0
        return cv2.flip(bgr, code)

    @staticmethod
    def canny_edges(bgr: np.ndarray, low: int = 50, high: int = 150) -> np.ndarray:
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, low, high)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def sobel_edges(bgr: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        mag = cv2.magnitude(gx, gy)
        mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        return cv2.cvtColor(mag, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def adaptive_threshold(bgr: np.ndarray, block: int = 11, c: int = 2) -> np.ndarray:
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        b = block if block % 2 == 1 else block + 1
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, b, c
        )
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def denoise(bgr: np.ndarray, strength: int = 10) -> np.ndarray:
        return cv2.fastNlMeansDenoisingColored(
            bgr, None, strength, strength, 7, 21
        )

    @staticmethod
    def resize_preview(
        bgr: np.ndarray, max_w: int, max_h: int
    ) -> Tuple[np.ndarray, float]:
        h, w = bgr.shape[:2]
        scale = min(max_w / w, max_h / h, 1.0)
        if scale >= 1.0:
            return bgr, 1.0
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_AREA), scale
