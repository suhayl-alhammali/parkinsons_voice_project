# External dataset report: Italian Parkinson's Voice and Speech

Source: Hugging Face mirror `birgermoell/Italian_Parkinsons_Voice_and_Speech` (CC-BY-4.0); original dataset by Dimauro & Girardi, IEEE DataPort.
Role in this project: **external test set only** - the model is never trained on it.

- Audio files probed: 831 (of 831 found)

## Groups (folder names verbatim)

| group folder | mapped label | age group | files | speakers |
|:--|:--|:--|--:|--:|
| 15 Young Healthy Control | HC | young | 45 | 15 |
| 22 Elderly Healthy Control | HC | elderly | 349 | 22 |
| 28 People with Parkinson's disease | PD | elderly | 437 | 24 |

## Files per speaker

- Speakers total: 61
- Files per speaker: min 3, median 16, max 48

## Audio properties

Sample rate by group (a correlation between sample rate and label would be a channel confound for the evaluation):

| group | 16000 | 44100 |
|:--|--:|--:|
| 15 Young Healthy Control | 45 | 0 |
| 22 Elderly Healthy Control | 349 | 0 |
| 28 People with Parkinson's disease | 277 | 160 |

- Sample rates: {44100: 160, 16000: 671}
- Channels: {1: 831}
- Formats: {'WAV': 831}
- Durations: min 3.4s, median 11.6s, max 250.3s, total 5.6h
- Files shorter than 10 s: 370 (short vowel/syllable tasks; only longer read-text recordings match our training conditions)

## Example filenames (first 3 per group)

**15 Young Healthy Control**
- `italian_parkinson\15 Young Healthy Control\Alberto R\B1LBULCAAS94M100120171015.wav` (38.3s)
- `italian_parkinson\15 Young Healthy Control\Alberto R\B2LBULCAAS94M100120171015.wav` (39.2s)
- `italian_parkinson\15 Young Healthy Control\Alberto R\PR1LBULCAAS94M100120171015..wav` (45.9s)

**22 Elderly Healthy Control**
- `italian_parkinson\22 Elderly Healthy Control\AGNESE P\B1APGANRET55F170320171104.wav` (102.3s)
- `italian_parkinson\22 Elderly Healthy Control\AGNESE P\B2APGANRET55F170320171105.wav` (77.7s)
- `italian_parkinson\22 Elderly Healthy Control\AGNESE P\D1APGANRET55F170320171106.wav` (6.8s)

**28 People with Parkinson's disease**
- `italian_parkinson\28 People with Parkinson's disease\6-10\Luigi B\B1lbuairgo52M1606161810.wav` (56.0s)
- `italian_parkinson\28 People with Parkinson's disease\6-10\Luigi B\B2lbuairgo52M1606161811.wav` (53.5s)
- `italian_parkinson\28 People with Parkinson's disease\6-10\Luigi B\D1lbuairgo52M1606161812.wav` (6.5s)

## Problems

None: all files readable, none shorter than 1 s.

## Risks and notes for the external evaluation

- Language differs (Italian vs English training data): read-text content and phonetics shift MFCC-type features; perturbation features (jitter, shimmer, HNR, CPPS) are more language-independent.
- The young-HC group makes age a confound: the fair comparison for our model is ELDERLY HC vs PD; young-HC results are reported separately.
- Recording equipment and rooms differ from MDVR-KCL; this is exactly the domain shift the external evaluation measures.
- Sample rates differing from 44100 Hz are resampled by our standard pipeline (and flagged).
- **Sample-rate/label confound found**: every 44100 Hz file belongs to the PD group (all HC files are 16000 Hz). A fair evaluation must bandwidth-harmonize: downsample ALL Italian files to 16 kHz first (removing content above 8 kHz everywhere) so the model cannot separate groups by recording bandwidth.
- Task types differ: vowels/syllables vs continuous speech. Only recordings long enough for our pipeline (>= 30 s continuous speech, ideally read text) should enter the headline comparison; the evaluation script must state its inclusion rule.