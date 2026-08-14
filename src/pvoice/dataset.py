"""Dataset discovery for MDVR-KCL: find audio files, labels, and subject IDs.

Expected MDVR-KCL layout after the student extracts the download into
``data/raw/mdvr_kcl`` (the inspection script also tolerates one extra level
of nesting, e.g. a top folder created by the zip):

    data/raw/mdvr_kcl/
        ReadText/
            HC/   ID00_hc_0_0_0.wav ...
            PD/   ID02_pd_2_1_1.wav ...
        SpontaneousDialogue/
            HC/   ...
            PD/   ...

Labels are inferred from BOTH the folder name (HC/PD) and the filename tag
(_hc_/_pd_).  If the two disagree for any file, the scan reports it as a
label conflict and that file must be reviewed before training.

Subject IDs are inferred from the leading "ID<number>" token in filenames.
Files without a recognizable subject ID are flagged; subject-independent
validation is impossible for such files, so they are excluded and reported.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd

from . import config

AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".m4a", ".ogg"}

# "ID00_hc_0_0_0.wav" -> subject "ID00", label tag "hc"
FILENAME_PATTERN = re.compile(r"^(ID\d+)[_-]?(hc|pd)?", re.IGNORECASE)


@dataclass
class AudioRecord:
    """One audio file with everything needed for grouped validation."""

    path: Path
    relative_path: str
    task: Optional[str]          # e.g. "ReadText" or "SpontaneousDialogue"
    label_from_folder: Optional[str]   # "HC" / "PD" from folder name
    label_from_name: Optional[str]     # "HC" / "PD" from filename tag
    subject_id: Optional[str]          # e.g. "ID00"
    problems: list[str] = field(default_factory=list)

    @property
    def label(self) -> Optional[str]:
        """Final label, only when the available sources agree."""
        sources = {s for s in (self.label_from_folder, self.label_from_name) if s}
        if len(sources) == 1:
            return next(iter(sources))
        return None  # missing or conflicting


def find_dataset_root(base: Path = config.RAW_DATA_DIR) -> Optional[Path]:
    """Locate the folder that actually contains the task folders.

    Handles the common case where extracting the zip creates one extra
    directory level.  Returns None when no audio files exist under ``base``.
    """
    if not base.exists():
        return None
    if any(_iter_audio_files(base)):
        return base
    return None


def _iter_audio_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
            yield path


def _label_from_parts(parts: tuple[str, ...]) -> Optional[str]:
    """Look for an HC/PD folder anywhere in the relative path."""
    for part in parts:
        upper = part.upper()
        if upper == "HC":
            return "HC"
        if upper == "PD":
            return "PD"
    return None


def _task_from_parts(parts: tuple[str, ...]) -> Optional[str]:
    """First folder level that is not HC/PD is treated as the task name."""
    for part in parts[:-1]:  # exclude the filename itself
        if part.upper() not in {"HC", "PD"}:
            return part
    return None


def scan_dataset(base: Path = config.RAW_DATA_DIR) -> list[AudioRecord]:
    """Scan the raw data folder and build one AudioRecord per audio file.

    This function only *finds and labels* files.  It does not open them;
    audio-level checks (duration, corruption) live in the inspection script
    because they require reading every file.
    """
    root = find_dataset_root(base)
    if root is None:
        return []

    records: list[AudioRecord] = []
    for path in _iter_audio_files(root):
        rel = path.relative_to(root)
        parts = rel.parts

        label_folder = _label_from_parts(parts[:-1])
        match = FILENAME_PATTERN.match(path.stem)
        subject_id = None
        label_name = None
        if match:
            subject_id = match.group(1).upper()
            if match.group(2):
                label_name = match.group(2).upper()

        record = AudioRecord(
            path=path,
            relative_path=str(rel),
            task=_task_from_parts(parts),
            label_from_folder=label_folder,
            label_from_name=label_name,
            subject_id=subject_id,
        )

        if record.subject_id is None:
            record.problems.append("no subject ID in filename")
        if record.label_from_folder and record.label_from_name and \
                record.label_from_folder != record.label_from_name:
            record.problems.append(
                f"label conflict: folder says {record.label_from_folder}, "
                f"filename says {record.label_from_name}"
            )
        if record.label is None and not record.problems:
            record.problems.append("no label found in folder or filename")

        records.append(record)
    return records


def records_to_frame(records: list[AudioRecord]) -> pd.DataFrame:
    """Convert scan results to a DataFrame (one row per audio file)."""
    rows = []
    for r in records:
        rows.append(
            {
                "relative_path": r.relative_path,
                "task": r.task,
                "subject_id": r.subject_id,
                "label": r.label,
                "label_from_folder": r.label_from_folder,
                "label_from_name": r.label_from_name,
                "problems": "; ".join(r.problems),
                "path": str(r.path),
            }
        )
    return pd.DataFrame(rows)


def usable_records(records: list[AudioRecord]) -> list[AudioRecord]:
    """Records that have both a consistent label and a subject ID."""
    return [r for r in records if r.label is not None and r.subject_id is not None]
