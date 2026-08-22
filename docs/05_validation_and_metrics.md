# 5. Validation and metrics

This is the scientific heart of the project. A model's reported score is
only meaningful if the way it was tested was fair. This document explains
what "fair" means here, how unfairness (leakage) inflates results, and how
every metric is defined.

## 5.1 What "training" and "testing" mean

A machine learning model learns patterns from **training data** (examples
whose answers it is shown). To find out whether it learned something
general — rather than memorising — it must be tested on **test data** it
has never seen.

An analogy: if a teacher gives students the exam questions *and* answers
beforehand, a perfect score proves nothing. Testing a model on data it
trained on is exactly that.

## 5.2 Cross-validation

With only 37 subjects, setting aside a single fixed test set would waste
data and give a result that depends heavily on which people happened to be
chosen. **K-fold cross-validation** solves this:

1. Split the data into 5 parts ("folds").
2. Train on 4 parts, test on the 5th.
3. Repeat 5 times so every part serves as the test set exactly once.
4. Every data point ends up with a prediction made by a model that never
   saw it. These are called **out-of-fold predictions**.

We additionally repeat the entire procedure with **3 different random
seeds** (42, 7, 2025), which produce three different ways of dividing
people into folds. Reporting the average and spread across seeds shows how
much the result depends on luck.

## 5.3 The critical part: grouping by subject

Each person in our dataset contributed **two recordings**. If those two
recordings were split — one into training, one into testing — the model
could recognise the *person* (their individual voice timbre, their
microphone, their room) rather than the *disease*. It would then score
brilliantly on this dataset and fail completely on anyone new.

This is called **data leakage**.

The fix is **grouped cross-validation**: the subject ID is declared as the
"group", and the splitter guarantees all recordings of one person stay
together on the same side of every split. We use `StratifiedGroupKFold`,
which does this *and* keeps the healthy/Parkinson's ratio similar across
folds.

**Belt and braces:** the code does not merely trust the library. In every
fold, it computes the intersection of training subjects and test subjects
and raises a `RuntimeError` that stops the entire program if that
intersection is not empty. This assertion has never triggered.

```python
overlap = set(groups.iloc[train_idx]) & set(groups.iloc[test_idx])
if overlap:
    raise RuntimeError(f"LEAKAGE: subjects {overlap} appear in train AND test")
```

## 5.4 Proof that this matters — measured, not asserted

We ran the *identical* pipeline and *identical* model twice, changing only
how the data was split:

| Split method | Balanced accuracy (per recording) |
|---|---|
| Correct: grouped by subject | **0.775** |
| Wrong: random 10-second chunks | **0.909** |

The wrong method inflates the score by **+0.13**. That gap is not
detection ability — it is the model recognising that a chunk from a
recording it partly memorised belongs to the same speaker.

This is the single most important figure in the project
(`reports/figures/validation_comparison.png`) and the reason many
published papers report 95–99% on this kind of data: they split at the
recording or window level, not by person.

An interesting detail we verified honestly: splitting randomly at the
*recording* level barely inflates our score (0.807 vs 0.806), because a
subject's two recordings are different tasks and thus not very similar.
The catastrophic leakage is specifically at the *chunk* level. We report
this precise version rather than the more dramatic but less accurate
claim.

## 5.5 A second protection: preprocessing inside the fold

Two data-preparation steps must learn from data:

- **Imputation** — filling missing values with the median.
- **Scaling** — rescaling features to comparable ranges (necessary because
  pitch is measured in hundreds of Hz while jitter is a fraction near
  0.02; without scaling, distance-based models would be dominated by the
  large numbers).

If the median or the scaling range were computed over the *whole* dataset,
information from the test data would leak into training — subtly, but
really.

Therefore both steps are placed **inside** the scikit-learn `Pipeline`
object, which guarantees they are re-fitted on the training portion of
each fold only:

```
Pipeline: [median imputer] → [standard scaler] → [classifier]
```

No feature selection was performed on the full dataset either.

## 5.6 Two levels of results

- **Recording level** — one prediction per audio file.
- **Subject level** — the person's recordings are combined by averaging
  their scores, then thresholded at 0.5. One prediction per person.

Subject level is the more meaningful number, because in real use you care
whether the system judges a *person* correctly. Both are always reported.

## 5.7 Every metric, defined

Assume the model examines healthy people (HC) and Parkinson's patients
(PD). Four outcomes are possible, forming the **confusion matrix**:

|  | Predicted HC | Predicted PD |
|---|---|---|
| **Actually HC** | True Negative (TN) — correctly cleared | False Positive (FP) — wrongly flagged |
| **Actually PD** | False Negative (FN) — missed | True Positive (TP) — correctly caught |

### Accuracy
`(TP + TN) / everything` — the fraction of all decisions that were right.

**Why we don't rely on it:** our data has 42 HC and 31 PD recordings. A
useless model that always answers "healthy" scores 42/73 = **0.575
accuracy** while catching zero patients. Accuracy hides this failure.

### Balanced accuracy — our primary metric
The average of the two class-specific rates:
`(sensitivity + specificity) / 2`.

The always-healthy model now scores exactly **0.500**, correctly exposing
it as worthless. This is why balanced accuracy is our headline metric.

### Sensitivity (recall for PD)
`TP / (TP + FN)` — of all people who really have Parkinson's, what
fraction did we catch? Our final model: **0.771**, so about 3 in 4.
Missing patients is the more costly error in screening.

### Specificity (recall for HC)
`TN / (TN + FP)` — of all healthy people, what fraction did we correctly
clear? Our final model: **0.873**, so about 1 in 8 healthy people is
wrongly flagged.

### Precision
`TP / (TP + FP)` — when the model says "PD", how often is it right?

### F1 score
The harmonic mean of precision and sensitivity — a single number
balancing "catching patients" against "not crying wolf".

### ROC-AUC
The model outputs a **score** between 0 and 1, not just a label. Different
thresholds trade sensitivity against specificity. The ROC curve plots that
trade-off across all thresholds, and **AUC** is the area under it.

The most intuitive definition: **pick one random Parkinson's patient and
one random healthy person; AUC is the probability that the model gives the
patient the higher score.**

- 0.5 = useless (coin flip)
- 0.7 = useful discrimination
- 1.0 = perfect

Our final model: **0.864 internally**, **0.701 on the foreign dataset**.
AUC is especially valuable across datasets, because it measures ranking
ability independently of where the 0.5 threshold happens to fall.

## 5.8 Why we always report variation

With 37 subjects, each fold's test set holds only 7–8 people. One person
classified differently swings the score by several points. So every result
is written as **mean ± standard deviation** across folds and seeds — for
example **0.822 ± 0.032** — and single-fold values are shown too. Quoting
one number without its spread would be dishonest at this sample size.

## 5.9 The suspicious-result rule

Written into the code before any results existed: if any properly
subject-independent result reaches **0.95 or above** on accuracy, balanced
accuracy, or ROC-AUC, the training script prints a warning and the
configuration must be investigated for leakage, duplicates, or a
confounder before anyone is allowed to call it a success.

No configuration ever triggered it under correct validation. The only
number that came close (0.909) was the deliberately leaky demonstration.

## 5.10 Relevant files

| File | Purpose |
|---|---|
| `src/pvoice/evaluate.py` | Grouped cross-validation, the leakage assertion, all metric computations |
| `scripts/train_models.py` | Phase 4 evaluation of all models |
| `scripts/make_figures.py` | Generates the honest-vs-leaky comparison figure |
| `reports/metrics_report.md` | Full Phase 4 results |
| `data/processed/oof_predictions.csv` | Out-of-fold predictions with subject IDs |
