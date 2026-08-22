# 4. The processing pipeline

This document describes exactly what happens to an audio file, from the
raw WAV to a row of numbers ready for machine learning.

**The golden rule of this project:** this identical pipeline is used for
training, for evaluation, and for predicting on a brand-new file. That is
enforced technically — see section 4.6.

## 4.1 From sound to numbers (background)

Sound is a pressure wave. A microphone converts it into a fluctuating
voltage, and an analogue-to-digital converter measures that voltage many
thousands of times per second. Each measurement is a **sample**.

- **Sample rate** = samples per second. Our files are 44100 Hz, meaning
  44,100 measurements per second of audio. A rule of physics (the Nyquist
  theorem) says a sample rate of 44100 Hz can faithfully represent
  frequencies up to 22050 Hz, which covers all of human hearing.
- **Amplitude** = the value of each sample, representing instantaneous
  loudness.
- **Channels** = independent recordings (1 = mono, 2 = stereo).

So a 2-minute mono recording at 44100 Hz is simply a list of about
5.3 million numbers.

## 4.2 Step 1 — Preprocessing (`src/pvoice/preprocess.py`)

Applied to every recording in a fixed order:

| Step | What it does | Why |
|---|---|---|
| 1. Convert to mono | Averages channels into one | The pipeline expects a single signal; all our files are already mono |
| 2. Resample to 44100 Hz | Standardises the sample rate | Features like jitter depend on timing resolution; mixing rates would make recordings incomparable |
| 3. Remove DC offset | Subtracts the signal's mean value | A constant electrical shift biases amplitude-based measures like shimmer |
| 4. Trim edge silence | Removes leading/trailing silence 30 dB below peak | Silence at the start/end carries no voice information and distorts pause statistics |
| 5. Peak-normalise to 0.95 | Scales so the loudest sample is 0.95 | Makes recordings comparable regardless of recording volume or microphone gain |

**What we deliberately do NOT do: noise reduction.**

This is a key scientific decision. Denoising algorithms work by
identifying "irregular" parts of the signal and smoothing them away. But
jitter, shimmer, HNR, and CPPS are precisely *measurements of
irregularity*. Denoising would erase the very evidence we are trying to
measure, and would make a Parkinson's voice look artificially healthy.
Only the five safe, reversible operations above are applied.

Note that peak normalisation is safe for shimmer because shimmer is a
*relative* measure — multiplying the whole signal by a constant does not
change the ratio between neighbouring cycles.

## 4.3 Step 2 — Segmentation into chunks

After preprocessing, each recording is cut into consecutive
**10-second chunks**. A trailing chunk shorter than 5 seconds is discarded;
a recording shorter than 5 seconds becomes a single chunk.

Why chunking helps:

1. **More stable measurements.** Each chunk gets its own set of
   measurements, and averaging many chunks smooths out random fluctuation
   better than one measurement over the whole recording.
2. **More training material.** 73 recordings became **1001 chunks**
   (between 7 and 22 chunks per recording), which the experiments could
   exploit.
3. **It respects subject grouping.** Chunks inherit their recording's
   subject ID, so grouped validation still works — and, as the experiments
   showed, forgetting that would be catastrophic (see
   [05_validation_and_metrics.md](05_validation_and_metrics.md)).

## 4.4 Step 3 — Feature extraction (`src/pvoice/features.py`)

For each chunk, 74 numbers are computed. (The scientific meaning of each
family is explained in [02_scientific_background.md](02_scientific_background.md);
this is the exact inventory.)

### The 43 "base" features (used in Phases 3–4)

**F0 statistics (7)** — via Praat pitch tracking, search range 75–500 Hz:
`f0_mean_hz`, `f0_median_hz`, `f0_std_hz`, `f0_min_hz`, `f0_max_hz`,
`f0_range_hz`, `voiced_fraction`

**Jitter (4):** `jitter_local`, `jitter_local_abs`, `jitter_rap`,
`jitter_ppq5`

