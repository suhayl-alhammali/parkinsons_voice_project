"""Build the chunk-level feature table (accuracy-improvement phase).

Where to run:  project folder, with .venv activated
Command:       python scripts/build_segment_features.py

Splits every usable recording into 10-second chunks (after the standard
preprocessing) and extracts the FULL extended feature set (base 43 + CPPS
+ pause statistics + delta-MFCC = 74) for every chunk.

Output: data/processed/segment_features.csv - one row per chunk, keeping
subject_id, label, task, source file, and chunk index for full
traceability and grouped validation.

Like build_features.py, results are cached per recording in
data/processed/segment_cache/ so an interrupted run resumes.  Extraction
takes ~40-60 s per recording (CPPS is expensive), ~50-70 minutes in total.
Delete the cache folder to force re-extraction after pipeline changes.
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
from pvoice.features import extended_feature_names, extract_features
from pvoice.preprocess import load_and_preprocess, segment_audio

CACHE_DIR = config.PROCESSED_DATA_DIR / "segment_cache"
OUTPUT_PATH = config.PROCESSED_DATA_DIR / "segment_features.csv"

META_COLUMNS = ["relative_path", "subject_id", "task", "label",
                "chunk_index", "chunk_start_s", "duration_s"]


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

    rows: list[dict] = []
    failures: list[tuple[str, str]] = []
    for record in tqdm(records, unit="file"):
        cache_file = _cache_path(record.relative_path)
        if cache_file.exists():
            rows.extend(json.loads(cache_file.read_text(encoding="utf-8")))
            continue
        try:
            audio = load_and_preprocess(record.path)
            chunks = segment_audio(audio)
            file_rows = []
            for index, chunk in enumerate(chunks):
                features = extract_features(chunk)
                file_rows.append({
                    "relative_path": record.relative_path,
                    "subject_id": record.subject_id,
                    "task": record.task,
                    "label": (config.LABEL_PD if record.label == "PD"
                              else config.LABEL_HC),
                    "chunk_index": index,
                    "chunk_start_s": index * config.SEGMENT_SECONDS,
                    "duration_s": chunk.duration_s,
                    **features,
                })
        except Exception as exc:
            failures.append((record.relative_path, str(exc)))
            continue
        cache_file.write_text(json.dumps(file_rows), encoding="utf-8")
        rows.extend(file_rows)

    frame = pd.DataFrame(rows,
                         columns=META_COLUMNS + extended_feature_names())
    config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved chunk feature table: {OUTPUT_PATH}")
    print(f"Chunks: {len(frame)} from "
          f"{frame['relative_path'].nunique()} recordings, "
          f"feature columns: {len(extended_feature_names())}")

    if failures:
        print(f"\nWARNING: {len(failures)} files failed:")
        for path, error in failures:
            print(f"  {path}: {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
