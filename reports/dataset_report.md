# MDVR-KCL dataset inspection report

Dataset folder: `C:\Users\MShaheen\Documents\parkinsons_voice_project\data\raw\mdvr_kcl`

## Folder structure

Folders containing audio, relative to the dataset folder:

- `ReadText\HC` (21 files)
- `ReadText\PD` (16 files)
- `SpontaneousDialogue\HC` (21 files)
- `SpontaneousDialogue\PD` (15 files)

## Overview

- Total audio files found: **73**
- Usable files (label + subject ID, no problems): **73**
- Audio formats: ['.wav']
- Sample rates: [44100]
- Channels: [1]

## Durations (seconds)

- min: 73.04  |  median: 141.29  |  mean: 141.35  |  max: 220.64

## Labels and tasks

Label was inferred from the HC/PD folder name and the `_hc_`/`_pd_` tag inside each filename. Files where the two disagree are excluded and listed under problems.

Files per task and label:

| task                | label   |   files |
|:--------------------|:--------|--------:|
| ReadText            | HC      |      21 |
| ReadText            | PD      |      16 |
| SpontaneousDialogue | HC      |      21 |
| SpontaneousDialogue | PD      |      15 |

## Subjects

Subject ID was inferred from the leading `ID<number>` token in each filename. Recordings from one subject are always kept together during validation (GroupKFold).

- Subjects with usable data: **37**
- Subjects in class HC: **21**
- Subjects in class PD: **16**

Recordings per subject:

| label   | subject_id   |   recordings |
|:--------|:-------------|-------------:|
| HC      | ID00         |            2 |
| HC      | ID01         |            2 |
| HC      | ID03         |            2 |
| HC      | ID05         |            2 |
| HC      | ID08         |            2 |
| HC      | ID09         |            2 |
| HC      | ID10         |            2 |
| HC      | ID11         |            2 |
| HC      | ID12         |            2 |
| HC      | ID14         |            2 |
| HC      | ID15         |            2 |
| HC      | ID19         |            2 |
| HC      | ID21         |            2 |
| HC      | ID22         |            2 |
| HC      | ID23         |            2 |
| HC      | ID25         |            2 |
| HC      | ID26         |            2 |
| HC      | ID28         |            2 |
| HC      | ID31         |            2 |
| HC      | ID35         |            2 |
| HC      | ID36         |            2 |
| PD      | ID02         |            2 |
| PD      | ID04         |            2 |
| PD      | ID06         |            2 |
| PD      | ID07         |            2 |
| PD      | ID13         |            2 |
| PD      | ID16         |            2 |
| PD      | ID17         |            2 |
| PD      | ID18         |            1 |
| PD      | ID20         |            2 |
| PD      | ID24         |            2 |
| PD      | ID27         |            2 |
| PD      | ID29         |            2 |
| PD      | ID30         |            2 |
| PD      | ID32         |            2 |
| PD      | ID33         |            2 |
| PD      | ID34         |            2 |

## Integrity checks

- Duplicate file contents (MD5): none found.
- Subjects appearing in more than one class: none found.

## Problem files

None found.

## Risk notes

- Small dataset: results may not generalize; report per-fold variation, not just the mean.
- All recordings of one subject share recording conditions; subject-independent validation is mandatory and is enforced in code.
- If accuracy looks very high (>= 95%), treat it as a warning sign and investigate for leakage before believing it.
