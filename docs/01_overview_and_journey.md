# 1. Project overview and the full journey

## 1.1 What the project is

A biomedical engineering graduation project that answers one question:

> Can we measure a person's voice recording and tell whether its acoustic
> pattern resembles the voices of people with Parkinson's disease, or the
> voices of healthy people — using only classical, explainable machine
> learning?

The deliverable is a **research screening-support prototype**: software
that a person can point at a WAV file and receive a cautious, clearly
non-medical indication, plus the complete scientific evidence of how well
it works and where it fails.

## 1.2 Fixed rules the project had to obey

These were decided at the start and never violated:

1. Dataset: **MDVR-KCL** (raw audio only).
2. **No pre-extracted feature datasets.** Feature extraction is a core
   contribution and had to be implemented in this project.
3. Python only, inside a project virtual environment (`.venv`), no global
   package installs.
4. **Subject-independent validation is mandatory** — recordings from one
   person may never appear in both training and testing.
5. The *same* preprocessing and feature-extraction code must be used for
   training, evaluation, and new-file prediction.
6. Classical, explainable machine learning first — not deep learning.
7. The output is **non-diagnostic**. Wording like "diagnoses Parkinson's"
   is forbidden.
8. If any result reaches 95% or higher, stop and investigate for leakage
   instead of celebrating.

## 1.3 The journey, phase by phase

### Phase 1 — Project foundation

Built the folder structure, the virtual environment, the dependency list,
and the skeleton of every module (configuration, dataset reading,
preprocessing, features, models, evaluation, prediction). Verified the
whole toolchain worked on Python 3.14 by running the pipeline on a
synthetic test tone before any real data existed.

**Key decision:** all settings (sample rate, pitch range, MFCC parameters,
paths) live in one file, `src/pvoice/config.py`, so training and
prediction can never silently drift apart.

### Phase 2 — Dataset inspection

Before any modelling, the dataset was inspected and a report generated:
folder structure, file count, formats, sample rates, durations, labels,
subject identities, duplicates, and corrupt files.

**Result:** 73 usable recordings from 37 subjects, no corrupt files, no
duplicates, no label conflicts, and every file traceable to a subject —
so grouped validation was confirmed possible. Details in
[03_dataset.md](03_dataset.md).

### Phase 3 — Preprocessing and feature extraction

Implemented the audio conditioning chain and the acoustic feature
extraction, producing one feature vector per recording, then validated
that table for missing values, impossible values, constant features, and
duplicates.

**Result:** 73 rows × 43 features, zero missing values, zero infinities,
validation passed. Details in [04_pipeline.md](04_pipeline.md).

### Phase 4 — Modelling and honest evaluation

Trained a majority-class baseline plus four models (logistic regression,
SVM, random forest, MLP), each inside a scikit-learn pipeline, evaluated
with `StratifiedGroupKFold` grouped by subject, and reported per-fold,
pooled, and per-subject metrics with confusion matrices.

**Result:** SVM-RBF selected, **0.780 balanced accuracy per subject**. A
confounder check (removing absolute-pitch features, which correlate with
speaker sex) showed the SVM did not depend on them, while the MLP
collapsed — so the MLP was dropped from later work.

### Phase 5 — The prototype

Built the Streamlit browser app and the command-line tool, both calling
one shared prediction function; added input validation with
plain-language error messages, a configuration-compatibility check that
refuses to predict if the pipeline changed since training, and the
mandatory non-diagnostic wording. Wrote automated tests for successful
prediction, configuration mismatch, and every category of invalid audio.

### Accuracy-improvement phase (requested by the supervisor)

The supervisor judged 0.78 too low for a public presentation, so a
structured improvement study was run — with the anti-overfitting rules
declared **before** any experiment:

- 5-fold subject-grouped cross-validation, repeated with 3 random seeds.
- Primary metric: balanced accuracy per subject.
- **A more complex variant must beat the simpler one by more than 0.02**,
  otherwise the simpler one wins.
- Anything ≥ 0.95 triggers a leakage investigation.

Nineteen configurations were evaluated: four data representations
(whole-recording vs 10-second chunks × 43 vs 74 features) × three models,
plus nested hyperparameter tuning, a soft-voting ensemble, and a
mean+standard-deviation summary variant.

**Result:** the winner was chunk-averaged 74 features with a
default-settings Random Forest, at **0.822 balanced accuracy per
subject**. The ensemble scored higher (0.840) but was **rejected** because
it beat the winner by only 0.018 — less than the pre-declared margin.
Details in [06_experiments_and_results.md](06_experiments_and_results.md).

### Honesty and demonstration additions

Triggered by a real observation: the supervisor recorded himself and a
friend (both healthy) and both scored ~0.65 toward Parkinson's. That
exposed a genuine weakness — the model had never been tested outside its
own recording conditions, and it presented borderline scores as confident
class labels. Three changes followed:

1. **An "inconclusive" band**: scores between 0.35 and 0.65 are no longer
   reported as a class at all.
2. **Recording-condition warnings**: sample-rate mismatch, clipping, low
   signal-to-noise ratio, and very short recordings.
3. **Microphone mode** in the app, explicitly labelled as an
   out-of-domain demonstration.

Presentation figures were also generated, including the key comparison
showing that the same pipeline reports 0.909 under a deliberately leaky
split versus 0.775 under the correct one.

### External validation

The strongest scientific step. The Italian Parkinson's Voice and Speech
dataset (831 recordings, 61 speakers) was downloaded and the **frozen**
model — no retraining, no threshold tuning — was tested on it.

A serious trap was caught during inspection: every 44.1 kHz file in that
dataset belongs to the Parkinson's group, so without correction the model
could have "detected Parkinson's" by detecting microphone bandwidth. All
audio was therefore bandwidth-harmonised to 16 kHz first.

**Result:** 0.629 balanced accuracy and 0.701 ROC-AUC on elderly healthy
versus Parkinson's speakers. Details in
[08_external_validation.md](08_external_validation.md).

## 1.4 What makes this project unusual

1. **Subject-independent validation, enforced in code.** A runtime
   assertion aborts the program if any subject ever appears on both sides
   of a split.
2. **A measured generalisation result**, not an assumed one — very few
   undergraduate projects test on a second, foreign dataset.
3. **Pre-declared model-selection rules**, including publicly reporting
   the configuration that scored highest and explaining why it was
   rejected.
4. **A prototype that admits uncertainty** rather than always producing a
   confident label.
5. **Full reproducibility**: every number in every report is regenerated
   by a script in the repository.
