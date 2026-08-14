# Final model report (after accuracy-improvement experiments)

**Research screening-support prototype - not a medical diagnostic system.**

- Model: Random Forest (300 trees, balanced class weights, default depth), pipeline = median imputer + standard scaler + RF.
- Features: 74 extended features (F0, jitter, shimmer, HNR, CPPS, pause statistics, MFCC + delta-MFCC summary) extracted per 10-s chunk and averaged per recording.
- Data: 73 recordings, 37 subjects.
- Validation: StratifiedGroupKFold (5 folds, subject groups), 3 seeds; identical protocol to the experiments that selected this configuration.

| seed | recording bal.acc | subject bal.acc | subject sens. | subject spec. | subject ROC-AUC |
|--:|--:|--:|--:|--:|--:|
| 42 | 0.816 | 0.780 | 0.750 | 0.810 | 0.872 |
| 7 | 0.816 | 0.827 | 0.750 | 0.905 | 0.826 |
| 2025 | 0.788 | 0.859 | 0.812 | 0.905 | 0.893 |

Mean subject-level: balanced accuracy 0.822, sensitivity 0.771, specificity 0.873, ROC-AUC 0.864.

Recording-level confusion matrix (seed 42; rows = true HC, PD; cols = predicted HC, PD):

```
[[36  6]
 [ 7 24]]
```

Out-of-fold predictions (seed 42): `final_oof_predictions.csv`.

Improvement over Phase 4 (same protocol): subject-level balanced accuracy 0.780 -> 0.822 (+0.042), driven by the extended features (CPPS, pauses, delta-MFCC) computed on 10-s chunks and averaged. Hyperparameter tuning, ensembling and mean+std summaries did not beat this by the pre-declared +0.02 margin and were rejected to limit overfitting risk (see experiments_report.md).
