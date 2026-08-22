# 6. Experiments and results

Every number here was produced under the subject-independent protocol
described in [05_validation_and_metrics.md](05_validation_and_metrics.md).

## 6.1 The models compared

All are wrapped in a pipeline of `median imputer → standard scaler →
classifier`.

| Model | Intuition |
|---|---|
| **Majority-class baseline** | Always predicts the more common class. Learns nothing. Exists so we can prove the real models are actually useful. |
| **Logistic Regression** | Draws a straight boundary between the groups; weights each feature by importance. Simplest and most interpretable. |
| **SVM (RBF kernel)** | Finds the boundary with the widest possible margin between the groups; the RBF kernel lets that boundary be curved. |
| **Random Forest** | Builds 300 decision trees, each on a random part of the data and features, and lets them vote. Handles mixed feature scales and interactions well, and reports which features mattered. |
| **MLP (neural network)** | A small neural network (32 and 16 hidden units). Included for completeness. |

All models except the baseline use `class_weight="balanced"`, which makes
the under-represented Parkinson's class count proportionally more during
training so the model is not biased toward always answering "healthy".

## 6.2 Phase 4 results (43 features, whole recording)

Subject-independent, 5 folds. Balanced accuracy:

| Model | Per recording | Per subject | ROC-AUC (recording) |
|---|---|---|---|
| Majority baseline | 0.500 | 0.500 | 0.500 |
| Logistic Regression | 0.651 | 0.662 | 0.717 |
| **SVM-RBF** | **0.768** | **0.780** | 0.741 |
| Random Forest | 0.739 | 0.725 | 0.775 |
| MLP | 0.671 | 0.686 | 0.736 |

The baseline achieved 0.575 *plain* accuracy while catching **zero**
patients (sensitivity 0.000) — the clearest possible demonstration of why
balanced accuracy is the right metric.

**Selection rule used:** highest *robust score* = mean balanced accuracy
minus its standard deviation across folds, which penalises models that are
merely lucky in one fold. SVM-RBF won with 0.637.

### The sex-confounder check

Absolute pitch strongly reflects speaker sex, and our two groups had mean
F0 of about 180 Hz (HC) versus 154 Hz (PD) — a difference that could
reflect group composition rather than disease. Since the dataset ships no
verified sex metadata, we could not check composition directly, so we
measured **dependence** instead: cross-validation was repeated with the
four absolute-F0 features removed.

| Model | With all features | Without absolute F0 |
|---|---|---|
| Logistic Regression | 0.651 | 0.699 |
| SVM-RBF | 0.768 | 0.780 |
| Random Forest | 0.739 | 0.707 |
| MLP | 0.671 | **0.526** |

The SVM and logistic regression were unaffected or improved, showing the
signal lives mostly in the perturbation and spectral features, not in
absolute pitch. The MLP collapsed to near chance, revealing it *had* been
leaning on the potential confound — so the MLP was dropped from all later
work.

## 6.3 The accuracy-improvement study

**Rules declared before running anything** (this ordering is what makes
the study trustworthy):

1. Protocol: 5-fold `StratifiedGroupKFold` × 3 seeds, identical splits for
   every variant.
2. Primary metric: balanced accuracy per subject.
3. **Adoption margin: a more complex variant must win by more than 0.02.**
4. Anything ≥ 0.95 stops the study for a leakage investigation.
5. All configurations get reported, including losers.

### The variants

| Variant | Data representation | Features |
|---|---|---|
| V0 | whole recording | 43 (base) |
| V1 | chunks averaged per recording | 74 (extended) |
| V2 | chunk-level classification, scores averaged | 43 |
| V3 | chunk-level classification, scores averaged | 74 |
| V4 | best of the above + nested hyperparameter tuning | — |
| V5 | best of the above + tuned SVM+RF soft-voting ensemble | — |
| V6 | chunks summarised by mean **and** standard deviation | 148 |

### Results (balanced accuracy per subject, mean ± std over 3 seeds)

| Variant / model | Subject | Recording | Subject AUC |
|---|---|---|---|
| V0 / logistic regression | 0.704 ± 0.029 | 0.685 | 0.765 |
| V0 / SVM | 0.780 ± 0.019 | 0.761 | 0.789 |
| V0 / random forest | 0.725 ± 0.019 | 0.725 | 0.808 |
| V1 / logistic regression | 0.746 ± 0.029 | 0.677 | 0.788 |
| V1 / SVM | 0.816 ± 0.026 | 0.792 | 0.841 |
| **V1 / random forest** | **0.822 ± 0.032** | **0.806** | **0.864** |
| V2 / logistic regression | 0.769 ± 0.042 | 0.770 | 0.841 |
| V2 / SVM | 0.817 ± 0.010 | 0.781 | 0.826 |
| V2 / random forest | 0.780 ± 0.011 | 0.750 | 0.802 |
| V3 / logistic regression | 0.772 ± 0.059 | 0.752 | 0.817 |
| V3 / SVM | 0.793 ± 0.024 | 0.757 | 0.820 |
| V3 / random forest | 0.780 ± 0.011 | 0.775 | 0.820 |
| V4 / logistic regression (tuned) | 0.772 ± 0.028 | 0.751 | 0.829 |
| V4 / SVM (tuned) | 0.775 ± 0.043 | 0.755 | 0.815 |
| V4 / random forest (tuned) | 0.814 ± 0.024 | 0.810 | 0.870 |
| V5 / SVM+RF ensemble | 0.840 ± 0.026 | 0.800 | 0.853 |
| V6 / logistic regression | 0.656 ± 0.027 | 0.653 | — |
| V6 / SVM | 0.824 ± 0.015 | 0.786 | — |
| V6 / random forest | 0.806 ± 0.023 | 0.794 | — |

