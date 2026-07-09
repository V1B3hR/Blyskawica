"""
Improved EEG feature extraction module.

Key improvements:
- Robust Welch nperseg handling
- Explicit asymmetry convention: asymmetry = log(left) - log(right)
- Optional preprocessing: bandpass + notch
- Channel name support and named asymmetry pairs
- get_feature_names helper for interpretability
- Safe PSD/spectral entropy handling and input validation
"""
from typing import Dict, List, Optional, Tuple, Sequence, Union

import logging
import numpy as np
from scipy import signal as sp_signal
from scipy.stats import entropy

logger = logging.getLogger(__name__)


class EEGFeatureExtractor:
    DEFAULT_BANDS: Dict[str, Tuple[float, float]] = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 45),
    }

    def __init__(self,
                 sampling_rate: int = 250,
                 extract_asymmetry: bool = True,
                 extract_connectivity: bool = False,
                 channel_pairs_for_asymmetry: Optional[List[Tuple[Union[int, str], Union[int, str]]]] = None,
                 channel_names: Optional[Sequence[str]] = None,
                 bands: Optional[Dict[str, Tuple[float, float]]] = None,
                 do_preproc: bool = False,
                 bp_low: float = 0.5,
                 bp_high: float = 45.0,
                 notch_freqs: Optional[Sequence[float]] = None):
        """
        Args:
            sampling_rate: sampling frequency in Hz
            extract_asymmetry: whether to compute asymmetry features
            extract_connectivity: whether to compute connectivity features (simple correlation summary)
            channel_pairs_for_asymmetry: list of (left, right) pairs; elements can be integer indices or channel names
            channel_names: optional sequence of channel names (maps indices -> names)
            bands: override default frequency bands
            do_preproc: whether to apply simple preprocessing (bandpass + optional notch) before features
            bp_low, bp_high: bandpass limits in Hz for preprocessing
            notch_freqs: iterable of frequencies to notch (e.g., [50.0] or [50.0, 100.0])
        """
        self.sampling_rate = int(sampling_rate)
        self.extract_asymmetry = bool(extract_asymmetry)
        self.extract_connectivity = bool(extract_connectivity)
        self.BANDS = dict(bands) if bands is not None else dict(self.DEFAULT_BANDS)
        self.channel_names = list(channel_names) if channel_names is not None else None
        self.do_preproc = bool(do_preproc)
        self.bp_low = float(bp_low)
        self.bp_high = float(bp_high)
        self.notch_freqs = list(notch_freqs) if notch_freqs is not None else []

        # store asymmetry pairs in raw form (may contain names or indices)
        if channel_pairs_for_asymmetry is None:
            # default simple placeholder pairs (indices) - adapt to your montage
            self.asymmetry_pairs = [(0, 1), (2, 3)]
        else:
            self.asymmetry_pairs = list(channel_pairs_for_asymmetry)

    # Public API
    def extract_features(self, eeg_data: np.ndarray) -> np.ndarray:
        """
        Extract features from single EEG recording (channels, timesteps).

        Returns:
            flattened 1D numpy array of features
        """
        eeg_data = np.asarray(eeg_data, dtype=float)
        if eeg_data.ndim != 2:
            raise ValueError("eeg_data must be 2D array of shape (channels, timesteps)")

        if self.do_preproc:
            eeg_data = self._preprocess(eeg_data)

        n_channels, _ = eeg_data.shape
        # validate channel-name mapping length if provided
        if self.channel_names is not None and len(self.channel_names) != n_channels:
            logger.warning("channel_names length (%d) doesn't match data channels (%d). Ignoring names.",
                           len(self.channel_names), n_channels)
            self.channel_names = None

        # band powers
        band_powers = self.extract_band_powers(eeg_data)  # shape (n_channels, n_bands)

        features = [band_powers.flatten()]

        # asymmetry features (log(left) - log(right) convention)
        if self.extract_asymmetry and len(self.asymmetry_pairs) > 0:
            asym = self.extract_asymmetry_features_from_bandpowers(band_powers)
            features.append(asym)

        # spectral entropy
        ent = self.extract_spectral_entropy(eeg_data)
        features.append(ent)

        # statistical features
        stats = self.extract_statistical_features(eeg_data)
        features.append(stats)

        # connectivity (simple summary)
        if self.extract_connectivity:
            conn = self.extract_connectivity_features(eeg_data)
            features.append(conn)

        return np.concatenate([np.asarray(x).ravel() for x in features])

    def extract_band_powers(self, eeg_data: np.ndarray) -> np.ndarray:
        """
        Compute relative band power for each channel and band.
        Returns array shape (n_channels, n_bands) with values normalized across the defined bands.
        """
        n_channels, n_time = eeg_data.shape
        band_names = list(self.BANDS.keys())
        n_bands = len(band_names)
        band_powers = np.zeros((n_channels, n_bands), dtype=float)

        for ch in range(n_channels):
            x = eeg_data[ch, :]
            # welch nperseg must be 1..len(x), prefer 256 but don't exceed len(x)
            nperseg = min(256, max(1, len(x)))
            try:
                freqs, psd = sp_signal.welch(x, fs=self.sampling_rate, nperseg=nperseg)
            except Exception as e:
                logger.warning("PSD computation failed for channel %d: %s", ch, e)
                continue

            for b_idx, bname in enumerate(band_names):
                low, high = self.BANDS[bname]
                mask = (freqs >= low) & (freqs <= high)
                if np.any(mask):
                    band_powers[ch, b_idx] = np.trapz(psd[mask], freqs[mask])
                else:
                    band_powers[ch, b_idx] = 0.0

        # Normalize by sum across the selected bands per channel -> relative band power
        eps = 1e-12
        total = np.sum(band_powers, axis=1, keepdims=True)
        band_powers = band_powers / (total + eps)
        return band_powers

    def extract_asymmetry_features_from_bandpowers(self, band_powers: np.ndarray) -> np.ndarray:
        """
        Build asymmetry features from band powers.
        Convention: asymmetry = log(left) - log(right), positive means greater left activation.
        Asymmetry pairs may be provided as indices or names.
        """
        n_channels = band_powers.shape[0]
        n_bands = band_powers.shape[1]
        resolved_pairs = []
        for left, right in self.asymmetry_pairs:
            left_idx = self._resolve_channel_index(left, n_channels)
            right_idx = self._resolve_channel_index(right, n_channels)
            if left_idx is None or right_idx is None:
                logger.warning("Could not resolve asymmetry pair (%s, %s); using zeros.", left, right)
                resolved_pairs.append((None, None))
            else:
                resolved_pairs.append((left_idx, right_idx))

        eps = 1e-12
        asym_list = []
        for left_idx, right_idx in resolved_pairs:
            if left_idx is None or right_idx is None:
                asym_list.append(np.zeros(n_bands))
            else:
                left_power = band_powers[left_idx, :] + eps
                right_power = band_powers[right_idx, :] + eps
                asym_list.append(np.log(left_power) - np.log(right_power))
        if len(asym_list) == 0:
            return np.zeros(0, dtype=float)
        return np.concatenate(asym_list)

    def extract_spectral_entropy(self, eeg_data: np.ndarray) -> np.ndarray:
        """
        Compute Shannon spectral entropy per channel using Welch PSD.
        Returns array of length n_channels.
        """
        n_channels, _ = eeg_data.shape
        entropies = np.zeros(n_channels, dtype=float)
        eps = 1e-12

        for ch in range(n_channels):
            x = eeg_data[ch, :]
            nperseg = min(256, max(1, len(x)))
            try:
                _, psd = sp_signal.welch(x, fs=self.sampling_rate, nperseg=nperseg)
            except Exception as e:
                logger.warning("Spectral entropy PSD failed on channel %d: %s", ch, e)
                entropies[ch] = 0.0
                continue
            s = np.sum(psd)
            if s <= 0 or np.all(psd == 0):
                entropies[ch] = 0.0
            else:
                p = psd / (s + eps)
                entropies[ch] = entropy(p + eps)  # natural log base
        return entropies

    def extract_statistical_features(self, eeg_data: np.ndarray) -> np.ndarray:
        """
        Returns concatenation of per-channel mean,std,min,max and two global stats: mean,std
        Length: 4*n_channels + 2
        """
        means = np.mean(eeg_data, axis=1)
        stds = np.std(eeg_data, axis=1)
        mins = np.min(eeg_data, axis=1)
        maxs = np.max(eeg_data, axis=1)
        global_mean = np.mean(eeg_data)
        global_std = np.std(eeg_data)
        return np.concatenate([means, stds, mins, maxs, np.array([global_mean, global_std])])

    def extract_connectivity_features(self, eeg_data: np.ndarray) -> np.ndarray:
        """
        Simple connectivity summary using Pearson correlation.
        Returns [mean, std, max, min] over upper-triangle correlation values.
        """
        n_channels, _ = eeg_data.shape
        if n_channels < 2:
            return np.array([0.0, 0.0, 0.0, 0.0])
        try:
            corr = np.corrcoef(eeg_data)
        except Exception as e:
            logger.warning("Correlation matrix failed: %s", e)
            return np.array([0.0, 0.0, 0.0, 0.0])
        iu = np.triu_indices(n_channels, k=1)
        vals = corr[iu]
        if vals.size == 0:
            return np.array([0.0, 0.0, 0.0, 0.0])
        return np.array([np.nanmean(vals), np.nanstd(vals), np.nanmax(vals), np.nanmin(vals)])

    # Helpers
    def _resolve_channel_index(self, ch: Union[int, str], n_channels: int) -> Optional[int]:
        """Resolve either int index or channel-name to index."""
        if isinstance(ch, int):
            if 0 <= ch < n_channels:
                return ch
            return None
        if isinstance(ch, str):
            if self.channel_names is None:
                return None
            try:
                return self.channel_names.index(ch)
            except ValueError:
                return None
        return None

    def _preprocess(self, eeg_data: np.ndarray) -> np.ndarray:
        """
        Simple preprocessing: bandpass between bp_low and bp_high using 4th order butterworth
        and optional notch filtering for provided notch_freqs (IIR notch).
        """
        data = eeg_data.copy()
        nyq = 0.5 * self.sampling_rate
        low = max(0.0, self.bp_low / nyq)
        high = min(0.999, self.bp_high / nyq)
        if low < high:
            b, a = sp_signal.butter(N=4, Wn=[low, high], btype='band')
            data = sp_signal.filtfilt(b, a, data, axis=1)
        else:
            logger.warning("Invalid bandpass settings, skipping bandpass: low=%f high=%f", self.bp_low, self.bp_high)

        for f0 in self.notch_freqs:
            # design notch (IIR) at f0
            q = 30.0
            w0 = f0 / nyq
            if 0 < w0 < 1:
                b, a = sp_signal.iirnotch(w0, q)
                data = sp_signal.filtfilt(b, a, data, axis=1)
            else:
                logger.warning("Skipping notch at %s Hz (out of range for sampling rate %d)", f0, self.sampling_rate)
        return data

    def get_feature_dimension(self, n_channels: int) -> int:
        """Return expected feature length for given channel count."""
        n_bands = len(self.BANDS)
        dim = n_channels * n_bands
        if self.extract_asymmetry:
            dim += len(self.asymmetry_pairs) * n_bands
        dim += n_channels  # spectral entropy
        dim += 4 * n_channels + 2  # statistical
        if self.extract_connectivity:
            dim += 4
        return dim

    def get_feature_names(self, n_channels: int) -> List[str]:
        """
        Produce human-readable feature names matching extract_features order.
        Use channel_names if provided.
        """
        band_names = list(self.BANDS.keys())
        ch_names = self.channel_names if self.channel_names is not None else [f"ch{idx}" for idx in range(n_channels)]
        names = []

        # band powers
        for ch in range(n_channels):
            for b in band_names:
                names.append(f"{ch_names[ch]}_band_{b}_relpower")

        # asymmetry
        if self.extract_asymmetry:
            for left, right in self.asymmetry_pairs:
                left_label = left if isinstance(left, str) else (ch_names[left] if isinstance(left, int) and 0 <= left < n_channels else str(left))
                right_label = right if isinstance(right, str) else (ch_names[right] if isinstance(right, int) and 0 <= right < n_channels else str(right))
                for b in band_names:
                    names.append(f"asym_{left_label}_vs_{right_label}_band_{b}_logdiff")

        # spectral entropy
        for ch in range(n_channels):
            names.append(f"{ch_names[ch]}_spectral_entropy")

        # statistical per channel
        for ch in range(n_channels):
            names.append(f"{ch_names[ch]}_mean")
        for ch in range(n_channels):
            names.append(f"{ch_names[ch]}_std")
        for ch in range(n_channels):
            names.append(f"{ch_names[ch]}_min")
        for ch in range(n_channels):
            names.append(f"{ch_names[ch]}_max")

        # global stats
        names.append("global_mean")
        names.append("global_std")

        # connectivity
        if self.extract_connectivity:
            names += ["conn_mean", "conn_std", "conn_max", "conn_min"]

        return names


def extract_eeg_features_batch(eeg_batch: np.ndarray,
                               sampling_rate: int = 250,
                               **kwargs) -> np.ndarray:
    """
    Batch convenience: eeg_batch shape (batch, channels, timesteps)
    Returns features shape (batch, n_features)
    """
    eeg_batch = np.asarray(eeg_batch)
    if eeg_batch.ndim != 3:
        raise ValueError("eeg_batch must be 3D array (batch, channels, timesteps)")
    extractor = EEGFeatureExtractor(sampling_rate=sampling_rate, **kwargs)
    features = []
    for i in range(eeg_batch.shape[0]):
        features.append(extractor.extract_features(eeg_batch[i]))
    return np.stack(features)
