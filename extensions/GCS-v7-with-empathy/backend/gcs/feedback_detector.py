# Single-cell, drop-in module for REAL-TIME, ADAPTIVE EEG FEEDBACK DETECTION
# - Automatic resampling (downsample/upsample) to target Fs
# - Sliding window that ADAPTS between 1.0s / 0.5s / 0.25s based on signal state
# - Multi-channel detection with per-channel results + overall summary
# - Lightweight (NumPy + SciPy); CPU-friendly, sub-ms per channel on typical settings
#
# Usage (pseudo-loop):
#   det = AdaptiveFeedbackDetector()
#   while stream:
#       eeg_chunk, fs = get_chunk()  # shape: [n_channels, n_samples]
#       out = det.process(eeg_chunk, fs)
#       if out["decision_changed"]: act_on_feedback(out)
#
# Notes:
# - “Feedback” here is a stand-in for your corrective/intent signal. We infer it using
#   bandpower & spectral-entropy heuristics (alpha/beta dynamics), then smooth + hysteresis.
# - Swap the `score_from_features` for your ML classifier if you have one.

import numpy as np
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
import logging

from scipy.signal import resample_poly, welch, filtfilt, iirnotch

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# ----------------------------- Utilities -------------------------------------

def bandpower_welch(x: np.ndarray, fs: float, fmin: float, fmax: float) -> float:
    """Bandpower via Welch PSD (robust for short windows)."""
    if x.size == 0:
        return 0.0
    nperseg = max(64, min(512, x.shape[-1]))  # auto-fit segment length
    noverlap = nperseg // 2
    freqs, psd = welch(x, fs=fs, nperseg=nperseg, noverlap=noverlap, detrend="constant")
    mask = (freqs >= fmin) & (freqs <= fmax)
    if not np.any(mask):
        return 0.0
    return float(np.trapz(psd[mask], freqs[mask]))


def spectral_entropy(x: np.ndarray, fs: float, fmax: float = 45.0) -> float:
    """Normalized spectral entropy in [0,1], higher ~ more irregular/busy."""
    if x.size == 0:
        return 0.0
    nperseg = max(64, min(512, x.shape[-1]))
    noverlap = nperseg // 2
    freqs, psd = welch(x, fs=fs, nperseg=nperseg, noverlap=noverlap, detrend="constant")
    mask = (freqs > 0.1) & (freqs <= fmax)
    p = psd[mask]
    if p.sum() <= 0:
        return 0.0
    p = p / p.sum()
    # Shannon entropy normalized by log(K)
    H = -(p * np.log(p + 1e-12)).sum()
    H_norm = H / np.log(len(p))
    return float(np.clip(H_norm, 0.0, 1.0))


def notch_filter_50_60(x: np.ndarray, fs: float) -> np.ndarray:
    """Apply 50/60Hz notch if within Nyquist (per-channel)."""
    y = x.copy()
    for f0 in (50.0, 60.0):
        if f0 < fs / 2 - 1:
            w0 = f0 / (fs / 2)
            b, a = iirnotch(w0, Q=30.0)
            for ch in range(y.shape[0]):
                y[ch] = filtfilt(b, a, y[ch])
    return y


# ------------------------- Configuration & State ------------------------------

@dataclass
class DetectorConfig:
    # Target processing sample rate (automatic up/down sampling)
    target_fs: float = 250.0

    # Sliding window options (seconds)
    window_options: Tuple[float, float, float] = (1.0, 0.5, 0.25)
    # Initial window length (seconds)
    init_window: float = 1.0

    # Decision cadence: step size as fraction of current window (e.g., 0.25 => 75% overlap)
    step_fraction: float = 0.25

    # Band definitions (Hz)
    theta: Tuple[float, float] = (4.0, 7.0)
    alpha: Tuple[float, float] = (8.0, 13.0)
    beta:  Tuple[float, float] = (13.0, 30.0)

    # Adaptive-policy thresholds on entropy (busy vs calm)
    # Busy => shrink window; Calm => expand window
    busy_entropy_hi: float = 0.70
    calm_entropy_lo: float = 0.50

    # Hysteresis: min decisions before allowing another window size change
    min_steps_between_resize: int = 6

    # Feedback decision thresholds (post-smoothing)
    trigger_threshold: float = 0.65   # go True above this
    release_threshold: float = 0.45   # go False below this

    # Smoothing EMA for scores
    ema_alpha: float = 0.3

    # Optional powerline notch
    apply_notch: bool = True

    # Max buffer seconds to keep
    max_buffer_sec: float = 3.0


