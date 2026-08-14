"""Predict from one audio file on the command line (Phase 5 CLI).

Where to run:  project folder, with .venv activated
Command:       python scripts/predict_file.py path\\to\\recording.wav

Exit codes: 0 = prediction shown, 1 = file problem, 2 = model/config
problem, 3 = unexpected software error (details with --debug).
"""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pvoice.predict import (
    AudioValidationError,
    PipelineConfigError,
    predict_file,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Research screening classification from a voice "
                    "recording (non-diagnostic)."
    )
    parser.add_argument("audio_file", help="Path to a .wav recording")
    parser.add_argument("--debug", action="store_true",
                        help="Show full technical error details")
    args = parser.parse_args()

    try:
        result = predict_file(Path(args.audio_file))
    except AudioValidationError as exc:
        print(f"This recording cannot be analyzed: {exc}")
        if args.debug and exc.debug:
            print(f"[debug] {exc.debug}")
        return 1
    except PipelineConfigError as exc:
        print(str(exc))
        return 2
    except Exception:
        print("Something went wrong while analyzing this file. "
              "Run again with --debug for technical details.")
        if args.debug:
            traceback.print_exc()
        return 3

    print()
    print("=" * 64)
    print("RESEARCH MODEL RESULT (non-diagnostic)")
    print("=" * 64)
    print(f"File: {result.file}")
    print(f"Duration: {result.original_duration_s:.1f} s "
          f"(analyzed after trimming: {result.duration_s:.1f} s), "
          f"original sample rate {result.original_sample_rate} Hz")
    print()
    print(result.headline)
    if result.pd_score is not None:
        print(f"Model score for the PD class: {result.pd_score:.2f} "
              "(0 = closer to HC, 1 = closer to PD).")
        print("This score is a property of the research model, NOT a "
              "person's medical risk.")
    if result.warnings:
        print()
        print("Notes about this recording:")
        for warning in result.warnings:
            print(f"  - {warning}")
    print()
    print(result.label_explanation)
    print()
    print(result.disclaimer)
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
