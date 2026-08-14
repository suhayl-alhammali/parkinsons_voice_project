"""Validate the extracted feature table and write reports/feature_report.md.

Where to run:  project folder, with .venv activated
Command:       python scripts/validate_features.py

Checks performed on data/processed/features.csv:

1. Every recording is present and traceable (subject_id, label, task, path).
2. Missing values (NaN) per feature, with an explanation of why they occur.
3. Infinite values (must be zero everywhere).
4. Impossible values, using physical plausibility ranges per feature family
   (e.g. F0 must lie inside the configured pitch search range, proportions
   must lie in [0, 1], HNR outside -20..60 dB is suspicious).
5. Suspiciously constant features (zero or near-zero variance) - these carry
   no information and usually signal an extraction bug.
6. Duplicate feature rows (identical vectors for different recordings).

The script never deletes or edits the feature table.  It only reports, so
that any exclusion decision is documented and reviewable.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from pvoice import config
from pvoice.features import feature_names

META_COLUMNS = ["relative_path", "subject_id", "task", "label", "duration_s"]
FEATURE_REPORT_PATH = config.REPORTS_DIR / "feature_report.md"

# Physical plausibility ranges.  A value outside its range is not
# automatically wrong, but must be looked at; the report lists every case.
# Praat's pitch tracker interpolates between analysis frames, so it can
# report F0 a fraction below the configured search floor (e.g. 74.95 Hz for
# a 75 Hz floor).  A 2% margin keeps the check strict while not flagging
# this normal interpolation behaviour.
_F0_LOW = config.PITCH_FLOOR_HZ * 0.98
_F0_HIGH = config.PITCH_CEILING_HZ * 1.02

PLAUSIBLE_RANGES: dict[str, tuple[float, float]] = {
    "f0_mean_hz": (_F0_LOW, _F0_HIGH),
    "f0_median_hz": (_F0_LOW, _F0_HIGH),
    "f0_min_hz": (_F0_LOW, _F0_HIGH),
    "f0_max_hz": (_F0_LOW, _F0_HIGH),
    "f0_std_hz": (0.0, (config.PITCH_CEILING_HZ - config.PITCH_FLOOR_HZ)),
    "f0_range_hz": (0.0, (config.PITCH_CEILING_HZ - config.PITCH_FLOOR_HZ)),
    "voiced_fraction": (0.0, 1.0),
    # Ratios (dimensionless). Praat reports jitter/shimmer as fractions;
    # 0.5 (=50%) is far beyond anything physiological.
    "jitter_local": (0.0, 0.5),
    "jitter_rap": (0.0, 0.5),
    "jitter_ppq5": (0.0, 0.5),
    "jitter_local_abs": (0.0, 0.01),   # seconds; >10 ms period jitter is absurd
    "shimmer_local": (0.0, 1.0),
    "shimmer_apq3": (0.0, 1.0),
    "shimmer_apq5": (0.0, 1.0),
    "shimmer_apq11": (0.0, 1.0),
    "shimmer_local_db": (0.0, 10.0),
    "hnr_mean_db": (-20.0, 60.0),
}


def main() -> int:
    if not config.FEATURE_TABLE_PATH.exists():
        print(f"Feature table not found: {config.FEATURE_TABLE_PATH}")
        print("Run: python scripts/build_features.py")
        return 1

    frame = pd.read_csv(config.FEATURE_TABLE_PATH)
    features = [c for c in frame.columns if c not in META_COLUMNS]
    lines: list[str] = []
    add = lines.append
    problems_found = 0

    add("# Phase 3 feature extraction report")
    add("")
    add(f"Feature table: `{config.FEATURE_TABLE_PATH}`")
    add("")

    # ------------------------------------------------------------------
    add("## Contents")
    add("")
    add(f"- Recordings (rows): **{len(frame)}**")
    add(f"- Feature columns: **{len(features)}**")
    add(f"- Metadata columns: {META_COLUMNS}")
    n_expected = len(feature_names())
    if len(features) != n_expected:
        add(f"- **WARNING: expected {n_expected} features, found {len(features)}**")
        problems_found += 1
    counts = frame.groupby("label").size()
    label_text = ", ".join(
        f"{config.LABEL_NAMES.get(lbl, lbl)}: {n}" for lbl, n in counts.items()
    )
    add(f"- Recordings per class: {label_text}")
    add(f"- Subjects: {frame['subject_id'].nunique()} "
        f"(traceability: every row keeps subject_id, task, label, and path)")
    add("")

    add("### Feature groups")
    add("")
    add("| group | features | source |")
    add("|:--|:--|:--|")
    add("| F0 statistics | mean, median, std, min, max, range, voiced fraction (7) | Praat pitch tracking |")
    add("| Jitter | local, local absolute, RAP, PPQ5 (4) | Praat point process |")
    add("| Shimmer | local, local dB, APQ3, APQ5, APQ11 (5) | Praat point process |")
    add("| Noise | mean HNR (1) | Praat harmonicity (cc) |")
    add(f"| MFCC | mean + std of {config.N_MFCC} coefficients ({2 * config.N_MFCC}) | librosa |")
    add("")

    # ------------------------------------------------------------------
    add("## Missing values (NaN)")
    add("")
    nan_counts = frame[features].isna().sum()
    nan_features = nan_counts[nan_counts > 0].sort_values(ascending=False)
    if nan_features.empty:
        add("No missing values anywhere in the table.")
    else:
        add("| feature | missing rows |")
        add("|:--|--:|")
        for name, count in nan_features.items():
            add(f"| {name} | {count} |")
        add("")
        add("NaN here means Praat could not measure the quantity (typically "
            "too few regular voiced periods in continuous speech), not a "
            "software crash. Rows are kept; the modeling stage imputes "
            "missing values inside each cross-validation fold.")
        nan_rows = frame[frame[features].isna().any(axis=1)]
        add("")
        add(f"Recordings affected: {len(nan_rows)} of {len(frame)}")
    add("")

    # ------------------------------------------------------------------
    add("## Infinite values")
    add("")
    inf_counts = np.isinf(frame[features].to_numpy(dtype=float)).sum(axis=0)
    inf_features = {f: int(n) for f, n in zip(features, inf_counts) if n > 0}
    if not inf_features:
        add("None found.")
    else:
        problems_found += 1
        add("**Infinite values found (must be investigated):**")
        for name, count in inf_features.items():
            add(f"- {name}: {count} rows")
    add("")

    # ------------------------------------------------------------------
    add("## Impossible / implausible values")
    add("")
    implausible: list[str] = []
    for name, (low, high) in PLAUSIBLE_RANGES.items():
        if name not in frame.columns:
            continue
        col = frame[name]
        bad = frame[(col < low) | (col > high)]
        for _, row in bad.iterrows():
            implausible.append(
                f"| {row['relative_path']} | {name} | {row[name]:.6g} "
                f"| {low:g} .. {high:g} |"
            )
    if not implausible:
        add("All values inside their physical plausibility ranges "
            "(MFCCs have no fixed range and are excluded from this check).")
    else:
        problems_found += 1
        add("| recording | feature | value | plausible range |")
        add("|:--|:--|--:|:--|")
        lines.extend(implausible)
    add("")

    # ------------------------------------------------------------------
    add("## Suspiciously constant features")
    add("")
    stds = frame[features].std()
    constant = stds[stds < 1e-12]
    near_constant = stds[(stds >= 1e-12) & (stds < 1e-6)]
    if constant.empty and near_constant.empty:
        add("None: every feature varies across recordings.")
    else:
        problems_found += 1
        for name in constant.index:
            add(f"- **{name} is constant** (zero variance) - carries no "
                "information, likely an extraction bug.")
        for name in near_constant.index:
            add(f"- {name} is nearly constant (std < 1e-6) - review.")
    add("")

    # ------------------------------------------------------------------
    add("## Duplicate feature vectors")
    add("")
    dup_mask = frame.duplicated(subset=features, keep=False)
    if not dup_mask.any():
        add("None: all recordings have distinct feature vectors.")
    else:
        problems_found += 1
        add("**Identical feature vectors for different recordings "
            "(possible duplicate audio or extraction bug):**")
        for _, row in frame[dup_mask].iterrows():
            add(f"- {row['relative_path']}")
    add("")

    # ------------------------------------------------------------------
    add("## Limitations to keep in mind")
    add("")
    add("- MDVR-KCL contains continuous speech (reading, dialogue), not "
        "sustained vowels. Jitter, shimmer and HNR are classically defined "
        "on sustained phonation, so their values here are noisier and "
        "should be interpreted as rough voice-quality indicators.")
    add("- Praat measures perturbation only on voiced stretches it can "
        "track; recordings with little stable voicing yield NaN (reported "
        "above) rather than fabricated numbers.")
    add("- MFCC summary statistics compress each whole recording into "
        "mean/std per coefficient; temporal detail is intentionally "
        "discarded for explainability.")
    add("")

    verdict = ("PASS - table is ready for modeling (Phase 4)."
               if problems_found == 0
               else f"REVIEW NEEDED - {problems_found} problem group(s) above.")
    add(f"**Validation verdict: {verdict}**")
    add("")

    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FEATURE_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {FEATURE_REPORT_PATH}")
    print(f"Verdict: {verdict}")
    return 0 if problems_found == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
