"""Basic pipeline tests using synthetic audio (no dataset needed).

Where to run:  project folder, with .venv activated
Command:       python -m pytest tests -q        (if pytest is installed)
        or:    python tests/test_pipeline.py    (runs the same checks)
"""

from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import soundfile as sf

from pvoice import config
from pvoice.features import extract_features, feature_names
from pvoice.preprocess import load_and_preprocess


def _make_test_tone(path: Path, f0: float = 150.0, seconds: float = 2.0) -> None:
    """Write a synthetic vowel-like tone: F0 + harmonics + tiny noise."""
    sr = config.SAMPLE_RATE
    t = np.arange(int(sr * seconds)) / sr
    signal = (np.sin(2 * np.pi * f0 * t)
              + 0.5 * np.sin(2 * np.pi * 2 * f0 * t)
              + 0.25 * np.sin(2 * np.pi * 3 * f0 * t))
    signal += 0.005 * np.random.default_rng(0).standard_normal(len(t))
    # Half a second of silence on each side, to exercise trimming.
    pad = np.zeros(int(0.5 * sr))
    signal = np.concatenate([pad, signal / np.max(np.abs(signal)), pad])
    sf.write(path, signal.astype(np.float32), sr)


def test_preprocess_and_features() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        wav = Path(tmp_dir) / "tone.wav"
        _make_test_tone(wav, f0=150.0)

        audio = load_and_preprocess(wav)
        assert audio.sample_rate == config.SAMPLE_RATE
        # Trimming should remove most of the 1.0 s of padded silence.
        assert audio.duration_s < audio.original_duration_s
        assert np.isclose(np.max(np.abs(audio.signal)), 0.95, atol=0.01)
        assert abs(float(np.mean(audio.signal))) < 1e-3  # DC removed

        features = extract_features(audio)
        from pvoice.features import extended_feature_names
        assert list(features.keys()) == extended_feature_names(), \
            "feature order must be stable"

        # A clean 150 Hz tone must be tracked near 150 Hz.
        assert abs(features["f0_mean_hz"] - 150.0) < 5.0
        # A nearly perfect tone has very low jitter/shimmer and high HNR.
        assert features["jitter_local"] < 0.01
        assert features["shimmer_local"] < 0.05
        assert features["hnr_mean_db"] > 20.0
        # No NaNs on a clean signal.
        bad = [k for k, v in features.items() if isinstance(v, float) and math.isnan(v)]
        assert not bad, f"unexpected NaN features: {bad}"

    print("test_preprocess_and_features: PASS")


def test_feature_names_unique() -> None:
    from pvoice.features import base_feature_names, extended_feature_names
    base = base_feature_names()
    extended = extended_feature_names()
    assert len(base) == len(set(base)) == 17 + 2 * config.N_MFCC
    assert len(extended) == len(set(extended)) == len(base) + 5 + 2 * config.N_MFCC
    assert extended[:len(base)] == base, "extended must start with base set"
    # The active set (used by the trained model) must be one of the two.
    assert feature_names() in (base, extended)
    print("test_feature_names_unique: PASS")


if __name__ == "__main__":
    test_feature_names_unique()
    test_preprocess_and_features()
    print("\nAll tests passed.")
