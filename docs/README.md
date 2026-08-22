# Project documentation

Complete, self-contained documentation of the graduation project
**"Voice Signal Analysis Using Machine Learning for Early Detection of
Parkinson's Disease"**.

These documents are written so that a reader (or an AI assistant) who has
never seen this project before can understand every decision, every
number, and every file, without needing any outside context.

> **Nature of the system:** a non-diagnostic research screening-support
> prototype. It never diagnoses Parkinson's disease.

## Reading order

| # | Document | What it covers |
|---|---|---|
| 1 | [01_overview_and_journey.md](01_overview_and_journey.md) | What the project is, its fixed rules, and the full chronological story of what was built and why |
| 2 | [02_scientific_background.md](02_scientific_background.md) | How voice is produced, what Parkinson's does to it, and why each acoustic measurement matters |
| 3 | [03_dataset.md](03_dataset.md) | The MDVR-KCL dataset: structure, labels, subjects, exact counts, inspection findings |
| 4 | [04_pipeline.md](04_pipeline.md) | Preprocessing, segmentation, and all 74 features defined one by one |
| 5 | [05_validation_and_metrics.md](05_validation_and_metrics.md) | Data leakage, subject-independent validation, and every metric explained |
| 6 | [06_experiments_and_results.md](06_experiments_and_results.md) | All model results, the 19-configuration study, and the final model |
| 7 | [07_prototype.md](07_prototype.md) | The app and command line, safety rules, uncertainty handling, tests |
| 8 | [08_external_validation.md](08_external_validation.md) | The Italian dataset test: design, the confound we caught, results |
| 9 | [09_limitations_and_ethics.md](09_limitations_and_ethics.md) | Honest limitations and the mandatory non-diagnostic wording |
| 10 | [10_repository_and_reproduction.md](10_repository_and_reproduction.md) | Every folder and script, and how to reproduce everything |
| 11 | [11_glossary.md](11_glossary.md) | Plain-language definitions of every technical term used |
| 12 | [12_presentation_qa.md](12_presentation_qa.md) | Key messages for the defence and likely examiner questions with answers |

## The project in one paragraph

Voice recordings from 37 people (21 healthy, 16 with Parkinson's disease)
were analysed. Each recording was cleaned, split into 10-second chunks,
and converted into 74 numerical acoustic measurements per chunk (pitch
statistics, jitter, shimmer, harmonics-to-noise ratio, cepstral peak
prominence, pause timing, and spectral shape features), which were then
averaged per recording. A Random Forest classifier was trained on these
measurements and validated so that no person ever appeared in both
training and testing. It reaches **0.822 balanced accuracy per subject**
on this dataset, and **0.701 ROC-AUC on a completely independent Italian
dataset** with no adaptation at all. A browser app and a command-line tool
let a user analyse a single recording, and the system deliberately answers
"inconclusive" when the evidence is weak.

## The headline numbers

| Quantity | Value |
|---|---|
| Subjects / recordings (training dataset) | 37 / 73 |
| Features per chunk | 74 |
| Chunks extracted | 1001 |
| Model configurations evaluated | 19 |
| Balanced accuracy, per subject (internal) | 0.822 ± 0.032 |
| ROC-AUC, per subject (internal) | 0.864 |
| Balanced accuracy, per subject (external, Italian) | 0.629 |
| ROC-AUC, per subject (external, Italian) | 0.701 |
| Same pipeline with a deliberately leaky split | 0.909 (inflated, not a result) |

## A note on honesty

Several numbers in this project are *lower* than what published papers
often claim for the same dataset. This is intentional and is the main
scientific contribution: the validation is subject-independent, the
external test is unadapted, and no result was tuned after seeing the test
data. Document 05 explains exactly why higher published numbers are
usually wrong.
