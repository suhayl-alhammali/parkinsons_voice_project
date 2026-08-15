# External validation: Italian Parkinson's Voice and Speech

**Frozen MDVR-KCL model, zero adaptation. Cross-dataset AND cross-language (English -> Italian). This measures generalization; lower numbers than the internal 0.822 were expected by design.**

## Setup

- Included: 216 recordings >= 30 s (61 speakers; per-speaker score = mean over their recordings, threshold 0.5).
- All audio bandwidth-harmonized to 16 kHz before the standard pipeline (prevents the sample-rate/label confound documented in italian_dataset_report.md).
- Failures: 0.

## Headline: elderly HC vs PD (age-fair, subject level)

| metric | value |
|:--|--:|
| balanced_accuracy | 0.629 |
| sensitivity_pd | 0.667 |
| specificity_hc | 0.591 |
| roc_auc | 0.701 |

Confusion (subject level): elderly HC 13 correct / 9 flagged PD; PD 16 caught / 8 missed.

## Secondary observations

- Young HC (15 speakers, all healthy): 3 classified HC, 12 flagged PD (specificity 0.200).
- Inconclusive-band fraction (recordings): 71.3%; per speaker group: elderly HC 100.0%, PD 62.5%, young HC 53.3%.
- Mean PD score by group: elderly HC 0.489, PD 0.566, young HC 0.626.

## Interpretation notes

- The model never saw Italian speech, these microphones, or the 16 kHz bandwidth during training; every gap between this result and the internal 0.822 quantifies domain shift.
- Bandwidth harmonization makes the comparison fair WITHIN the Italian dataset but also removes high-frequency content the model's MFCC features saw during training, shifting absolute scores; discrimination (AUC) is the most meaningful number here.
- Speaker-level results dominate: recordings per speaker vary (1-4 included), so per-recording metrics are secondary.
