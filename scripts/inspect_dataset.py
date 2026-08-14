"""Inspect the MDVR-KCL dataset and write reports/dataset_report.md.

Where to run:  project folder, with .venv activated
Command:       python scripts/inspect_dataset.py

What it does:
1. Scans data/raw/mdvr_kcl for audio files.
2. Infers labels (HC/PD) and subject IDs from folders and filenames.
3. Opens every audio file to check duration, sample rate, and corruption.
4. Writes reports/dataset_report.md and data/processed/dataset_index.csv.

If the dataset is not in place yet, it prints clear instructions and exits.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

# Make "src" importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd
import soundfile as sf

from pvoice import config
from pvoice.dataset import records_to_frame, scan_dataset, usable_records


def probe_audio(path: Path) -> dict:
    """Read one audio file's header (fast) and basic signal stats."""
    info = {"duration_s": np.nan, "sample_rate": np.nan, "channels": np.nan,
            "read_error": "", "max_abs_amplitude": np.nan, "md5": ""}
    try:
        meta = sf.info(str(path))
        info["duration_s"] = meta.duration
        info["sample_rate"] = meta.samplerate
        info["channels"] = meta.channels
        data, _ = sf.read(str(path), dtype="float32", always_2d=True)
        info["max_abs_amplitude"] = float(np.max(np.abs(data))) if data.size else 0.0
        info["md5"] = hashlib.md5(path.read_bytes()).hexdigest()
    except Exception as exc:  # corrupt or unreadable file
        info["read_error"] = str(exc)
    return info


def main() -> int:
    print(f"Looking for the dataset in: {config.RAW_DATA_DIR}")
    records = scan_dataset()

    if not records:
        print()
        print("No audio files found.")
        print("Please place the extracted MDVR-KCL dataset inside:")
        print(f"    {config.RAW_DATA_DIR}")
        print("See the file README_PLACE_DATASET_HERE.txt in that folder.")
        return 1

    print(f"Found {len(records)} audio files. Probing each file "
          "(this can take a minute)...")

    frame = records_to_frame(records)
    probes = pd.DataFrame([probe_audio(Path(p)) for p in frame["path"]])
    frame = pd.concat([frame, probes], axis=1)

    # Extra suspicion flags based on audio content.
    silent = frame["max_abs_amplitude"] < 1e-4
    too_short = frame["duration_s"] < config.MIN_DURATION_S
    corrupt = frame["read_error"] != ""
    for mask, note in ((silent, "silent audio"),
                       (too_short, "shorter than minimum duration"),
                       (corrupt, "could not be read")):
        frame.loc[mask, "problems"] = frame.loc[mask, "problems"].where(
            frame.loc[mask, "problems"] == "", frame.loc[mask, "problems"] + "; "
        ) + note

    config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_csv(config.DATASET_INDEX_PATH, index=False)

    write_report(frame)
    print(f"\nWrote {config.DATASET_REPORT_PATH}")
    print(f"Wrote {config.DATASET_INDEX_PATH}")
    return 0


def write_report(frame: pd.DataFrame) -> None:
    ok = frame[(frame["problems"] == "") & frame["label"].notna()
               & frame["subject_id"].notna()]
    lines: list[str] = []
    add = lines.append

    add("# MDVR-KCL dataset inspection report")
    add("")
    add(f"Dataset folder: `{config.RAW_DATA_DIR}`")
    add("")

    add("## Folder structure")
    add("")
    add("Folders containing audio, relative to the dataset folder:")
    add("")
    folders = sorted(set(str(Path(p).parent) for p in frame["relative_path"]))
    for folder in folders:
        count = sum(str(Path(p).parent) == folder for p in frame["relative_path"])
        add(f"- `{folder}` ({count} files)")
    add("")

    add("## Overview")
    add("")
    add(f"- Total audio files found: **{len(frame)}**")
    add(f"- Usable files (label + subject ID, no problems): **{len(ok)}**")
    add(f"- Audio formats: {sorted(set(Path(p).suffix.lower() for p in frame['path']))}")
    add(f"- Sample rates: {sorted(frame['sample_rate'].dropna().unique().astype(int).tolist())}")
    add(f"- Channels: {sorted(frame['channels'].dropna().unique().astype(int).tolist())}")
    add("")

    add("## Durations (seconds)")
    add("")
    dur = frame["duration_s"].dropna()
    if not dur.empty:
        add(f"- min: {dur.min():.2f}  |  median: {dur.median():.2f}  |  "
            f"mean: {dur.mean():.2f}  |  max: {dur.max():.2f}")
    add("")

    add("## Labels and tasks")
    add("")
    add("Label was inferred from the HC/PD folder name and the `_hc_`/`_pd_` "
        "tag inside each filename. Files where the two disagree are excluded "
        "and listed under problems.")
    add("")
    add("Files per task and label:")
    add("")
    add(frame.groupby(["task", "label"], dropna=False).size()
        .rename("files").reset_index().to_markdown(index=False))
    add("")

    add("## Subjects")
    add("")
    add("Subject ID was inferred from the leading `ID<number>` token in each "
        "filename. Recordings from one subject are always kept together "
        "during validation (GroupKFold).")
    add("")
    subj = (ok.groupby(["label", "subject_id"]).size()
            .rename("recordings").reset_index())
    add(f"- Subjects with usable data: **{subj['subject_id'].nunique()}**")
    per_class = subj.groupby("label")["subject_id"].nunique()
    for label, count in per_class.items():
        add(f"- Subjects in class {label}: **{count}**")
    add("")
    add("Recordings per subject:")
    add("")
    add(subj.to_markdown(index=False))
    add("")

    add("## Integrity checks")
    add("")
    # Exact duplicate files (identical bytes) would leak between CV folds
    # if the copies carried different subject IDs.
    dup_groups = (frame[frame["md5"] != ""].groupby("md5")
                  .filter(lambda g: len(g) > 1))
    if dup_groups.empty:
        add("- Duplicate file contents (MD5): none found.")
    else:
        add("- **Duplicate file contents found:**")
        for _, group in dup_groups.groupby("md5"):
            add(f"  - {', '.join(group['relative_path'])}")
    # A subject listed under both HC and PD would make its label unreliable.
    class_overlap = (ok.groupby("subject_id")["label"].nunique())
    conflicted = class_overlap[class_overlap > 1]
    if conflicted.empty:
        add("- Subjects appearing in more than one class: none found.")
    else:
        add(f"- **Subjects in both classes: {', '.join(conflicted.index)}** "
            "- their labels are unreliable; review required.")
    add("")

    add("## Problem files")
    add("")
    problems = frame[frame["problems"] != ""]
    if problems.empty:
        add("None found.")
    else:
        add(problems[["relative_path", "problems"]].to_markdown(index=False))
    add("")

    add("## Risk notes")
    add("")
    add("- Small dataset: results may not generalize; report per-fold "
        "variation, not just the mean.")
    add("- All recordings of one subject share recording conditions; "
        "subject-independent validation is mandatory and is enforced in code.")
    add("- If accuracy looks very high (>= 95%), treat it as a warning sign "
        "and investigate for leakage before believing it.")
    add("")

    config.DATASET_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
