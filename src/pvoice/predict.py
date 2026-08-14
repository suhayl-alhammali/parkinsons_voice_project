"""Prediction for a single new audio file.

Uses the SAME preprocessing (preprocess.load_and_preprocess) and the SAME
feature extraction (features.extract_features) as training, then applies the
saved model pipeline.

Safety behaviour required by the project:

- models/pipeline_config.json is verified before EVERY prediction; if it is
  missing, or any pipeline setting or the ordered feature list differs from
  the current code, prediction refuses to run (PipelineConfigError).
- The audio file is validated first (exists, non-empty, readable, not
  silent, long enough).  Failures raise AudioValidationError with a message
  a non-technical user can understand; the technical detail is kept on the
  exception's ``debug`` attribute for logs.
- Output wording is deliberately cautious: the result is a research model
  classification, never a diagnosis.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import soundfile as sf

from . import config
from .features import extract_features, feature_names
from .preprocess import load_and_preprocess, segment_audio

# Recordings shorter than this are rejected outright (too little speech for
# any of the acoustic measurements to mean anything).
MIN_PREDICT_DURATION_S = config.MIN_DURATION_S
# Below this we still predict, but attach a reliability warning (the
# training recordings were 70+ seconds long).
SHORT_RECORDING_WARNING_S = 10.0
SILENCE_PEAK_THRESHOLD = 1e-4


class AudioValidationError(Exception):
    """The audio file cannot be analyzed. str() is safe to show to users."""

    def __init__(self, message: str, debug: str = ""):
        super().__init__(message)
        self.debug = debug


class PipelineConfigError(Exception):
    """The saved model is not compatible with the current pipeline code."""


@dataclass
class PredictionResult:
    file: str
    predicted_label: str          # "HC" or "PD"
    headline: str                 # cautious one-sentence classification
    pd_score: float | None        # model score for the PD class (0..1)
    duration_s: float             # analyzed duration after trimming
    original_duration_s: float
    original_sample_rate: int
    warnings: list[str] = field(default_factory=list)
    disclaimer: str = config.DISCLAIMER
    label_explanation: str = config.LABEL_EXPLANATION


def validate_audio_file(audio_path: str | Path) -> None:
    """Reject unusable files with messages a non-expert can understand."""
    path = Path(audio_path)
    if not path.exists():
        raise AudioValidationError(f"The file could not be found: {path}")
    if path.stat().st_size == 0:
        raise AudioValidationError(
            "The file is empty (0 bytes). Please choose a real recording.")
    try:
        info = sf.info(str(path))
    except Exception as exc:
        raise AudioValidationError(
            "This file could not be read as audio. Please provide a "
            "standard WAV recording (uncompressed .wav works best).",
            debug=f"{type(exc).__name__}: {exc}",
        ) from exc
    if info.frames == 0 or info.duration <= 0:
        raise AudioValidationError(
            "The file contains no audio samples. Please choose a real "
            "recording.")
    if info.duration < MIN_PREDICT_DURATION_S:
        raise AudioValidationError(
            f"The recording is too short ({info.duration:.2f} seconds). "
            f"Please provide at least {MIN_PREDICT_DURATION_S:.0f} second(s) "
            "of speech.")
    try:
        data, _ = sf.read(str(path), dtype="float32", always_2d=True)
    except Exception as exc:
        raise AudioValidationError(
            "The audio data inside this file is damaged and could not be "
            "decoded.",
            debug=f"{type(exc).__name__}: {exc}",
        ) from exc
    if data.size == 0 or float(np.max(np.abs(data))) < SILENCE_PEAK_THRESHOLD:
        raise AudioValidationError(
            "The recording appears to be silent. Please record again and "
            "make sure the microphone captured your voice.")


def load_model(model_path: Path = config.MODEL_FILE):
    """Load the trained pipeline saved by the training script."""
    if not model_path.exists():
        raise PipelineConfigError(
            "No trained model was found. The training step must be "
            "completed first (see README, Phase 4)."
        )
    return joblib.load(model_path)


def check_pipeline_config(config_path: Path = config.PIPELINE_CONFIG_FILE) -> None:
    """Verify the saved model was trained with the current pipeline settings.

    If sample rate, pitch range, MFCC settings, or the ordered feature list
    changed since training, predictions would silently use a different
    pipeline than training did - exactly what the 'same pipeline' rule
    forbids.  Missing or unreadable configuration is treated as
    incompatible: we refuse to guess.
    """
    if not config_path.exists():
        raise PipelineConfigError(
            "The saved model has no pipeline configuration file "
            f"({config_path.name}), so compatibility cannot be verified. "
            "Retrain the model to regenerate it."
        )
    try:
        saved = json.loads(config_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineConfigError(
            "The pipeline configuration file could not be read "
            f"({config_path.name}). Retrain the model to regenerate it."
        ) from exc
    current = current_pipeline_config()
    mismatches = {
        key: (saved.get(key), current[key])
        for key in current
        if saved.get(key) != current[key]
    }
    if mismatches:
        raise PipelineConfigError(
            "The pipeline settings have changed since the model was "
            "trained, so old model and new features are not compatible. "
            "Retrain the model before predicting. Changed settings: "
            f"{sorted(mismatches)}"
        )


def current_pipeline_config() -> dict:
    """The settings that define the preprocessing/feature pipeline."""
    return {
        "sample_rate": config.SAMPLE_RATE,
        "trim_top_db": config.TRIM_TOP_DB,
        "pitch_floor_hz": config.PITCH_FLOOR_HZ,
        "pitch_ceiling_hz": config.PITCH_CEILING_HZ,
        "n_mfcc": config.N_MFCC,
        "mfcc_n_fft": config.MFCC_N_FFT,
        "mfcc_hop_length": config.MFCC_HOP_LENGTH,
        "feature_set": config.FEATURE_SET,
        "aggregation": config.AGGREGATION,
        "segment_seconds": config.SEGMENT_SECONDS,
        "segment_min_seconds": config.SEGMENT_MIN_SECONDS,
        "cpps_pitch_floor_hz": config.CPPS_PITCH_FLOOR_HZ,
        "cpps_time_step": config.CPPS_TIME_STEP,
        "pause_min_s": config.PAUSE_MIN_S,
        "pause_top_db": config.PAUSE_TOP_DB,
        "feature_names": feature_names(),
    }


def _headline(label: str) -> str:
    return ("The acoustic pattern was classified by the research model as "
            f"closer to the {label} class.")


def predict_file(audio_path: str | Path,
                 model_path: Path = config.MODEL_FILE) -> PredictionResult:
    """Run the full pipeline on one audio file and return a cautious result.

    Raises AudioValidationError or PipelineConfigError with user-friendly
    messages; any other exception indicates a genuine software problem.
    """
    check_pipeline_config()
    model = load_model(model_path)
    validate_audio_file(audio_path)

    audio = load_and_preprocess(audio_path)
    warnings = list(audio.warnings)
    if audio.duration_s < SHORT_RECORDING_WARNING_S:
        warnings.append(
            f"the recording is much shorter ({audio.duration_s:.1f} s) than "
            "the research recordings the model was trained on (70+ s), so "
            "the result is less reliable")

    # Same rule as training: split into chunks, extract features per chunk,
    # average each feature over chunks (config.AGGREGATION).
    chunks = segment_audio(audio)
    chunk_rows = [extract_features(chunk) for chunk in chunks]
    mean_features = pd.DataFrame(chunk_rows).mean(axis=0).to_dict()
    X = pd.DataFrame([mean_features], columns=feature_names())

    predicted = int(model.predict(X)[0])
    label = config.LABEL_NAMES[predicted]
    score = None
    if hasattr(model, "predict_proba"):
        score = float(model.predict_proba(X)[0, 1])

    return PredictionResult(
        file=str(audio_path),
        predicted_label=label,
        headline=_headline(label),
        pd_score=score,
        duration_s=audio.duration_s,
        original_duration_s=audio.original_duration_s,
        original_sample_rate=audio.original_sample_rate,
        warnings=warnings,
    )
