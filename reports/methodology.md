# Methodology

This document explains how the system works and why each design decision
was made. It is written to be reused in the final project report.

## 1. Problem statement

Parkinson's disease affects the muscles used for speaking, which changes
measurable properties of the voice: less stable pitch, more cycle-to-cycle
variation in frequency (jitter) and amplitude (shimmer), more breathiness
(lower harmonics-to-noise ratio and cepstral peak prominence), and altered
speech timing with more pauses. This project builds a research prototype
that measures these properties in a voice recording and uses classical
machine learning to indicate whether the acoustic pattern is closer to the
healthy-control (HC) or Parkinson's (PD) group of a research dataset. It
is a screening-support demonstration, not a diagnostic system.

## 2. Dataset

MDVR-KCL (Mobile Device Voice Recordings at King's College London): 73
usable recordings from 37 subjects (21 HC, 16 PD), recorded on one phone
in a controlled setting. Each subject performed up to two tasks: reading a
fixed text and a spontaneous dialogue. Recordings are 44.1 kHz WAV, mostly
1.5-3.5 minutes. Labels (HC/PD) come from the folder structure and are
cross-checked against the filename tags; subject IDs come from the ID##
filename prefix. Every file passed integrity checks (readable, non-silent,
consistent label, extractable subject ID).

Class balance: 42 HC vs 31 PD recordings (some subjects have one task
only). No per-subject sex or age metadata ships with the audio, which
limits demographic confound analysis (see Limitations).

## 3. Preprocessing

Every recording (training and prediction alike) passes the same chain:

1. Convert to mono.
2. Resample to 44100 Hz (the dataset's native rate).
3. Remove DC offset (subtract the mean).
4. Trim leading/trailing silence (30 dB below peak).
5. Peak-normalize to 0.95.

Deliberately NO noise reduction or filtering: jitter, shimmer, HNR and
CPPS measure tiny waveform irregularities, and denoising algorithms
distort exactly those irregularities.

## 4. Segmentation

Each preprocessed recording is split into consecutive 10-second chunks
(trailing chunk kept if >= 5 s). 10 s is long enough for stable
perturbation statistics yet yields ~14 chunks per recording (1001 chunks
total), which stabilizes the recording-level summary.

## 5. Features (74 per chunk)

| family | features | tool |
|:--|:--|:--|
| F0 statistics | mean, median, std, min, max, range, voiced fraction (7) | Praat pitch tracking (75-500 Hz) |
| Jitter | local, local-absolute, RAP, PPQ5 (4) | Praat point process |
| Shimmer | local, local-dB, APQ3, APQ5, APQ11 (5) | Praat point process |
| Noise | mean HNR (1) | Praat harmonicity |
| Cepstral | CPPS (1) | Praat power cepstrogram |
| Timing | pauses/min, mean pause, pause ratio, mean speech-segment length (4) | energy-based segmentation |
| Spectral | MFCC 0-12 mean+std (26) | librosa |
| Spectral dynamics | delta-MFCC 0-12 mean+std (26) | librosa |

The recording's final feature vector is the per-feature MEAN over its
chunks. Praat-based measures that cannot be computed on a chunk (too little
voicing) yield NaN and are median-imputed inside each training fold.

## 6. Models

All candidates are scikit-learn pipelines: median imputer -> standard
scaler -> classifier. Because imputation and scaling live inside the
pipeline, they are re-fit on the training part of every fold - never on
the full dataset (no preprocessing leakage). Candidates: logistic
regression, SVM-RBF, random forest, MLP (dropped after a robustness check),
plus a majority-class baseline.

**Final model: Random Forest** (300 trees, balanced class weights,
default depth), selected by pre-declared experiments (below).

## 7. Validation protocol

- **Subject-independent**: StratifiedGroupKFold with subject ID as the
  group - recordings of the same person are never split between training
  and test. A runtime assertion re-checks every fold.
- 5 folds x 3 random seeds; all metrics reported as mean +/- std.
- Metrics: balanced accuracy (primary; robust to the 42:31 class
  imbalance), sensitivity, specificity, F1, ROC-AUC, confusion matrices,
  at recording level and subject level (subject score = mean of the
  subject's recording scores).
- Why grouping matters: with random 10-s-chunk splits the same pipeline
  scores 0.909 balanced accuracy - +0.13 of pure memorization of
  recording identity (see figures/validation_comparison.png).

## 8. Model selection (overfitting guards)

19 configurations were evaluated under the identical protocol: 4 data
representations (recording-level base features, recording-level extended,
chunk-level base, chunk-level extended) x 3 models, then nested
hyperparameter tuning and a soft-voting ensemble on the best
representation, plus a mean+std feature-summary variant. Rules fixed
BEFORE running: primary metric = subject-level balanced accuracy; a more
complex variant must beat the simpler one by > 0.02 to be adopted; any
result >= 0.95 triggers a leakage investigation. Result: extended features
with chunk-mean aggregation + default random forest won; tuning (0.814),
the ensemble (0.840) and mean+std summaries (0.824) did not clear the
margin over 0.822 and were rejected as within-noise complexity.

## 9. Final performance (subject-independent)

| level | balanced accuracy | sensitivity | specificity | ROC-AUC |
|:--|--:|--:|--:|--:|
| recording | 0.806 +/- 0.013 | - | - | 0.86 |
| subject | 0.822 +/- 0.032 | 0.771 | 0.873 | 0.864 |

Majority-class baseline: 0.5 balanced accuracy, 0 sensitivity.

## 10. Prototype behavior

The Streamlit app and CLI reuse the exact pipeline above (enforced by a
saved pipeline-configuration file checked before every prediction).
Safeguards: input validation with plain-language messages; scores in
0.35-0.65 reported as inconclusive rather than a class call; warnings for
short recordings, sample-rate mismatch, clipping, and low SNR; microphone
mode is explicitly framed as an out-of-domain demonstration; mandatory
non-diagnostic disclaimer before and after every result.

## 11. Limitations

1. 37 subjects from one recording setup and one language; fold-to-fold
   spread (+/- 0.03) reflects the small sample, and generalization to
   other microphones/languages is unmeasured (no external test set yet).
2. No sex/age metadata: demographic confounding cannot be fully excluded.
   An ablation without absolute-F0 features (the most sex-correlated)
   changed subject balanced accuracy by < 0.02, bounding the risk.
3. Jitter/shimmer/HNR are defined on sustained phonation; on continuous
   speech they are noisier proxies.
4. Scores are model properties, not calibrated medical probabilities.
