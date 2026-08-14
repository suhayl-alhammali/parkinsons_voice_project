"""Central configuration for the whole pipeline.

Every stage (training, evaluation, prediction) must read its settings from
here so that the exact same pipeline is applied everywhere.  Do not hard-code
sample rates, pitch ranges, or paths anywhere else.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# Project root = folder that contains "src", "data", "models", ...
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
# The student must place the extracted MDVR-KCL dataset inside this folder.
# See data/raw/mdvr_kcl/README_PLACE_DATASET_HERE.txt for instructions.
RAW_DATA_DIR = DATA_DIR / "raw" / "mdvr_kcl"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

FEATURE_TABLE_PATH = PROCESSED_DATA_DIR / "features.csv"
DATASET_INDEX_PATH = PROCESSED_DATA_DIR / "dataset_index.csv"
DATASET_REPORT_PATH = REPORTS_DIR / "dataset_report.md"

# ---------------------------------------------------------------------------
# Audio preprocessing
# ---------------------------------------------------------------------------

# All audio is converted to mono and resampled to this rate before analysis.
# 44100 Hz matches the native rate of MDVR-KCL recordings; keeping it avoids
# resampling artefacts in jitter/shimmer measurements.
SAMPLE_RATE = 44100

# Silence trimming (librosa.effects.trim) threshold in dB below peak.
TRIM_TOP_DB = 30

# Recordings shorter than this (seconds, after trimming) are flagged as
# suspicious in the dataset report and excluded from training.
MIN_DURATION_S = 1.0

# ---------------------------------------------------------------------------
# Pitch / perturbation analysis (Parselmouth / Praat)
# ---------------------------------------------------------------------------

# Pitch search range in Hz.  75-500 covers adult male and female speech and
# is the standard Praat range for pathological voice work.
PITCH_FLOOR_HZ = 75.0
PITCH_CEILING_HZ = 500.0

# Standard Praat point-process settings for jitter/shimmer.
JITTER_SHIMMER_PERIOD_FLOOR = 0.0001   # seconds
JITTER_SHIMMER_PERIOD_CEILING = 0.02   # seconds
JITTER_SHIMMER_MAX_PERIOD_FACTOR = 1.3
SHIMMER_MAX_AMPLITUDE_FACTOR = 1.6

# Harmonicity (HNR) analysis settings (Praat "To Harmonicity (cc)").
HNR_TIME_STEP = 0.01
HNR_SILENCE_THRESHOLD = 0.1
HNR_PERIODS_PER_WINDOW = 1.0

# ---------------------------------------------------------------------------
# MFCC settings (librosa)
# ---------------------------------------------------------------------------

N_MFCC = 13
MFCC_N_FFT = 2048
MFCC_HOP_LENGTH = 512

# ---------------------------------------------------------------------------
# Segmentation (accuracy-improvement phase)
# ---------------------------------------------------------------------------

# Recordings are split into fixed-length chunks; each chunk is classified
# and chunk scores are averaged per recording.  10 s is long enough for
# stable perturbation statistics but yields ~14 chunks per recording.
SEGMENT_SECONDS = 10.0
# Trailing chunks shorter than this are dropped.
SEGMENT_MIN_SECONDS = 5.0

# CPPS (smoothed cepstral peak prominence) - Praat standard settings.
CPPS_PITCH_FLOOR_HZ = 60.0
CPPS_TIME_STEP = 0.002
CPPS_MAX_FREQUENCY_HZ = 5000.0
CPPS_PREEMPHASIS_FROM_HZ = 50.0

# Pause statistics: a gap between speech stretches counts as a pause when
# it is at least this long (seconds); speech stretches found at this
# threshold below the peak (librosa.effects.split).
PAUSE_MIN_S = 0.2
PAUSE_TOP_DB = 25

# ---------------------------------------------------------------------------
# Modeling
# ---------------------------------------------------------------------------

# Which feature set the trained model uses: "base" (Phase 3/4, 43
# features) or "extended" (base + CPPS + pause statistics + delta-MFCC).
# Decided by the accuracy-improvement experiments (see
# reports/experiments_report.md); pipeline_config.json pins it per model.
FEATURE_SET = "extended"

# How a recording becomes ONE feature vector: recordings are split into
# SEGMENT_SECONDS chunks, features are extracted per chunk, and the
# per-feature MEAN over chunks is the recording's vector.  Training and
# prediction must both use this rule (enforced via pipeline_config.json).
AGGREGATION = "chunk_feature_mean"

# Class labels.  0 = healthy control, 1 = Parkinson's disease group.
LABEL_HC = 0
LABEL_PD = 1
LABEL_NAMES = {LABEL_HC: "HC", LABEL_PD: "PD"}

# Number of folds for GroupKFold cross-validation.  Must not exceed the
# number of subjects in the smaller class; the training script checks this.
N_SPLITS = 5

RANDOM_STATE = 42

# Saved artifact filenames.
MODEL_FILE = MODELS_DIR / "model.joblib"
SCALER_FILE = MODELS_DIR / "scaler.joblib"
PIPELINE_CONFIG_FILE = MODELS_DIR / "pipeline_config.json"

# ---------------------------------------------------------------------------
# Prototype result interpretation
# ---------------------------------------------------------------------------

# Model scores inside this band are reported as "inconclusive" instead of
# a hard HC/PD call.  With subject-level balanced accuracy ~0.82, scores
# near 0.5 carry little evidence either way; showing them as a class
# label would overstate what the model knows (this matters most for
# out-of-domain recordings, which often land near the boundary).
UNCERTAIN_LOW = 0.35
UNCERTAIN_HIGH = 0.65

# Recording-condition heuristics (warnings only, never blocking).
CLIPPING_WARN_FRACTION = 0.001   # >0.1% of samples at full scale
SNR_WARN_DB = 15.0               # rough energy-percentile SNR estimate

# ---------------------------------------------------------------------------
# Prototype wording (mandatory cautious language)
# ---------------------------------------------------------------------------

DISCLAIMER = (
    "This is a research screening-support prototype and is not a medical "
    "diagnostic tool. Its result must not replace evaluation by a "
    "qualified healthcare professional."
)

# Plain-language explanation of the two classes, shown in the prototype.
LABEL_EXPLANATION = (
    "HC means the recording's acoustic pattern is closer to the healthy "
    "control group of the research dataset. PD means it is closer to the "
    "group of participants with Parkinson's disease. This describes "
    "similarity of voice measurements only - it does not establish whether "
    "a person does or does not have any medical condition."
)
