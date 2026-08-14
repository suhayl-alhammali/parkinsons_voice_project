"""Inspect the Italian Parkinson's Voice and Speech dataset (external set).

Where to run:  project folder, with .venv activated
Command:       python scripts/inspect_italian_dataset.py

The dataset (downloaded from the Hugging Face mirror
birgermoell/Italian_Parkinsons_Voice_and_Speech, CC-BY-4.0) is used ONLY
as an external test set: our MDVR-KCL-trained model is evaluated on it,
never trained on it.

This script discovers the structure instead of assuming it:
- group folders (healthy young / healthy elderly / Parkinson's)
- speaker subfolders inside each group
- audio formats, sample rates, channels, durations
- unreadable / empty / very short files
and writes reports/italian_dataset_report.md for review BEFORE any
evaluation is run (same discipline as Phase 2 for MDVR-KCL).
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import soundfile as sf

from pvoice import config

ROOT = config.DATA_DIR / "raw" / "italian_pvs"
REPORT = config.REPORTS_DIR / "italian_dataset_report.md"
AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".m4a", ".ogg"}

# Folder-name fragments -> (label, age_group).  Discovered names are
# reported verbatim too, so a mismatch is visible instead of silent.
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


def main() -> int:
    if not ROOT.exists():
        print(f"Dataset folder not found: {ROOT}")
        return 1

    audio_files = [p for p in ROOT.rglob("*")
                   if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS]
    if not audio_files:
        print(f"No audio files found under {ROOT}")
        return 1
    print(f"Found {len(audio_files)} audio files. Probing (takes a minute)...")

    rows = []
    problems = []
    for path in audio_files:
        rel = path.relative_to(ROOT)
        parts = rel.parts
        # Layouts differ per group:
        #   HC: italian_parkinson/<group>/<speaker>/<file>
        #   PD: italian_parkinson/<group>/<batch>/<speaker>/<file>
        # The speaker folder is always the file's direct parent.
        group_folder = parts[1] if len(parts) >= 3 else parts[0]
        speaker = path.parent.name if path.parent.name != group_folder else "?"
        label, age = classify_group(group_folder)
        try:
            info = sf.info(str(path))
            duration = float(info.duration)
            sr = int(info.samplerate)
            channels = int(info.channels)
            fmt = info.format
        except Exception as exc:
            problems.append(f"unreadable: {rel} ({type(exc).__name__})")
            continue
        if duration < 1.0:
            problems.append(f"very short ({duration:.2f}s): {rel}")
        rows.append({
            "rel": str(rel), "group_folder": group_folder,
            "label": label, "age": age, "speaker": speaker,
            "duration": duration, "sr": sr, "channels": channels,
            "fmt": fmt,
        })

    lines = ["# External dataset report: Italian Parkinson's Voice and Speech",
             "",
             "Source: Hugging Face mirror `birgermoell/"
             "Italian_Parkinsons_Voice_and_Speech` (CC-BY-4.0); original "
             "dataset by Dimauro & Girardi, IEEE DataPort.",
             "Role in this project: **external test set only** - the model "
             "is never trained on it.",
             ""]
    add = lines.append

    add(f"- Audio files probed: {len(rows)} "
        f"(of {len(audio_files)} found)")
    group_counts = Counter(r["group_folder"] for r in rows)
    add("")
    add("## Groups (folder names verbatim)")
    add("")
    add("| group folder | mapped label | age group | files | speakers |")
    add("|:--|:--|:--|--:|--:|")
    for group, count in sorted(group_counts.items()):
        speakers = {r["speaker"] for r in rows if r["group_folder"] == group}
        label = next(r["label"] for r in rows if r["group_folder"] == group)
        age = next(r["age"] for r in rows if r["group_folder"] == group)
        add(f"| {group} | {label} | {age} | {count} | {len(speakers)} |")
    unmapped = [r for r in rows if r["label"] is None]
    if unmapped:
        add("")
        add(f"**WARNING: {len(unmapped)} files in unmapped group folders** - "
            "review before use: "
            + ", ".join(sorted({r['group_folder'] for r in unmapped})))
    add("")

    add("## Files per speaker")
    add("")
    per_speaker = defaultdict(int)
    for r in rows:
        per_speaker[(r["group_folder"], r["speaker"])] += 1
    counts = sorted(per_speaker.values())
    add(f"- Speakers total: {len(per_speaker)}")
    add(f"- Files per speaker: min {counts[0]}, median "
        f"{counts[len(counts) // 2]}, max {counts[-1]}")
    add("")

    add("## Audio properties")
    add("")
    sr_counts = Counter(r["sr"] for r in rows)
    ch_counts = Counter(r["channels"] for r in rows)
    fmt_counts = Counter(r["fmt"] for r in rows)
    add("Sample rate by group (a correlation between sample rate and "
        "label would be a channel confound for the evaluation):")
    add("")
    add("| group | " + " | ".join(str(sr) for sr in sorted(sr_counts)) + " |")
    add("|:--|" + "--:|" * len(sr_counts))
    for group in sorted(group_counts):
        cells = []
        for sr in sorted(sr_counts):
            cells.append(str(sum(1 for r in rows
                                 if r["group_folder"] == group
                                 and r["sr"] == sr)))
        add(f"| {group} | " + " | ".join(cells) + " |")
    add("")
    durations = sorted(r["duration"] for r in rows)
    add(f"- Sample rates: {dict(sr_counts)}")
    add(f"- Channels: {dict(ch_counts)}")
    add(f"- Formats: {dict(fmt_counts)}")
    total_h = sum(durations) / 3600
    add(f"- Durations: min {durations[0]:.1f}s, median "
        f"{durations[len(durations) // 2]:.1f}s, max {durations[-1]:.1f}s, "
        f"total {total_h:.1f}h")
    short = sum(1 for d in durations if d < 10)
    add(f"- Files shorter than 10 s: {short} "
        "(short vowel/syllable tasks; only longer read-text recordings "
        "match our training conditions)")
    add("")

    add("## Example filenames (first 3 per group)")
    add("")
    for group in sorted(group_counts):
        add(f"**{group}**")
        for r in [r for r in rows if r["group_folder"] == group][:3]:
            add(f"- `{r['rel']}` ({r['duration']:.1f}s)")
        add("")

    add("## Problems")
    add("")
    if problems:
        for p in problems[:50]:
            add(f"- {p}")
        if len(problems) > 50:
            add(f"- ... and {len(problems) - 50} more")
    else:
        add("None: all files readable, none shorter than 1 s.")
    add("")

    add("## Risks and notes for the external evaluation")
    add("")
    add("- Language differs (Italian vs English training data): read-text "
        "content and phonetics shift MFCC-type features; perturbation "
        "features (jitter, shimmer, HNR, CPPS) are more "
        "language-independent.")
    add("- The young-HC group makes age a confound: the fair comparison "
        "for our model is ELDERLY HC vs PD; young-HC results are reported "
        "separately.")
    add("- Recording equipment and rooms differ from MDVR-KCL; this is "
        "exactly the domain shift the external evaluation measures.")
    add("- Sample rates differing from 44100 Hz are resampled by our "
        "standard pipeline (and flagged).")
    add("- **Sample-rate/label confound found**: every 44100 Hz file "
        "belongs to the PD group (all HC files are 16000 Hz). A fair "
        "evaluation must bandwidth-harmonize: downsample ALL Italian "
        "files to 16 kHz first (removing content above 8 kHz everywhere) "
        "so the model cannot separate groups by recording bandwidth.")
    add("- Task types differ: vowels/syllables vs continuous speech. Only "
        "recordings long enough for our pipeline (>= 30 s continuous "
        "speech, ideally read text) should enter the headline comparison; "
        "the evaluation script must state its inclusion rule.")

    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
