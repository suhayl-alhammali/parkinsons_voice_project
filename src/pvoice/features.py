"""Acoustic feature extraction.

One preprocessed signal in -> one flat dict of named features out.

Feature families (all required by the project constraints):

1. F0 statistics            (Parselmouth / Praat pitch tracking)
2. Jitter variants          (Praat point process)
3. Shimmer variants         (Praat point process)
4. Harmonic-to-noise ratio  (Praat harmonicity)
5. MFCC summary statistics  (librosa, mean + std per coefficient)

The same function :func:`extract_features` is used to build the training
feature table and to analyze a new file at prediction time, which guarantees
the "same pipeline" rule.
"""

from __future__ import annotations

import math

import librosa
import numpy as np
import parselmouth
from parselmouth.praat import call

from . import config
from .preprocess import PreprocessedAudio


def extract_features(audio: PreprocessedAudio) -> dict[str, float]:
    """Extract ALL known features (base + extended) from one signal.

    Downstream code selects the columns it needs via feature_names() /
    base_feature_names() / extended_feature_names(), so base-only models
    and extended models share this single extraction path.
    """
    features: dict[str, float] = {}
    features.update(_praat_features(audio))
    features.update(_mfcc_features(audio))
    features.update(_cpps_features(audio))
    features.update(_pause_features(audio))
    # Return in the canonical order so feature tables are stable.
    return {name: features[name] for name in extended_feature_names()}


def base_feature_names() -> list[str]:
    """The Phase 3/4 feature set (43 features)."""
    praat_names = [
        "f0_mean_hz", "f0_median_hz", "f0_std_hz", "f0_min_hz", "f0_max_hz",
        "f0_range_hz", "voiced_fraction",
        "jitter_local", "jitter_local_abs", "jitter_rap", "jitter_ppq5",
        "shimmer_local", "shimmer_local_db", "shimmer_apq3", "shimmer_apq5",
        "shimmer_apq11",
        "hnr_mean_db",
    ]
    mfcc_names = []
    for i in range(config.N_MFCC):
        mfcc_names.append(f"mfcc{i}_mean")
        mfcc_names.append(f"mfcc{i}_std")
    return praat_names + mfcc_names


def extended_feature_names() -> list[str]:
    """Base features + CPPS + pause statistics + delta-MFCC (74 features)."""
    delta_names = []
    for i in range(config.N_MFCC):
        delta_names.append(f"mfccD{i}_mean")
        delta_names.append(f"mfccD{i}_std")
    return (base_feature_names()
            + ["cpps_db",
               "pause_count_per_min", "pause_mean_s", "pause_ratio",
               "speech_seg_mean_s"]
            + delta_names)


def feature_names() -> list[str]:
    """Ordered feature list of the ACTIVE feature set (config.FEATURE_SET).

    This is what trained models consume and what pipeline_config.json pins.
    """
    if config.FEATURE_SET == "extended":
        return extended_feature_names()
    return base_feature_names()


# ---------------------------------------------------------------------------
# Praat-based features (F0, jitter, shimmer, HNR)
# ---------------------------------------------------------------------------

def _praat_features(audio: PreprocessedAudio) -> dict[str, float]:
    sound = parselmouth.Sound(
        audio.signal.astype(np.float64), sampling_frequency=audio.sample_rate
    )

    pitch = sound.to_pitch(
        pitch_floor=config.PITCH_FLOOR_HZ, pitch_ceiling=config.PITCH_CEILING_HZ
    )
    f0_values = pitch.selected_array["frequency"]
    voiced = f0_values[f0_values > 0]

    out: dict[str, float] = {}
    if voiced.size > 0:
        out["f0_mean_hz"] = float(np.mean(voiced))
        out["f0_median_hz"] = float(np.median(voiced))
        out["f0_std_hz"] = float(np.std(voiced))
        out["f0_min_hz"] = float(np.min(voiced))
        out["f0_max_hz"] = float(np.max(voiced))
        out["f0_range_hz"] = out["f0_max_hz"] - out["f0_min_hz"]
        out["voiced_fraction"] = float(voiced.size / f0_values.size)
    else:
        for name in ("f0_mean_hz", "f0_median_hz", "f0_std_hz", "f0_min_hz",
                     "f0_max_hz", "f0_range_hz", "voiced_fraction"):
            out[name] = math.nan

    # Point process for jitter/shimmer.
    point_process = call(
        sound, "To PointProcess (periodic, cc)",
        config.PITCH_FLOOR_HZ, config.PITCH_CEILING_HZ,
    )
    pf = config.JITTER_SHIMMER_PERIOD_FLOOR
    pc = config.JITTER_SHIMMER_PERIOD_CEILING
    mpf = config.JITTER_SHIMMER_MAX_PERIOD_FACTOR
    maf = config.SHIMMER_MAX_AMPLITUDE_FACTOR

    def _safe(value: float) -> float:
        # Praat returns NaN (or raises) when too few periods are found.
        return float(value) if value == value else math.nan

    try:
        out["jitter_local"] = _safe(call(point_process, "Get jitter (local)", 0, 0, pf, pc, mpf))
        out["jitter_local_abs"] = _safe(call(point_process, "Get jitter (local, absolute)", 0, 0, pf, pc, mpf))
        out["jitter_rap"] = _safe(call(point_process, "Get jitter (rap)", 0, 0, pf, pc, mpf))
        out["jitter_ppq5"] = _safe(call(point_process, "Get jitter (ppq5)", 0, 0, pf, pc, mpf))
    except parselmouth.PraatError:
        for name in ("jitter_local", "jitter_local_abs", "jitter_rap", "jitter_ppq5"):
            out[name] = math.nan

    try:
        args = (0, 0, pf, pc, mpf, maf)
        out["shimmer_local"] = _safe(call([sound, point_process], "Get shimmer (local)", *args))
        out["shimmer_local_db"] = _safe(call([sound, point_process], "Get shimmer (local_dB)", *args))
        out["shimmer_apq3"] = _safe(call([sound, point_process], "Get shimmer (apq3)", *args))
        out["shimmer_apq5"] = _safe(call([sound, point_process], "Get shimmer (apq5)", *args))
        out["shimmer_apq11"] = _safe(call([sound, point_process], "Get shimmer (apq11)", *args))
    except parselmouth.PraatError:
        for name in ("shimmer_local", "shimmer_local_db", "shimmer_apq3",
                     "shimmer_apq5", "shimmer_apq11"):
            out[name] = math.nan

    try:
        harmonicity = call(
            sound, "To Harmonicity (cc)",
            config.HNR_TIME_STEP, config.PITCH_FLOOR_HZ,
            config.HNR_SILENCE_THRESHOLD, config.HNR_PERIODS_PER_WINDOW,
        )
        out["hnr_mean_db"] = _safe(call(harmonicity, "Get mean", 0, 0))
    except parselmouth.PraatError:
        out["hnr_mean_db"] = math.nan

    return out