@dataclass
class ChannelState:
    ema_score: float = 0.0
    last_decision: bool = False


@dataclass
class AdaptiveState:
    cur_window_sec: float
    step_counter_since_resize: int = 0


# -------------------------- Main Detector Class ------------------------------

class AdaptiveFeedbackDetector:
    """
    Real-time, adaptive-window EEG feedback detector:
    - Feeds a circular buffer (per call) with resampled data to target_fs.
    - On each step, extracts features per channel from the last 'cur_window_sec'.
    - Computes a feedback score (0..1), smooths via EMA, applies hysteresis.
    - Adapts window size based on spectral entropy (busy->shorter, calm->longer).
    """

    def __init__(self, config: Optional[DetectorConfig] = None):
        self.cfg = config or DetectorConfig()
        self.target_fs = self.cfg.target_fs

        # Buffer to accumulate resampled EEG (shape: [n_channels, variable_samples])
        self._buf: Optional[np.ndarray] = None
        self._buf_max_samples = int(self.cfg.max_buffer_sec * self.target_fs)

        self._channels: int = 0
        self._states: Dict[int, ChannelState] = {}
        self._adaptive = AdaptiveState(cur_window_sec=self.cfg.init_window)

        self._step_samples_cache = None  # recompute when window changes
        logging.info("AdaptiveFeedbackDetector initialized: Fs=%.1f Hz, initial window=%.2fs",
                     self.target_fs, self._adaptive.cur_window_sec)

    # ------------------------ Public API ------------------------

    def process(self, eeg_chunk: np.ndarray, chunk_fs: float) -> Dict[str, Any]:
        """
        Push a new EEG chunk and get a detection decision.
        Args:
          eeg_chunk: shape [n_channels, n_samples]
          chunk_fs:  sampling rate of this chunk
        Returns:
          dict with per-channel 'decision' and metadata.
        """
        assert eeg_chunk.ndim == 2, "eeg_chunk must be [n_channels, n_samples]"
        n_channels, n_samples = eeg_chunk.shape

        # Initialize buffers/states on first call
        if self._buf is None:
            self._channels = n_channels
            self._buf = np.zeros((n_channels, 0), dtype=np.float32)
            self._states = {ch: ChannelState() for ch in range(n_channels)}

        # 1) Resample chunk to target_fs (auto down/upsample)
        rs_chunk = self._resample_to_target(eeg_chunk, chunk_fs)  # [C, Ns_rs]

        # 2) Optional notch filter (per chunk after resampling)
        if self.cfg.apply_notch and rs_chunk.shape[1] > 8:
            rs_chunk = notch_filter_50_60(rs_chunk, self.target_fs)

        # 3) Append to circular buffer
        self._append_to_buffer(rs_chunk)

        # 4) If we don't have enough samples for current window, return “no-update” quickly
        window_samples = int(self._adaptive.cur_window_sec * self.target_fs)
        if self._buf.shape[1] < window_samples:
            return {
                "updated": False,
                "reason": "insufficient_samples",
                "cur_window_sec": self._adaptive.cur_window_sec,
            }

        # 5) Determine step size (hop) from current window and step_fraction
        if self._step_samples_cache is None:
            step_samples = max(1, int(self.cfg.step_fraction * window_samples))
            self._step_samples_cache = step_samples

        # 6) Extract the most recent window for analysis
        Xw = self._buf[:, -window_samples:]  # [C, W]

        # 7) Compute features per channel & form scores
        per_ch_scores = np.zeros(self._channels, dtype=np.float32)
        per_ch_entropy = np.zeros(self._channels, dtype=np.float32)

        for ch in range(self._channels):
            x = Xw[ch]
            feats = self._extract_features(x, fs=self.target_fs)
            score = self._score_from_features(feats)  # 0..1
            per_ch_scores[ch] = self._update_ema(ch, score)
            per_ch_entropy[ch] = feats["entropy"]

        # 8) Hysteresis decision per channel
        decisions = {}
        decision_changed = False
        for ch in range(self._channels):
            prev = self._states[ch].last_decision
            s = per_ch_scores[ch]
            if prev:
                # stay ON until we’re clearly below release_threshold
                now = s >= self.cfg.release_threshold
            else:
                # stay OFF until we’re clearly above trigger_threshold
                now = s >= self.cfg.trigger_threshold
            # If state changed, note it
            if now != prev:
                decision_changed = True
            self._states[ch].last_decision = now
            decisions[ch] = bool(now)

        # 9) Adaptive window policy based on median entropy across channels (+ hysteresis)
        med_entropy = float(np.median(per_ch_entropy))
        self._maybe_resize_window(med_entropy)

        # 10) Advance buffer "cursor" by step size (simulate sliding window hop)
        step_samples = self._step_samples_cache
        if self._buf.shape[1] > window_samples + step_samples:
            self._buf = self._buf[:, step_samples:]

        return {
            "updated": True,
            "cur_window_sec": self._adaptive.cur_window_sec,
            "step_samples": step_samples,
            "target_fs": self.target_fs,
            "scores": per_ch_scores.tolist(),
            "entropy_median": med_entropy,
            "decision": decisions,
            "decision_changed": decision_changed,
        }

    # --------------------- Internal helpers ---------------------

    def _resample_to_target(self, x: np.ndarray, fs_in: float) -> np.ndarray:
        """Resample [C, N] to target_fs using rational polyphase (fast & accurate)."""
        if fs_in == self.target_fs:
            return x.astype(np.float32, copy=False)

        # Determine up/down factors with good precision
        # Limit factors to avoid huge resampling ratios
        r = self.target_fs / fs_in
        # Search small integer approximation for r
        best_p, best_q = _best_rational_approx(r, max_den=64)
        y = np.empty((x.shape[0], int(np.ceil(x.shape[1] * best_p / best_q))), dtype=np.float32)
        for ch in range(x.shape[0]):
            y[ch] = resample_poly(x[ch].astype(np.float32, copy=False), up=best_p, down=best_q).astype(np.float32)
        return y

    def _append_to_buffer(self, rs_chunk: np.ndarray) -> None:
        """Append resampled chunk to circular buffer with cap."""
        if self._buf is None:
            self._buf = rs_chunk
        else:
            self._buf = np.concatenate([self._buf, rs_chunk], axis=1)
        # Trim to max buffer
        if self._buf.shape[1] > self._buf_max_samples:
            self._buf = self._buf[:, -self._buf_max_samples :]

    def _extract_features(self, x: np.ndarray, fs: float) -> Dict[str, float]:
        """Compute lightweight features for fast real-time scoring."""
        alpha = bandpower_welch(x, fs, *self.cfg.alpha)
        beta  = bandpower_welch(x, fs, *self.cfg.beta)
        theta = bandpower_welch(x, fs, *self.cfg.theta)

        total = alpha + beta + theta + 1e-9
        alpha_rel = alpha / total
        beta_rel  = beta  / total
        theta_rel = theta / total

        ent = spectral_entropy(x, fs, fmax=45.0)

        return {
            "alpha": alpha, "beta": beta, "theta": theta,
            "alpha_rel": alpha_rel, "beta_rel": beta_rel, "theta_rel": theta_rel,
            "entropy": ent,
        }

    def _score_from_features(self, f: Dict[str, float]) -> float:
        """
        Heuristic score in [0,1] from features.
        Replace this with your trained classifier if available.
        Intuition:
          - Higher beta_rel (13–30 Hz) + moderate entropy => “engaged/intent” (feedback)
          - Very high entropy => penalize (too noisy)
          - Moderate alpha_rel can support if beta_rel also moderate
        """
        beta_rel  = f["beta_rel"]
        alpha_rel = f["alpha_rel"]
        ent = f["entropy"]

        # Base from beta
        score = 0.6 * beta_rel

        # Alpha synergy (gentle boost if present alongside beta)
        score += 0.25 * np.sqrt(max(0.0, alpha_rel * beta_rel))

        # Entropy penalty (noisy/irregular -> reduce confidence)
        score *= float(np.clip(1.2 - ent, 0.0, 1.0))

        # Clamp to [0,1]
        return float(np.clip(score, 0.0, 1.0))

    def _update_ema(self, ch: int, new_score: float) -> float:
        """EMA smoothing of per-channel score."""
        st = self._states[ch]
        st.ema_score = (1 - self.cfg.ema_alpha) * st.ema_score + self.cfg.ema_alpha * new_score
        return st.ema_score

    def _maybe_resize_window(self, median_entropy: float) -> None:
        """Adapt window size based on entropy, with hysteresis and floor/ceiling."""
        self._adaptive.step_counter_since_resize += 1
        if self._adaptive.step_counter_since_resize < self.cfg.min_steps_between_resize:
            return

        wopts = sorted(self.cfg.window_options, reverse=True)  # [1.0, 0.5, 0.25] by default
        cur = self._adaptive.cur_window_sec
        idx = wopts.index(cur)

        # Busy -> try shorter window; Calm -> try longer window
        new_idx = idx
        if median_entropy >= self.cfg.busy_entropy_hi and idx < len(wopts) - 1:
            new_idx = idx + 1
        elif median_entropy <= self.cfg.calm_entropy_lo and idx > 0:
            new_idx = idx - 1

        if new_idx != idx:
            self._adaptive.cur_window_sec = wopts[new_idx]
            self._adaptive.step_counter_since_resize = 0
            # Recompute step size for new window
            self._step_samples_cache = None
            logging.info("Adaptive window change: %.2fs  -->  %.2fs (median entropy=%.2f)",
                         cur, self._adaptive.cur_window_sec, median_entropy)


