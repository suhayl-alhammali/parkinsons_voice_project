# Phase 4: model evaluation report

**This is a research screening-support prototype. It is not a medical diagnostic system, and none of the numbers below are claims of diagnostic performance.**

## Evaluation design and leakage safeguards

- Data: 73 recordings, 37 subjects (HC 42 recordings / PD 31 recordings).
- Validation: StratifiedGroupKFold, 5 folds, groups = subject_id, shuffled with fixed random seed (42).
- No subject ever appears in both training and test of a fold; a hard runtime assertion re-checks every fold and aborts on overlap (it never triggered).
- Imputation (median) and scaling are steps INSIDE each model pipeline, so they are re-fit on the training part of every fold only. No preprocessing was fit on the full dataset before CV. No feature selection was performed on the full dataset.
- Every recording is predicted exactly once, by a model that never saw that subject. All metrics below are computed from these out-of-fold predictions (saved with subject IDs to `oof_predictions.csv`).
- Subject-level prediction rule: mean of the subject's recording-level PD probabilities, class = PD if mean >= 0.5.

## Results per model

### baseline_majority

| metric | per-fold mean +/- std | pooled recording-level | subject-level |
|:--|:--|--:|--:|
| accuracy | 0.575 +/- 0.029 | 0.575 | 0.568 |
| balanced_accuracy | 0.500 +/- 0.000 | 0.500 | 0.500 |
| sensitivity_pd | 0.000 +/- 0.000 | 0.000 | 0.000 |
| specificity_hc | 1.000 +/- 0.000 | 1.000 | 1.000 |
| precision | 0.000 +/- 0.000 | 0.000 | 0.000 |
| f1 | 0.000 +/- 0.000 | 0.000 | 0.000 |
| roc_auc | 0.500 +/- 0.000 | 0.500 | 0.500 |

Per-fold balanced accuracy: 0.500, 0.500, 0.500, 0.500, 0.500

Pooled confusion matrices (rows = true HC, PD; cols = predicted HC, PD):

```
recording level:      subject level:
   42   0                21   0
   31   0                16   0
```

### logistic_regression

| metric | per-fold mean +/- std | pooled recording-level | subject-level |
|:--|:--|--:|--:|
| accuracy | 0.671 +/- 0.175 | 0.671 | 0.676 |
| balanced_accuracy | 0.640 +/- 0.195 | 0.651 | 0.662 |
| sensitivity_pd | 0.500 +/- 0.365 | 0.516 | 0.562 |
| specificity_hc | 0.780 +/- 0.149 | 0.786 | 0.762 |
| precision | 0.573 +/- 0.329 | 0.640 | 0.643 |
| f1 | 0.508 +/- 0.327 | 0.571 | 0.600 |
| roc_auc | 0.705 +/- 0.161 | 0.717 | 0.747 |

Per-fold balanced accuracy: 0.533, 0.812, 0.312, 0.833, 0.708

Pooled confusion matrices (rows = true HC, PD; cols = predicted HC, PD):

```
recording level:      subject level:
   33   9                16   5
   15  16                 7   9
```

### svm_rbf

| metric | per-fold mean +/- std | pooled recording-level | subject-level |
|:--|:--|--:|--:|
| accuracy | 0.768 +/- 0.122 | 0.767 | 0.784 |
| balanced_accuracy | 0.763 +/- 0.126 | 0.768 | 0.780 |
| sensitivity_pd | 0.767 +/- 0.200 | 0.774 | 0.750 |
| specificity_hc | 0.760 +/- 0.159 | 0.762 | 0.810 |
| precision | 0.714 +/- 0.145 | 0.706 | 0.750 |
| f1 | 0.731 +/- 0.153 | 0.738 | 0.750 |
| roc_auc | 0.741 +/- 0.159 | 0.741 | 0.789 |

Per-fold balanced accuracy: 0.733, 0.750, 0.625, 1.000, 0.708

Pooled confusion matrices (rows = true HC, PD; cols = predicted HC, PD):

```
recording level:      subject level:
   32  10                17   4
    7  24                 4  12
```

### random_forest

| metric | per-fold mean +/- std | pooled recording-level | subject-level |
|:--|:--|--:|--:|
| accuracy | 0.752 +/- 0.099 | 0.753 | 0.730 |
| balanced_accuracy | 0.732 +/- 0.109 | 0.739 | 0.725 |
| sensitivity_pd | 0.633 +/- 0.267 | 0.645 | 0.688 |
| specificity_hc | 0.830 +/- 0.171 | 0.833 | 0.762 |
| precision | 0.747 +/- 0.169 | 0.741 | 0.688 |
| f1 | 0.656 +/- 0.205 | 0.690 | 0.688 |
| roc_auc | 0.799 +/- 0.148 | 0.775 | 0.813 |

