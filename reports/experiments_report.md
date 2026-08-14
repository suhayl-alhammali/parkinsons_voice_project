# Accuracy-improvement experiments

Protocol: StratifiedGroupKFold (5 folds, subject groups), 3 seeds; primary metric = subject-level balanced accuracy (mean +/- std across seeds). Adoption needs > 0.02 improvement over the simpler variant. The saved production model is unchanged by this script.

| variant/model | subject bal.acc | recording bal.acc | subject AUC | subject sens. | subject spec. |
|:--|--:|--:|--:|--:|--:|
| V0_rec_base/logistic_regression | 0.704 +/- 0.029 | 0.685 +/- 0.059 | 0.765 | 0.646 | 0.762 |
| V0_rec_base/svm_rbf | 0.780 +/- 0.019 | 0.761 +/- 0.026 | 0.789 | 0.750 | 0.810 |
| V0_rec_base/random_forest | 0.725 +/- 0.019 | 0.725 +/- 0.015 | 0.808 | 0.688 | 0.762 |
| V1_rec_extended/logistic_regression | 0.746 +/- 0.029 | 0.677 +/- 0.035 | 0.788 | 0.667 | 0.825 |
| V1_rec_extended/svm_rbf | 0.816 +/- 0.026 | 0.792 +/- 0.018 | 0.841 | 0.792 | 0.841 |
| V1_rec_extended/random_forest | 0.822 +/- 0.032 | 0.806 +/- 0.013 | 0.864 | 0.771 | 0.873 |
| V2_chunk_base/logistic_regression | 0.769 +/- 0.042 | 0.770 +/- 0.013 | 0.841 | 0.729 | 0.810 |
| V2_chunk_base/svm_rbf | 0.817 +/- 0.010 | 0.781 +/- 0.013 | 0.826 | 0.729 | 0.905 |
| V2_chunk_base/random_forest | 0.780 +/- 0.011 | 0.750 +/- 0.010 | 0.802 | 0.688 | 0.873 |
| V3_chunk_extended/logistic_regression | 0.772 +/- 0.059 | 0.752 +/- 0.019 | 0.817 | 0.688 | 0.857 |
| V3_chunk_extended/svm_rbf | 0.793 +/- 0.024 | 0.757 +/- 0.005 | 0.820 | 0.729 | 0.857 |
| V3_chunk_extended/random_forest | 0.780 +/- 0.011 | 0.775 +/- 0.011 | 0.820 | 0.688 | 0.873 |
| V4_tuned/logistic_regression | 0.772 +/- 0.028 | 0.751 +/- 0.005 | 0.829 | 0.750 | 0.794 |
| V4_tuned/svm_rbf | 0.775 +/- 0.043 | 0.755 +/- 0.032 | 0.815 | 0.708 | 0.841 |
| V4_tuned/random_forest | 0.814 +/- 0.024 | 0.810 +/- 0.008 | 0.870 | 0.771 | 0.857 |
| V5_ensemble/svm_plus_rf | 0.840 +/- 0.026 | 0.800 +/- 0.013 | 0.853 | 0.792 | 0.889 |

Best untuned variant: **V1_rec_extended/random_forest**

## Additional pre-justified variant

V6: like V1 but summarizing chunks with mean AND std per feature (148
columns; rationale: intra-recording variability is a known PD marker).

| variant/model | subject bal.acc | recording bal.acc |
|:--|--:|--:|
| V6_rec_meanstd/logistic_regression | 0.656 +/- 0.027 | 0.653 |
| V6_rec_meanstd/svm_rbf | 0.824 +/- 0.015 | 0.786 |
| V6_rec_meanstd/random_forest | 0.806 +/- 0.023 | 0.794 |

## Final decision (pre-declared rules applied)

Adopted: **V1_rec_extended / random_forest** - subject-level balanced
accuracy **0.822 +/- 0.032** (recording-level 0.806, subject AUC 0.864),
vs 0.780 for the Phase 4 reference (V0 svm_rbf): **+0.042**.

Rejected despite equal or higher point estimates, because none beat V1's
random forest by the pre-declared +0.02 margin that a MORE COMPLEX variant
must clear:

- V5 ensemble (0.840): +0.018 < margin; adds tuning + two-model ensemble.
- V6 mean+std SVM (0.824): +0.002 < margin; doubles the feature count.
- V4 tuned RF (0.814): tuning did not even match the default settings.

This margin rule exists to limit selection overfitting: with 37 subjects,
differences of ~0.02 are within seed-to-seed noise, and choosing the most
complex of several near-tied variants would fit the validation data, not
the problem. 19 configurations were evaluated in total; all are reported
above (none hidden).

The final configuration was retrained and saved by
scripts/train_final_model.py (see reports/final_model_report.md).