# ---------------------- Rational Approximation Helper -------------------------

def _best_rational_approx(x: float, max_den: int = 64) -> Tuple[int, int]:
    """
    Find p/q approximating x with q <= max_den (simple continued fraction approach).
    Keeps resample_poly factors small & efficient.
    """
    from math import floor

    if x <= 0:
        return 1, 1

    # Continued fraction expansion
    a = []
    r = x
    for _ in range(20):
        ai = floor(r)
        a.append(ai)
        frac = r - ai
        if frac < 1e-9:
            break
        r = 1.0 / frac

    # Convergents
    num1, num2 = 1, 0
    den1, den2 = 0, 1
    best_p, best_q = 1, 1
    min_err = float("inf")

    for ai in a:
        num = ai * num1 + num2
        den = ai * den1 + den2
        if den <= max_den:
            err = abs(x - num / den)
            if err < min_err:
                min_err = err
                best_p, best_q = num, den
            num2, num1 = num1, num
            den2, den1 = den1, den
        else:
            break

    return max(1, best_p), max(1, best_q)


# ------------------------------- Demo Stub -----------------------------------
if __name__ == "__main__":
    # Synthetic demo (won't run forever). Comment/remove in production.
    rng = np.random.default_rng(0)
    det = AdaptiveFeedbackDetector()

    # Simulate 64ch @ 512 Hz stream, delivering ~128 ms chunks
    fs_in = 512.0
    n_channels = 16
    chunk_ms = 128
    samples_per_chunk = int(fs_in * (chunk_ms / 1000.0))

    # Create two regimes: calm (alpha-ish), then busy (beta-ish)
    t = 0.0
    dt = 1.0 / fs_in

    def synth_chunk(t0, n, mode="calm"):
        tt = t0 + np.arange(n) * dt
        X = np.zeros((n_channels, n), dtype=np.float32)
        for ch in range(n_channels):
            if mode == "calm":
                # alpha-dominant 10 Hz + small noise
                X[ch] = 20e-6 * np.sin(2 * np.pi * 10.0 * tt) + 5e-6 * rng.standard_normal(n)
            else:
                # beta-dominant 20 Hz + more noise
                X[ch] = 15e-6 * np.sin(2 * np.pi * 20.0 * tt) + 10e-6 * rng.standard_normal(n)
        return X

    for i in range(40):
        mode = "calm" if i < 20 else "busy"
        chunk = synth_chunk(t, samples_per_chunk, mode=mode)
        t += samples_per_chunk * dt
        out = det.process(chunk, fs_in)
        if out["updated"]:
            logging.info(
                "win=%.2fs | step=%d | Fs=%.0f | entropy_med=%.2f | any=True? %s",
                out["cur_window_sec"], out["step_samples"], out["target_fs"],
                out["entropy_median"], any(out["decision"].values())
            )