Per-fold balanced accuracy: 0.783, 0.750, 0.521, 0.833, 0.771

Pooled confusion matrices (rows = true HC, PD; cols = predicted HC, PD):

```
recording level:      subject level:
   35   7                16   5
   11  20                 5  11
```

### mlp

| metric | per-fold mean +/- std | pooled recording-level | subject-level |
|:--|:--|--:|--:|
| accuracy | 0.685 +/- 0.053 | 0.685 | 0.703 |
| balanced_accuracy | 0.663 +/- 0.048 | 0.671 | 0.686 |
| sensitivity_pd | 0.571 +/- 0.178 | 0.581 | 0.562 |
| specificity_hc | 0.755 +/- 0.181 | 0.762 | 0.810 |
| precision | 0.688 +/- 0.159 | 0.643 | 0.692 |
| f1 | 0.596 +/- 0.093 | 0.610 | 0.621 |
| roc_auc | 0.743 +/- 0.140 | 0.736 | 0.777 |

Per-fold balanced accuracy: 0.617, 0.679, 0.646, 0.750, 0.625

Pooled confusion matrices (rows = true HC, PD; cols = predicted HC, PD):

```
recording level:      subject level:
   32  10                17   4
   13  18                 7   9
```

## Baseline comparison

The majority-class baseline (always predicts HC) reaches accuracy 0.575 but balanced accuracy 0.500 and sensitivity for PD 0.000: it never finds a PD case. Any useful model must clearly beat 0.5 balanced accuracy; comparisons above use balanced accuracy for exactly this reason.

## Model selection

Rule: highest robust score = (mean balanced accuracy across folds) - (std across folds), recording level; ties broken by mean ROC-AUC. The std penalty prefers models that are stable across folds rather than occasionally lucky.

| model | robust score | mean ROC-AUC |
|:--|--:|--:|
| svm_rbf | 0.637 | 0.741 |
| random_forest | 0.623 | 0.799 |
| mlp | 0.615 | 0.743 |
| logistic_regression | 0.445 | 0.705 |

**Selected model: svm_rbf**. It was refit on all 73 recordings and saved for the Phase 5 prototype.

## Confounder and task analysis

### Absolute F0 and (unrecorded) speaker sex

MDVR-KCL provides no verified per-subject sex/age metadata in the audio distribution, so a direct check of group composition is not possible without guessing - which we do not do. Absolute pitch features (F0 mean/median/min/max) are the features most likely to encode speaker sex. The HC group's mean F0 is ~180 Hz vs ~154 Hz for PD, a difference more plausibly explained by group composition than by disease. To measure how much the models depend on this, CV was repeated without those 4 features:

| model | balanced accuracy (all features) | balanced accuracy (without absolute F0) |
|:--|--:|--:|
| logistic_regression | 0.651 | 0.699 |
| svm_rbf | 0.768 | 0.780 |
| random_forest | 0.739 | 0.707 |
| mlp | 0.671 | 0.526 |

If performance collapses without absolute F0, the models were leaning on a potential sex confound; if it holds, the perturbation/MFCC features carry the real signal.

### Performance by task

Recording-level accuracy of each model split by task (from the same OOF predictions):

| model | ReadText | SpontaneousDialogue |
|:--|--:|--:|
| baseline_majority | 0.568 | 0.583 |
| logistic_regression | 0.622 | 0.722 |
| svm_rbf | 0.784 | 0.750 |
| random_forest | 0.730 | 0.778 |
| mlp | 0.649 | 0.722 |

## Warnings and suspicious results

No model reached the 95% suspicion threshold on accuracy, balanced accuracy, or ROC-AUC.

## Limitations

- 37 subjects is small; fold-to-fold variation above is large and any single headline number should be read with its std.
- Recording conditions are homogeneous per class group; results may not transfer to other microphones, rooms, or languages.
- Continuous speech makes jitter/shimmer/HNR noisier than sustained-vowel protocols.
- Speaker sex/age are not available, so demographic confounding cannot be fully excluded - only bounded by the ablation above.
- This is a research screening prototype; it must not be used for medical decisions.