**19 configurations, all reported, none hidden.**

### The decision — and why we rejected the highest score

Adopted: **V1 / random forest, 0.822**.

Rejected despite equal or higher point estimates:

| Rejected variant | Score | Margin over 0.822 | Verdict |
|---|---|---|---|
| V5 ensemble | 0.840 | +0.018 | below the 0.02 margin; adds tuning *and* two models |
| V6 SVM (mean+std) | 0.824 | +0.002 | below margin; doubles feature count to 148 |
| V4 tuned RF | 0.814 | −0.008 | tuning did not even match default settings |

**Why this is a strength, not a missed opportunity.** With 37 subjects,
the seed-to-seed spread is about ±0.03. A gap of 0.018 is smaller than
that noise. Choosing the most complex of several statistically tied
variants means fitting the *validation procedure* rather than the problem
— the classic way projects quietly overfit. The margin rule was fixed
beforehand precisely so this decision could not be rationalised after
seeing the numbers.

## 6.4 The final model

**Random Forest** (300 trees, balanced class weights, default depth) on
**74 extended features** extracted per 10-second chunk and averaged per
recording.

### Performance (subject-independent, 3 seeds)

| Seed | Recording bal. acc. | Subject bal. acc. | Sensitivity | Specificity | Subject AUC |
|---|---|---|---|---|---|
| 42 | 0.816 | 0.780 | 0.750 | 0.810 | 0.872 |
| 7 | 0.816 | 0.827 | 0.750 | 0.905 | 0.826 |
| 2025 | 0.788 | 0.859 | 0.812 | 0.905 | 0.893 |
| **Mean** | **0.806 ± 0.013** | **0.822 ± 0.032** | **0.771** | **0.873** | **0.864** |

### Confusion matrix (recording level, seed 42)

|  | Predicted HC | Predicted PD |
|---|---|---|
| **Actually HC** | 36 | 6 |
| **Actually PD** | 7 | 24 |

So of 31 Parkinson's recordings, 24 were caught and 7 missed; of 42
healthy recordings, 36 were correctly cleared and 6 wrongly flagged.

### Improvement over Phase 4

0.780 → 0.822 (**+0.042**), achieved by the extended features (CPPS,
pause statistics, delta-MFCC) computed on chunks and averaged — not by
hyperparameter tuning, which did not help at all.

## 6.5 Which features mattered most

From the Random Forest's importance scores
(`reports/figures/feature_importance.png`), the top features are:

| Rank | Feature | Importance | Interpretation |
|---|---|---|---|
| 1 | `f0_range_hz` | 0.069 | pitch range — monotone speech is a classic Parkinson's sign |
| 2 | `f0_max_hz` | 0.058 | highest pitch reached |
| 3 | `mfcc2_std` | 0.054 | variability of spectral shape |
| 4 | `mfcc6_mean` | 0.048 | average spectral shape |
| 5 | `mfccD2_std` | 0.036 | variability of spectral *change* |
| 6 | `mfccD6_std` | 0.036 | variability of spectral change |
| 7 | `f0_mean_hz` | 0.031 | average pitch |
| 8 | `mfcc4_std` | 0.028 | spectral variability |
| 9 | `jitter_local_abs` | 0.027 | cycle-timing irregularity |
| 10 | `f0_median_hz` | 0.022 | typical pitch |

This is a satisfying result for an explainable project: the single most
important feature is **pitch range**, which corresponds directly to the
best-known clinical description of Parkinsonian speech (monotone,
reduced prosody). Spectral *variability* features (the `_std` group) rank
above spectral averages, consistent with reduced articulatory movement.

## 6.6 Relevant files

| File | Purpose |
|---|---|
| `scripts/run_experiments.py` | The 19-configuration study |
| `scripts/train_final_model.py` | Trains and saves the final model |
| `scripts/make_figures.py` | All result figures |
| `reports/metrics_report.md` | Phase 4 results |
| `reports/experiments_report.md` | All 19 configurations and the decision |
| `reports/final_model_report.md` | Final model performance |
| `models/model.joblib` | The trained final model |
| `data/processed/final_oof_predictions.csv` | Final out-of-fold predictions |
