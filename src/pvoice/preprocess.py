"""Consistent audio preprocessing used by training, evaluation, AND prediction.

The rules (from the project constraints):

- convert to mono
- fixed sample rate (config.SAMPLE_RATE)
- remove DC offset
- normalize amplitude
- trim leading/trailing silence
- NO aggressive filtering or denoising, because jitter, shimmer, F0 and HNR
  are sensitive to it.  Perturbation features are computed from this lightly
  processed signal on purpose.

Every entry point of the project must call :func:`load_and_preprocess` so the
exact same conditioning is applied everywhere.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np

from . import config


@dataclass
class PreprocessedAudio:
    """A cleaned mono signal plus bookkeeping info for reports."""

    signal: np.ndarray        # float32 mono, peak-normalized
    sample_rate: int
    original_sample_rate: int
    original_duration_s: float
    duration_s: float         # after trimming
    warnings: list[str]


def load_and_preprocess(path: str | Path,
                        sample_rate: int = config.SAMPLE_RATE,
                        trim_top_db: float = config.TRIM_TOP_DB) -> PreprocessedAudio:
    """Load one audio file and apply the standard conditioning chain."""
    path = Path(path)
    warnings: list[str] = []

    # librosa loads as float, converts to mono, and resamples in one call.
    original_sr = librosa.get_samplerate(path)
    signal, sr = librosa.load(path, sr=sample_rate, mono=True)
    original_duration = len(signal) / sr

    # Remove DC offset (a constant shift biases perturbation measures).
    signal = signal - np.mean(signal)

    # Trim leading/trailing silence only.  Internal pauses are kept: Praat's
    # pitch tracking simply ignores unvoiced regions, and cutting inside the
    # recording could create artificial amplitude jumps (fake shimmer).
    trimmed, _ = librosa.effects.trim(signal, top_db=trim_top_db)
    if len(trimmed) == 0:
        warnings.append("signal is entirely silence after trimming")
        trimmed = signal

    # Peak normalization to make amplitudes comparable across recordings and
    # recording devices.  (Shimmer is a *relative* measure, so a single
    # global gain does not distort it.)
    peak = np.max(np.abs(trimmed))
    if peak > 0:
        trimmed = trimmed / peak * 0.95
    else:
        warnings.append("signal is all zeros")

    duration = len(trimmed) / sr
    if duration < config.MIN_DURATION_S:
        warnings.append(
            f"very short recording: {duration:.2f}s "
            f"(minimum expected {config.MIN_DURATION_S}s)"
        )

    return PreprocessedAudio(
        signal=trimmed.astype(np.float32),
        sample_rate=sr,
        original_sample_rate=int(original_sr),
        original_duration_s=float(original_duration),
        duration_s=float(duration),
        warnings=warnings,
    )


def segment_audio(audio: PreprocessedAudio,
                  seconds: float = config.SEGMENT_SECONDS,
                  min_seconds: float = config.SEGMENT_MIN_SECONDS,
                  ) -> list[PreprocessedAudio]:
    """Split a preprocessed signal into consecutive fixed-length chunks.

    Chunks are cut AFTER the standard preprocessing, so training and
    prediction segment identically.  A trailing chunk shorter than
    ``min_seconds`` is dropped.  Recordings shorter than ``min_seconds``
    yield a single chunk containing the whole signal.
    """
    sr = audio.sample_rate
    chunk_len = int(seconds * sr)
    min_len = int(min_seconds * sr)
    signal = audio.signal
    if len(signal) <= chunk_len:
        chunks = [signal]
    else:
        chunks = [signal[start:start + chunk_len]
                  for start in range(0, len(signal), chunk_len)]
        if len(chunks[-1]) < min_len and len(chunks) > 1:
            chunks = chunks[:-1]
    return [
        PreprocessedAudio(
            signal=chunk,
            sample_rate=sr,
            original_sample_rate=audio.original_sample_rate,
            original_duration_s=audio.original_duration_s,
            duration_s=len(chunk) / sr,
            warnings=list(audio.warnings),
        )
        for chunk in chunks
    ]
