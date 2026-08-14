"""Streamlit prototype: select a voice recording, get a research result.

Where to run:  project folder, with .venv activated
Command:       streamlit run app.py

Requires a trained model in models/ (run scripts/train_models.py first,
which itself requires Phases 2-3 to be complete).

The interface never shows technical tracebacks.  Unexpected errors are
logged to the terminal that runs Streamlit; the user sees a short plain
message instead.
"""

from __future__ import annotations

import logging
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st

from pvoice import config
from pvoice.predict import (
    AudioValidationError,
    PipelineConfigError,
    check_pipeline_config,
    predict_file,
)

logger = logging.getLogger("pvoice.app")
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Voice Screening Research Prototype",
                   page_icon="🎙️")

st.title("Parkinson's-Related Voice Changes — Research Prototype")

# The mandatory notice, always visible at the top.
st.warning(config.DISCLAIMER)

st.markdown(
    "Select a voice recording (WAV format). The system extracts acoustic "
    "features (F0, jitter, shimmer, HNR, MFCC) with the same pipeline used "
    "in training, and applies a machine learning model trained on the "
    "MDVR-KCL research dataset."
)

with st.expander("What do HC and PD mean here?"):
    st.markdown(config.LABEL_EXPLANATION)

# Fail early and safely if the model or its configuration is unusable.
try:
    check_pipeline_config()
except PipelineConfigError as exc:
    st.error(str(exc))
    st.stop()

uploaded = st.file_uploader("Choose a WAV audio file", type=["wav"])

if uploaded is not None:
    # Streamlit keeps uploads in memory; the pipeline needs a real file
    # path, so the bytes go to a temporary file that is always deleted in
    # the finally-block below.  Nothing the user uploads is kept.
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=Path(uploaded.name).suffix, delete=False
        ) as tmp:
            tmp.write(uploaded.getvalue())
            tmp_path = Path(tmp.name)

        with st.spinner("Analyzing recording (about 1 minute for a "
                        "2-minute recording)..."):
            result = predict_file(tmp_path)

    except AudioValidationError as exc:
        st.error(f"This recording cannot be analyzed: {exc}")
        if exc.debug:
            logger.error("Audio validation failed for %s: %s",
                         uploaded.name, exc.debug)
    except PipelineConfigError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Something went wrong while analyzing this file. "
                 "Please try a different WAV recording. Technical details "
                 "were written to the terminal for debugging.")
        logger.exception("Unexpected error analyzing %s", uploaded.name)
    else:
        st.subheader("File information")
        st.markdown(
            f"- **File:** {uploaded.name}\n"
            f"- **Duration:** {result.original_duration_s:.1f} s "
            f"(analyzed after silence trimming: {result.duration_s:.1f} s)\n"
            f"- **Original sample rate:** {result.original_sample_rate} Hz"
        )

        st.subheader("Research model result")
        st.markdown(f"**{result.headline}**")
        if result.pd_score is not None:
            st.markdown(
                f"Model score for the PD class: **{result.pd_score:.2f}** "
                "(0 = closer to HC class, 1 = closer to PD class). This is "
                "a property of the research model, **not** a person's "
                "medical risk or probability of disease."
            )
        for warning in result.warnings:
            st.warning(f"Note about this recording: {warning}")

        st.info(config.DISCLAIMER)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
