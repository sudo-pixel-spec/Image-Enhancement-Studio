"""Image quality metrics for IPV project evaluation (PSNR, SSIM, MSE)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import cv2
import numpy as np


@dataclass
class QualityMetrics:
    """Comparison of processed image against a reference (typically original)."""

    mse: float
    psnr_db: float
    ssim: float
    mean_intensity: float
    std_intensity: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "mse": self.mse,
            "psnr_db": self.psnr_db,
            "ssim": self.ssim,
            "mean_intensity": self.mean_intensity,
            "std_intensity": self.std_intensity,
        }

    def summary(self) -> str:
        return (
            f"MSE={self.mse:.2f}  PSNR={self.psnr_db:.2f} dB  "
            f"SSIM={self.ssim:.4f}  μ={self.mean_intensity:.1f}  σ={self.std_intensity:.1f}"
        )


def mse(reference: np.ndarray, test: np.ndarray) -> float:
    """Mean squared error between two BGR images of equal shape."""
    if reference.shape != test.shape:
        test = cv2.resize(test, (reference.shape[1], reference.shape[0]))
    ref = reference.astype(np.float64)
    tst = test.astype(np.float64)
    return float(np.mean((ref - tst) ** 2))


def psnr(reference: np.ndarray, test: np.ndarray, max_pixel: float = 255.0) -> float:
    """
    Peak Signal-to-Noise Ratio in decibels.

    PSNR = 10 · log10(MAX² / MSE)
    Returns inf when images are identical.
    """
    err = mse(reference, test)
    if err < 1e-10:
        return float("inf")
    return float(10.0 * np.log10((max_pixel**2) / err))


def _ssim_single_channel(ref: np.ndarray, tst: np.ndarray, window: int = 11) -> float:
    """SSIM for one 2D channel (Wang et al., 2004)."""
    ref = ref.astype(np.float64)
    tst = tst.astype(np.float64)
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    kernel = cv2.getGaussianKernel(window, 1.5)
    window_2d = kernel @ kernel.T

    mu1 = cv2.filter2D(ref, -1, window_2d)
    mu2 = cv2.filter2D(tst, -1, window_2d)
    mu1_sq, mu2_sq, mu1_mu2 = mu1**2, mu2**2, mu1 * mu2

    sigma1_sq = cv2.filter2D(ref**2, -1, window_2d) - mu1_sq
    sigma2_sq = cv2.filter2D(tst**2, -1, window_2d) - mu2_sq
    sigma12 = cv2.filter2D(ref * tst, -1, window_2d) - mu1_mu2

    num = (2 * mu1_mu2 + c1) * (2 * sigma12 + c2)
    den = (mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2)
    ssim_map = num / (den + 1e-12)
    return float(np.mean(ssim_map))


def ssim(reference: np.ndarray, test: np.ndarray) -> float:
    """
    Structural Similarity Index (average over BGR channels).

    Range [-1, 1]; 1 means identical structure. Typical good enhancement: 0.85–0.99.
    """
    if reference.shape != test.shape:
        test = cv2.resize(test, (reference.shape[1], reference.shape[0]))
    scores = []
    for c in range(reference.shape[2] if reference.ndim == 3 else 1):
        ref_c = reference[:, :, c] if reference.ndim == 3 else reference
        tst_c = test[:, :, c] if test.ndim == 3 else test
        scores.append(_ssim_single_channel(ref_c, tst_c))
    return float(np.mean(scores))


def compute_metrics(reference: np.ndarray, processed: np.ndarray) -> QualityMetrics:
    """Full metric bundle comparing processed output to reference image."""
    if reference.shape != processed.shape:
        processed = cv2.resize(processed, (reference.shape[1], reference.shape[0]))
    return QualityMetrics(
        mse=mse(reference, processed),
        psnr_db=psnr(reference, processed),
        ssim=ssim(reference, processed),
        mean_intensity=float(np.mean(processed)),
        std_intensity=float(np.std(processed)),
    )
