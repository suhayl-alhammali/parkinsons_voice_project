"""Build the feature table from all usable dataset recordings (Phase 3).

Where to run:  project folder, with .venv activated
Command:       python scripts/build_features.py

Reads every usable audio file, applies the standard preprocessing, extracts
the full feature vector, and saves data/processed/features.csv with one row
per recording (including label and subject_id for grouped validation).

Extraction takes ~10-15 seconds per recording, so results are cached one
JSON file per recording in data/processed/feature_cache/.  If the run is
interrupted, simply run the script again: finished recordings are skipped.
Delete the cache folder to force a full re-extraction (do this whenever the
preprocessing or feature settings change).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
from tqdm import tqdm

from pvoice import config
from pvoice.dataset import scan_dataset, usable_records
from pvoice.features import extract_features, feature_names
from pvoice.preprocess import load_and_preprocess

CACHE_DIR = config.PROCESSED_DATA_DIR / "feature_cache"


def _cache_path(relative_path: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", relative_path)
    return CACHE_DIR / (safe + ".json")


def main() -> int:
    records = usable_records(scan_dataset())
    if not records:
        print("No usable audio files found. Run scripts/inspect_dataset.py "
              "first and check the dataset location.")
        return 1

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached = sum(_cache_path(r.relative_path).exists() for r in records)
    if cached:
        print(f"Resuming: {cached} of {len(records)} recordings already done.")

    print(f"Extracting features from {len(records)} recordings...")
    rows = []
    failures = []
    for record in tqdm(records, unit="file"):
        cache_file = _cache_path(record.relative_path)
        if cache_file.exists():
            rows.append(json.loads(cache_file.read_text(encoding="utf-8")))
            continue
        try:
            audio = load_and_preprocess(record.path)
            features = extract_features(audio)
        except Exception as exc:
            failures.append((record.relative_path, str(exc)))
            continue
        row = {
            "relative_path": record.relative_path,
            "subject_id": record.subject_id,
            "task": record.task,
            "label": config.LABEL_PD if record.label == "PD" else config.LABEL_HC,
            "duration_s": audio.duration_s,
        }
        row.update(features)
        cache_file.write_text(json.dumps(row), encoding="utf-8")
        rows.append(row)

    frame = pd.DataFrame(rows, columns=["relative_path", "subject_id", "task",
                                        "label", "duration_s"] + feature_names())
    config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_csv(config.FEATURE_TABLE_PATH, index=False)
    print(f"\nSaved feature table: {config.FEATURE_TABLE_PATH}")
    print(f"Rows: {len(frame)}, feature columns: {len(feature_names())}")

    if failures:
        print(f"\nWARNING: {len(failures)} files failed feature extraction:")
        for path, error in failures:
            print(f"  {path}: {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
