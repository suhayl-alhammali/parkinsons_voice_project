"""Phase 5 prediction-path tests (need the trained model from Phase 4).

Where to run:  project folder, with .venv activated
Command:       python tests/test_prediction.py

Covers, as required by Phase 5:
1. Successful prediction on a valid synthetic WAV (same code path the
   Streamlit app and the CLI both call).
2. Pipeline-configuration mismatch -> PipelineConfigError, no prediction.
3. Missing configuration file -> PipelineConfigError.
4. Invalid audio: missing, empty, corrupted, silent, and too-short files
   -> AudioValidationError with a user-friendly message.
5. The result object carries the mandatory cautious wording.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import soundfile as sf

from pvoice import config
from pvoice.predict import (
    AudioValidationError,
    PipelineConfigError,
    check_pipeline_config,
    current_pipeline_config,
    predict_file,
)


def _write_tone(path: Path, seconds: float = 5.0, amplitude: float = 0.8,
                f0: float = 140.0) -> None:
    sr = config.SAMPLE_RATE
    t = np.arange(int(sr * seconds)) / sr
    signal = amplitude * (np.sin(2 * np.pi * f0 * t)
                          + 0.4 * np.sin(2 * np.pi * 2 * f0 * t))
    signal += 0.01 * np.random.default_rng(1).standard_normal(len(t))
    sf.write(path, (signal / np.max(np.abs(signal)) * amplitude
                    ).astype(np.float32), sr)


def test_successful_prediction(tmp_dir: Path) -> None:
    wav = tmp_dir / "voice.wav"
    _write_tone(wav)
    result = predict_file(wav)
    assert result.predicted_label in ("HC", "PD", "UNCERTAIN")
    if result.predicted_label == "UNCERTAIN":
        assert "could not clearly assign" in result.headline
    else:
        assert result.headline.startswith(
            "The acoustic pattern was classified by the research model "
            "as closer to")
    assert result.pd_score is None or 0.0 <= result.pd_score <= 1.0
    assert "not a medical diagnostic tool" in result.disclaimer
    # 5 s recording is far below the ~2-minute training recordings.
    assert any("less reliable" in w for w in result.warnings)
    print("test_successful_prediction: PASS "
          f"(label={result.predicted_label}, score={result.pd_score:.2f})")


def test_uncertain_band() -> None:
    from pvoice.predict import classify_score

    assert classify_score(0.20, "HC")[0] == "HC"
    assert classify_score(0.80, "HC")[0] == "PD"
    for score in (0.35, 0.50, 0.65):
        label, headline = classify_score(score, "PD")
        assert label == "UNCERTAIN"
        assert "could not clearly assign" in headline
    # Just outside the band -> hard call again.
    assert classify_score(0.349, "PD")[0] == "HC"
    assert classify_score(0.651, "HC")[0] == "PD"
    # No probability available -> fall back to the model's class.
    assert classify_score(None, "PD")[0] == "PD"
    print("test_uncertain_band: PASS")


def test_config_mismatch(tmp_dir: Path) -> None:
    bad = current_pipeline_config()
    bad["sample_rate"] = 16000  # pretend the model was trained differently
    bad_path = tmp_dir / "pipeline_config.json"
    bad_path.write_text(json.dumps(bad))
    try:
        check_pipeline_config(config_path=bad_path)
    except PipelineConfigError as exc:
        assert "Retrain" in str(exc)
        print("test_config_mismatch: PASS")
        return
    raise AssertionError("mismatched config was accepted")


def test_config_missing(tmp_dir: Path) -> None:
    try:
        check_pipeline_config(config_path=tmp_dir / "does_not_exist.json")
    except PipelineConfigError:
        print("test_config_missing: PASS")
        return
    raise AssertionError("missing config was accepted")


def test_feature_list_mismatch(tmp_dir: Path) -> None:
    bad = current_pipeline_config()
    bad["feature_names"] = bad["feature_names"][:-1]  # one feature removed
    bad_path = tmp_dir / "pipeline_config.json"
    bad_path.write_text(json.dumps(bad))
    try:
        check_pipeline_config(config_path=bad_path)
    except PipelineConfigError as exc:
        assert "feature_names" in str(exc)
        print("test_feature_list_mismatch: PASS")
        return
    raise AssertionError("wrong feature list was accepted")


def test_invalid_audio(tmp_dir: Path) -> None:
    cases = {}

    missing = tmp_dir / "missing.wav"
    cases["missing file"] = missing

    empty = tmp_dir / "empty.wav"
    empty.write_bytes(b"")
    cases["empty file"] = empty

    corrupt = tmp_dir / "corrupt.wav"
    corrupt.write_bytes(b"this is definitely not audio data" * 100)
    cases["corrupted file"] = corrupt

    silent = tmp_dir / "silent.wav"
    sf.write(silent, np.zeros(config.SAMPLE_RATE * 3, dtype=np.float32),
             config.SAMPLE_RATE)
    cases["silent recording"] = silent

    short = tmp_dir / "short.wav"
    _write_tone(short, seconds=0.3)
    cases["too-short recording"] = short

    for name, path in cases.items():
        try:
            predict_file(path)
        except AudioValidationError as exc:
            assert str(exc), "message must not be empty"
            assert "Traceback" not in str(exc)
            print(f"test_invalid_audio [{name}]: PASS ({exc})")
        else:
            raise AssertionError(f"{name} was accepted for prediction")


if __name__ == "__main__":
    if not config.MODEL_FILE.exists():
        print("SKIP: no trained model found; run scripts/train_models.py first.")
        raise SystemExit(1)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        test_successful_prediction(tmp_dir)
        test_uncertain_band()
        test_config_mismatch(tmp_dir)
        test_config_missing(tmp_dir)
        test_feature_list_mismatch(tmp_dir)
        test_invalid_audio(tmp_dir)
    print("\nAll prediction tests passed.")