# ---------------------------------------------------------------------------
# MFCC summary statistics + delta-MFCC (librosa)
# ---------------------------------------------------------------------------

def _mfcc_features(audio: PreprocessedAudio) -> dict[str, float]:
    mfcc = librosa.feature.mfcc(
        y=audio.signal,
        sr=audio.sample_rate,
        n_mfcc=config.N_MFCC,
        n_fft=config.MFCC_N_FFT,
        hop_length=config.MFCC_HOP_LENGTH,
    )
    out: dict[str, float] = {}
    for i in range(config.N_MFCC):
        out[f"mfcc{i}_mean"] = float(np.mean(mfcc[i]))
        out[f"mfcc{i}_std"] = float(np.std(mfcc[i]))
    # Delta-MFCC: frame-to-frame change of each coefficient, capturing how
    # fast the spectral envelope moves (articulation dynamics).
    delta = librosa.feature.delta(mfcc)
    for i in range(config.N_MFCC):
        out[f"mfccD{i}_mean"] = float(np.mean(delta[i]))
        out[f"mfccD{i}_std"] = float(np.std(delta[i]))
    return out


# ---------------------------------------------------------------------------
# CPPS: smoothed cepstral peak prominence (Praat), a robust dysphonia
# measure that works on continuous speech.  Lower CPPS = breathier/noisier.
# ---------------------------------------------------------------------------

def _cpps_features(audio: PreprocessedAudio) -> dict[str, float]:
    try:
        sound = parselmouth.Sound(
            audio.signal.astype(np.float64),
            sampling_frequency=audio.sample_rate,
        )
        cepstrogram = call(
            sound, "To PowerCepstrogram",
            config.CPPS_PITCH_FLOOR_HZ, config.CPPS_TIME_STEP,
            config.CPPS_MAX_FREQUENCY_HZ, config.CPPS_PREEMPHASIS_FROM_HZ,
        )
        cpps = call(
            cepstrogram, "Get CPPS",
            False,          # subtract tilt before smoothing
            0.02, 0.0005,   # time / quefrency averaging windows
            60.0, 330.0,    # peak search pitch range (Hz)
            0.05, "parabolic",
            0.001, 0.05,    # tilt line quefrency range (s)
            "Straight", "Robust",
        )
        value = float(cpps)
    except (parselmouth.PraatError, ValueError):
        value = math.nan
    return {"cpps_db": value if value == value else math.nan}


# ---------------------------------------------------------------------------
# Pause statistics (librosa energy-based speech/pause segmentation).
# Parkinsonian speech tends to contain more and longer pauses.
# ---------------------------------------------------------------------------

def _pause_features(audio: PreprocessedAudio) -> dict[str, float]:
    sr = audio.sample_rate
    total_s = len(audio.signal) / sr
    out = {"pause_count_per_min": math.nan, "pause_mean_s": math.nan,
           "pause_ratio": math.nan, "speech_seg_mean_s": math.nan}
    if total_s <= 0:
        return out
    intervals = librosa.effects.split(
        audio.signal, top_db=config.PAUSE_TOP_DB,
        frame_length=config.MFCC_N_FFT, hop_length=config.MFCC_HOP_LENGTH,
    )
    if len(intervals) == 0:
        return out
    speech_lengths = [(end - start) / sr for start, end in intervals]
    gaps = [(intervals[i + 1][0] - intervals[i][1]) / sr
            for i in range(len(intervals) - 1)]
    pauses = [g for g in gaps if g >= config.PAUSE_MIN_S]
    out["pause_count_per_min"] = len(pauses) / (total_s / 60.0)
    out["pause_mean_s"] = float(np.mean(pauses)) if pauses else 0.0
    out["pause_ratio"] = float(sum(pauses) / total_s)
    out["speech_seg_mean_s"] = float(np.mean(speech_lengths))
    return out
