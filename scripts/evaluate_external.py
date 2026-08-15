"""External validation on the Italian Parkinson's Voice and Speech dataset.

Where to run:  project folder, with .venv activated
Command:       python scripts/evaluate_external.py

Design (approved by Hussein, see reports/italian_dataset_report.md):
1. Include only recordings >= 30 s (continuous read-speech tasks; the
   short vowel/syllable tasks do not match our pipeline's assumptions).
2. Bandwidth harmonization: EVERY included file is first downsampled to
   16 kHz (all HC files are 16 kHz natively; 160 PD files are 44.1 kHz -
   without this step the model could separate groups by bandwidth).
   The 16 kHz signal is then resampled to the pipeline's standard 44.1 kHz
   and written to a temporary WAV, so the standard preprocessing, 10-s
   segmentation, feature extraction, and chunk-mean aggregation run
   completely unchanged.
3. The MDVR-KCL-trained model is FROZEN: no retraining, no threshold
   tuning. Each recording gets a PD score; speaker score = mean over the
   speaker's included recordings.
4. Headline comparison: elderly HC vs PD (age-fair). Young HC reported
   separately. Inconclusive-band (0.35-0.65) fractions reported.

Features are cached per file in data/processed/external_cache/ so an
interrupted run resumes. Total runtime is roughly an hour (CPPS).
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import joblib
import librosa
import numpy as np
import pandas as pd
import soundfile as sf
from tqdm import tqdm

from pvoice import config
from pvoice.evaluate import compute_metrics
from pvoice.features import extract_features, feature_names
from pvoice.predict import check_pipeline_config
from pvoice.preprocess import load_and_preprocess, segment_audio

ROOT = config.DATA_DIR / "raw" / "italian_pvs"
CACHE_DIR = config.PROCESSED_DATA_DIR / "external_cache"
OUT_CSV = config.PROCESSED_DATA_DIR / "external_predictions.csv"
REPORT = config.REPORTS_DIR / "external_validation_report.md"

MIN_DURATION_S = 30.0
HARMONIZE_SR = 16000

GROUP_MAP = {
    "young healthy": ("HC", "young"),
    "elderly healthy": ("HC", "elderly"),
    "parkinson": ("PD", "elderly"),
}


def classify_group(folder_name: str):
    lower = folder_name.lower()
    for fragment, (label, age) in GROUP_MAP.items():
        if fragment in lower:
            return label, age
    return None, None


def collect_files() -> list[dict]:
    """All eligible recordings with group/speaker metadata."""
    records = []
    for path in sorted(ROOT.rglob("*.wav")):
        rel = path.relative_to(ROOT)
        if len(rel.parts) < 3:
            continue
        group_folder = rel.parts[1]
        label, age = classify_group(group_folder)
        if label is None:
            continue
        try:
            info = sf.info(str(path))
        except Exception:
            continue
        if info.duration < MIN_DURATION_S:
            continue
        records.append({
            "rel": str(rel),
            "path": path,
            "label": label,
            "age_group": age,
            "speaker": f"{group_folder}/{path.parent.name}",
            "duration_s": float(info.duration),
            "native_sr": int(info.samplerate),
        })
    return records


def _cache_path(rel: str) -> Path:
    return CACHE_DIR / (re.sub(r"[^A-Za-z0-9_.-]", "_", rel) + ".json")


def harmonized_features(path: Path) -> dict[str, float]:
    """Bandwidth-harmonize, then run the standard pipeline unchanged."""
    # Step 1: force everything through 16 kHz (kills content above 8 kHz
    # for the 44.1 kHz PD files, exactly matching the HC files' bandwidth).
    signal16, _ = librosa.load(path, sr=HARMONIZE_SR, mono=True)
    signal44 = librosa.resample(signal16, orig_sr=HARMONIZE_SR,
                                target_sr=config.SAMPLE_RATE)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        sf.write(tmp_path, signal44.astype(np.float32), config.SAMPLE_RATE)
        # Step 2: the exact same pipeline as training/prediction.
        audio = load_and_preprocess(tmp_path)
        chunks = segment_audio(audio)
        chunk_rows = [extract_features(chunk) for chunk in chunks]
        return pd.DataFrame(chunk_rows).mean(axis=0).to_dict()
    finally:
        tmp_path.unlink(missing_ok=True)


def main() -> int:
    check_pipeline_config()
    model = joblib.load(config.MODEL_FILE)

    records = collect_files()
    if not records:
        print("No eligible recordings found - check the dataset location.")
        return 1
    print(f"{len(records)} recordings >= {MIN_DURATION_S:.0f}s from "
          f"{len({r['speaker'] for r in records})} speakers.")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    failures = []
    for record in tqdm(records, unit="file"):
        cache = _cache_path(record["rel"])
        if cache.exists():
            features = json.loads(cache.read_text(encoding="utf-8"))
        else:
            try:
                features = harmonized_features(record["path"])
            except Exception as exc:
                failures.append((record["rel"], f"{type(exc).__name__}: {exc}"))
                continue
            cache.write_text(json.dumps(features), encoding="utf-8")
        X = pd.DataFrame([features], columns=feature_names())
        prob = float(model.predict_proba(X)[0, 1])
        rows.append({**{k: record[k] for k in
                        ("rel", "label", "age_group", "speaker",
                         "duration_s", "native_sr")},
                     "prob_pd": prob})

    frame = pd.DataFrame(rows)
    frame.to_csv(OUT_CSV, index=False)
    print(f"Saved per-recording predictions: {OUT_CSV}")
    if failures:
        print(f"WARNING: {len(failures)} failures:")
        for rel, err in failures:
            print(f"  {rel}: {err}")

    write_report(frame, failures)
    return 0


def band_fraction(probs: pd.Series) -> float:
    return float(((probs >= config.UNCERTAIN_LOW)
                  & (probs <= config.UNCERTAIN_HIGH)).mean())


def write_report(frame: pd.DataFrame, failures: list) -> None:
    speakers = (frame.groupby("speaker")
                .agg(label=("label", "first"),
                     age_group=("age_group", "first"),
                     n_recordings=("prob_pd", "size"),
                     prob_pd=("prob_pd", "mean"))
                .reset_index())
    speakers["y_true"] = (speakers["label"] == "PD").astype(int)
    speakers["y_pred"] = (speakers["prob_pd"] >= 0.5).astype(int)

    elderly = speakers[speakers["age_group"] == "elderly"]
    young = speakers[speakers["age_group"] == "young"]
    headline = compute_metrics(elderly["y_true"].to_numpy(),
                               elderly["y_pred"].to_numpy(),
                               elderly["prob_pd"].to_numpy())

    lines = [
        "# External validation: Italian Parkinson's Voice and Speech",
        "",
        "**Frozen MDVR-KCL model, zero adaptation. Cross-dataset AND "
        "cross-language (English -> Italian). This measures "
        "generalization; lower numbers than the internal 0.822 were "
        "expected by design.**",
        "",
        "## Setup",
        "",
        f"- Included: {len(frame)} recordings >= 30 s "
        f"({len(speakers)} speakers; per-speaker score = mean over their "
        "recordings, threshold 0.5).",
        "- All audio bandwidth-harmonized to 16 kHz before the standard "
        "pipeline (prevents the sample-rate/label confound documented in "
        "italian_dataset_report.md).",
        f"- Failures: {len(failures)}.",
        "",
        "## Headline: elderly HC vs PD (age-fair, subject level)",
        "",
        "| metric | value |",
        "|:--|--:|",
    ]
    for key in ("balanced_accuracy", "sensitivity_pd", "specificity_hc",
                "roc_auc"):
        lines.append(f"| {key} | {headline[key]:.3f} |")
    tn = int(((elderly.y_true == 0) & (elderly.y_pred == 0)).sum())
    fp = int(((elderly.y_true == 0) & (elderly.y_pred == 1)).sum())
    fn = int(((elderly.y_true == 1) & (elderly.y_pred == 0)).sum())
    tp = int(((elderly.y_true == 1) & (elderly.y_pred == 1)).sum())
    lines += [
        "",
        f"Confusion (subject level): elderly HC {tn} correct / {fp} "
        f"flagged PD; PD {tp} caught / {fn} missed.",
        "",
        "## Secondary observations",
        "",
        f"- Young HC ({len(young)} speakers, all healthy): "
        f"{int((young.y_pred == 0).sum())} classified HC, "
        f"{int((young.y_pred == 1).sum())} flagged PD "
        f"(specificity {float((young.y_pred == 0).mean()):.3f}).",
        f"- Inconclusive-band fraction (recordings): "
        f"{band_fraction(frame['prob_pd']):.1%}; per speaker group: "
        f"elderly HC {band_fraction(elderly[elderly.y_true == 0]['prob_pd']):.1%}, "
        f"PD {band_fraction(elderly[elderly.y_true == 1]['prob_pd']):.1%}, "
        f"young HC {band_fraction(young['prob_pd']):.1%}.",
        f"- Mean PD score by group: "
        f"elderly HC {elderly[elderly.y_true == 0]['prob_pd'].mean():.3f}, "
        f"PD {elderly[elderly.y_true == 1]['prob_pd'].mean():.3f}, "
        f"young HC {young['prob_pd'].mean():.3f}.",
        "",
        "## Interpretation notes",
        "",
        "- The model never saw Italian speech, these microphones, or the "
        "16 kHz bandwidth during training; every gap between this result "
        "and the internal 0.822 quantifies domain shift.",
        "- Bandwidth harmonization makes the comparison fair WITHIN the "
        "Italian dataset but also removes high-frequency content the "
        "model's MFCC features saw during training, shifting absolute "
        "scores; discrimination (AUC) is the most meaningful number here.",
        "- Speaker-level results dominate: recordings per speaker vary "
        "(1-4 included), so per-recording metrics are secondary.",
        "",
    ]
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    raise SystemExit(main())
