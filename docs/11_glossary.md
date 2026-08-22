# 11. Glossary

Plain-language definitions of every technical term used in this project.

## Audio and signal processing

**Sample** — one measurement of sound pressure at one instant.

**Sample rate** — how many samples are recorded per second. Ours is
44100 Hz. A higher rate captures higher frequencies.

**Mono / stereo** — one channel of audio versus two.

**Amplitude** — the value of a sample; corresponds to loudness.

**WAV** — an uncompressed audio file format; stores samples directly with
no quality loss.

**DC offset** — a constant electrical shift added to the whole signal by
imperfect hardware. Removed by subtracting the signal's mean.

**Normalisation** — rescaling the signal so its loudest point has a fixed
value, making recordings comparable regardless of recording volume.

**Trimming** — removing silence from the beginning and end of a recording.

**Clipping** — distortion that occurs when the sound is too loud for the
recording range, so peaks are cut flat.

**SNR (signal-to-noise ratio)** — how loud the speech is compared with the
background noise, in decibels. Higher is cleaner.

**Resampling** — converting audio from one sample rate to another.

**Bandwidth harmonisation** — deliberately reducing all recordings to the
same maximum frequency content so that none can be identified by its
recording quality.

**Spectrum** — the description of a sound in terms of how much energy it
contains at each frequency.

**Cepstrum** — the result of analysing the spectrum *of a spectrum*; useful
for detecting regular harmonic spacing.

## Voice measurements

**F0 (fundamental frequency)** — the rate of vocal-fold vibration; heard
as pitch. Measured in Hz.

**Voiced fraction** — the proportion of the recording in which vocal-fold
vibration was detected at all.

**Jitter** — cycle-to-cycle irregularity in the *timing* of vocal-fold
vibrations.

**Shimmer** — cycle-to-cycle irregularity in the *amplitude* of vocal-fold
vibrations.

**HNR (harmonics-to-noise ratio)** — how much of the voice is ordered tone
versus turbulent noise, in decibels. Lower means breathier.

**CPPS (smoothed cepstral peak prominence)** — how strongly the voice's
harmonic structure stands out above the background in the cepstrum. A
robust measure of overall voice quality that works on continuous speech.

**MFCC (Mel-frequency cepstral coefficients)** — a compact numerical
description of the shape of the spectrum, on a frequency scale matched to
human hearing. Captures the filtering effect of the vocal tract.

**Delta-MFCC** — how fast each MFCC changes from moment to moment;
captures the dynamics of articulation.

**Dysarthria** — a speech disorder caused by weakened or poorly controlled
speech muscles. Parkinson's produces the *hypokinetic* form.

**Dysphonia** — disordered voice quality (hoarseness, breathiness).

**Praat / Parselmouth** — Praat is the standard software for scientific
speech analysis; Parselmouth is the Python interface to it. Used here for
F0, jitter, shimmer, HNR, and CPPS.

**librosa** — a Python audio-analysis library. Used here for MFCC,
resampling, and silence detection.

## Machine learning

**Feature** — one measured number describing a recording (for example
`jitter_local`). We use 74.

**Feature vector** — the full list of features for one recording.

**Label / class** — the correct answer for an example: HC (healthy
control) or PD (Parkinson's disease).

**Training** — the process of showing a model labelled examples so it can
learn patterns.

**Testing** — measuring performance on examples the model has never seen.

**Classifier / model** — the algorithm that maps a feature vector to a
class.

**Logistic Regression** — a simple model that separates classes with a
straight boundary.

**SVM (Support Vector Machine)** — a model that finds the boundary with
the widest margin between classes. The **RBF kernel** allows that boundary
to curve.

**Random Forest** — many decision trees trained on random subsets, voting
together. Our final model.

**MLP (multilayer perceptron)** — a small neural network.

**Baseline** — a deliberately trivial model (here: always predict the
majority class) used to prove real models add value.

**Ensemble** — combining several models' predictions.

**Hyperparameter** — a setting chosen before training (e.g. number of
trees), as opposed to something learned from data.

**Tuning** — searching for good hyperparameter values.

**Pipeline** — a chain of processing steps (imputer → scaler →
classifier) treated as a single object, so all steps are fitted only on
training data.

**Imputation** — filling in missing values; we use the median of the
training data.

**Scaling (standardisation)** — rescaling features to comparable ranges so
that features with large numeric values do not dominate.

**Class weight ("balanced")** — making the rarer class count more during
training so the model is not biased toward the common class.

**Overfitting** — when a model learns the peculiarities of the training
data instead of general patterns, so it performs well in testing but badly
in reality.

**Data leakage** — when information from the test data reaches the model
during training, producing falsely high scores. The central danger this
project guards against.

**Cross-validation** — splitting data into K parts and rotating which part
is the test set, so every example gets a prediction from a model that
never saw it.

**GroupKFold / StratifiedGroupKFold** — cross-validation that keeps all
recordings of one person together in the same fold, and (stratified) also
keeps the class ratio balanced across folds.

**Out-of-fold prediction** — a prediction made for an example by a model
that was not trained on it.

**Seed** — a number controlling random choices; changing it produces a
different random split, which is why we repeat with 3 seeds.

**Ablation** — deliberately removing something (e.g. pitch features) to
measure how much the result depended on it.

**Confounder** — a hidden variable that correlates with the answer and
lets the model "cheat" (e.g. speaker sex, or recording bandwidth).

**Domain shift** — when new data differs systematically from training data
(different microphone, room, language), causing performance to drop.

## Metrics

**Confusion matrix** — a 2×2 table of correct and incorrect predictions
for each class.

**True positive / negative** — a patient correctly identified / a healthy
person correctly cleared.

**False positive** — a healthy person wrongly flagged ("false alarm").

**False negative** — a patient missed.

**Accuracy** — the fraction of all predictions that were correct.
Misleading with imbalanced classes.

**Balanced accuracy** — the average of sensitivity and specificity. Our
primary metric.

**Sensitivity (recall)** — the fraction of patients correctly caught.

**Specificity** — the fraction of healthy people correctly cleared.

**Precision** — of those flagged as patients, the fraction who really are.

**F1 score** — the harmonic mean of precision and sensitivity.

**ROC curve** — the trade-off between sensitivity and false alarms across
all possible decision thresholds.

**AUC (area under the ROC curve)** — the probability that a randomly
chosen patient receives a higher score than a randomly chosen healthy
person. 0.5 = useless, 1.0 = perfect.

**Threshold** — the score cut-off (0.5 here) above which a prediction is
called PD.

**Standard deviation** — a measure of spread; we report it to show how
much results vary between folds and seeds.

## Project-specific terms

**HC** — healthy control group.

**PD** — Parkinson's disease group.

**Subject / speaker ID** — the identifier grouping all recordings of one
person; the basis of honest validation.

**Chunk / segment** — a 10-second piece of a recording.

**Chunk-feature mean** — our aggregation rule: average each feature across
a recording's chunks.

**Base feature set** — the original 43 features.

**Extended feature set** — the final 74 features.

**Inconclusive band** — scores between 0.35 and 0.65, reported as "cannot
tell" rather than as a class.

**Pipeline configuration** (`pipeline_config.json`) — the saved record of
every setting used to train the model; checked before every prediction.

**Adoption margin** — the pre-declared rule that a more complex variant
must improve balanced accuracy by more than 0.02 to be adopted.

**Internal validation** — testing on unseen *people* from the same
dataset.

**External validation** — testing on a completely different dataset.
