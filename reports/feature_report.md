# Phase 3 feature extraction report

Feature table: `C:\Users\MShaheen\Documents\parkinsons_voice_project\data\processed\features.csv`

## Contents

- Recordings (rows): **73**
- Feature columns: **43**
- Metadata columns: ['relative_path', 'subject_id', 'task', 'label', 'duration_s']
- Recordings per class: HC: 42, PD: 31
- Subjects: 37 (traceability: every row keeps subject_id, task, label, and path)

### Feature groups

| group | features | source |
|:--|:--|:--|
| F0 statistics | mean, median, std, min, max, range, voiced fraction (7) | Praat pitch tracking |
| Jitter | local, local absolute, RAP, PPQ5 (4) | Praat point process |
| Shimmer | local, local dB, APQ3, APQ5, APQ11 (5) | Praat point process |
| Noise | mean HNR (1) | Praat harmonicity (cc) |
| MFCC | mean + std of 13 coefficients (26) | librosa |

## Missing values (NaN)

No missing values anywhere in the table.

## Infinite values

None found.

## Impossible / implausible values

All values inside their physical plausibility ranges (MFCCs have no fixed range and are excluded from this check).

## Suspiciously constant features

None: every feature varies across recordings.

## Duplicate feature vectors

None: all recordings have distinct feature vectors.

## Limitations to keep in mind

- MDVR-KCL contains continuous speech (reading, dialogue), not sustained vowels. Jitter, shimmer and HNR are classically defined on sustained phonation, so their values here are noisier and should be interpreted as rough voice-quality indicators.
- Praat measures perturbation only on voiced stretches it can track; recordings with little stable voicing yield NaN (reported above) rather than fabricated numbers.
- MFCC summary statistics compress each whole recording into mean/std per coefficient; temporal detail is intentionally discarded for explainability.

**Validation verdict: PASS - table is ready for modeling (Phase 4).**