**Shimmer (5):** `shimmer_local`, `shimmer_local_db`, `shimmer_apq3`,
`shimmer_apq5`, `shimmer_apq11`

**Noise (1):** `hnr_mean_db`

**MFCC (26):** `mfcc0_mean`, `mfcc0_std`, … `mfcc12_mean`, `mfcc12_std`
(13 coefficients × mean and standard deviation)

### The 31 additional "extended" features (added in the improvement phase)

**Cepstral (1):** `cpps_db`

**Pause and timing (4):** `pause_count_per_min`, `pause_mean_s`,
`pause_ratio`, `speech_seg_mean_s`

**Delta-MFCC (26):** `mfccD0_mean`, `mfccD0_std`, … `mfccD12_mean`,
`mfccD12_std`

**Total: 74 features per chunk.** The final model uses all 74.

### Key parameter settings (all in `src/pvoice/config.py`)

| Setting | Value | Note |
|---|---|---|
| Sample rate | 44100 Hz | dataset's native rate |
| Silence-trim threshold | 30 dB below peak | |
| Pitch search range | 75–500 Hz | covers adult male and female voices |
| MFCC coefficients | 13 | standard choice |
| MFCC window / hop | 2048 / 512 samples | ≈46 ms window, ≈12 ms step |
| Chunk length / minimum | 10 s / 5 s | |
| CPPS pitch floor | 60 Hz | Praat standard |
| Pause threshold | ≥ 0.2 s gap, 25 dB below peak | |

## 4.5 Step 4 — One vector per recording

Each recording's final feature vector is the **average of its chunks'
feature vectors**, feature by feature. So a recording with 14 chunks
produces 14 sets of 74 numbers, which are averaged into a single set of
74 numbers.

This aggregation rule is called `chunk_feature_mean` in the configuration,
and prediction on a new file follows exactly the same rule.

## 4.6 How "same pipeline everywhere" is enforced

When a model is trained, a file `models/pipeline_config.json` is written
alongside it, recording every pipeline setting: sample rate, trim
threshold, pitch range, MFCC parameters, feature set, aggregation rule,
chunk length, CPPS and pause settings, and the **complete ordered list of
feature names**.

Before *every* prediction, the software compares that file against the
current code's settings. If anything differs — even the order of one
feature — the prediction is refused with a message telling the user to
retrain. A missing or unreadable configuration file is likewise treated as
incompatible.

This makes the "same pipeline" rule a mechanical guarantee rather than a
promise.

## 4.7 Quality validation of the feature table

The generated table was checked automatically
(`scripts/validate_features.py`, report in `reports/feature_report.md`):

| Check | Result |
|---|---|
| Missing values (NaN) | 0 in the recording-level table |
| Infinite values | 0 |
| Values outside physically plausible ranges | 0 |
| Constant / zero-variance features | 0 |
| Duplicate feature vectors | 0 |

One point needed interpretation: Praat's pitch tracker occasionally
reports a minimum F0 slightly *below* the 75 Hz search floor (e.g.
74.95 Hz), because it interpolates between analysis frames. This is normal
behaviour, not an error, so the validator allows a 2% tolerance.

In the chunk-level table, a small number of chunks (2 to 16 out of 1001,
depending on the feature) have missing perturbation values because those
chunks contain too little steady voicing for Praat to measure. These are
left as missing and filled in later by the median imputer *inside each
training fold* — never by looking at the test data.

## 4.8 Relevant files

| File | Purpose |
|---|---|
| `src/pvoice/preprocess.py` | Preprocessing chain and chunk splitting |
| `src/pvoice/features.py` | All 74 feature computations |
| `src/pvoice/config.py` | Every parameter listed above |
| `scripts/build_features.py` | Builds the 43-feature recording-level table |
| `scripts/build_segment_features.py` | Builds the 74-feature chunk-level table |
| `scripts/validate_features.py` | Quality validation and report |
| `data/processed/features.csv` | 73 rows × 43 features |
| `data/processed/segment_features.csv` | 1001 rows × 74 features |
