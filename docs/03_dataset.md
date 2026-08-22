# 3. The dataset: MDVR-KCL

## 3.1 What it is

**MDVR-KCL** = *Mobile Device Voice Recordings at King's College London*.
It contains voice recordings from people diagnosed with Parkinson's
disease and from healthy control subjects, captured on a mobile phone in a
controlled setting. It is publicly available from Zenodo
(https://zenodo.org/record/2867216).

The audio itself is **not** stored in the project's GitHub repository —
it is large and carries its own licence. The repository contains
instructions for downloading it into `data/raw/mdvr_kcl/`.

## 3.2 Folder structure

```
data/raw/mdvr_kcl/
├── ReadText/
│   ├── HC/    21 files   (healthy controls reading a fixed text)
│   └── PD/    16 files   (Parkinson's patients reading the same text)
└── SpontaneousDialogue/
    ├── HC/    21 files   (healthy controls in free conversation)
    └── PD/    15 files   (Parkinson's patients in free conversation)
```

Two recording tasks therefore exist:

- **ReadText** — every speaker reads the *same* passage. Content is
  controlled, so differences between speakers come from *how* they speak,
  not *what* they say.
- **SpontaneousDialogue** — free speech. More natural, but content varies
  between speakers.

## 3.3 Exact contents (from the inspection report)

| Property | Value |
|---|---|
| Total audio files | 73 |
| Usable files (valid label + subject ID, no problems) | 73 |
| File format | WAV only |
| Sample rate | 44100 Hz (all files) |
| Channels | 1 (mono, all files) |
| Shortest recording | 73.04 seconds |
| Median recording | 141.29 seconds |
| Mean recording | 141.35 seconds |
| Longest recording | 220.64 seconds |

**Subjects:**

| Group | Subjects | Recordings |
|---|---|---|
| HC (healthy control) | 21 | 42 |
| PD (Parkinson's disease) | 16 | 31 |
| **Total** | **37** | **73** |

Almost every subject contributed exactly 2 recordings (one per task). The
single exception is PD subject `ID18`, who has only 1 recording — which is
why 37 subjects produce 73 rather than 74 recordings.

## 3.4 How labels were determined

The class label is **not** guessed. It is read from **two independent
sources** and cross-checked:

1. The folder name (`HC` or `PD`).
2. A tag inside the filename (`_hc_` or `_pd_`), e.g.
   `ID00_hc_0_0_0.wav`, `ID02_pd_2_1_1.wav`.

If the two sources ever disagreed, the file would be **excluded** and
listed as a label conflict rather than silently assigned. In practice, no
conflicts were found.

## 3.5 How subject identity was determined

The subject ID is the leading `ID<number>` token of the filename — for
example `ID00_hc_0_0_0.wav` belongs to subject `ID00`. This is the single
most important piece of metadata in the entire project, because it makes
subject-independent validation possible: the two recordings of `ID00` must
always travel together into either the training set or the test set, never
be split.

Files without a recognisable subject ID would be excluded and reported.
None were found.

## 3.6 Integrity checks performed

| Check | Result |
|---|---|
| Corrupt or unreadable files | none |
| Empty or zero-length files | none |
| Duplicate file contents (MD5 hash comparison) | none |
| Label conflicts (folder vs filename) | none |
| Files without a subject ID | none |
| Subjects appearing in more than one class | none |
| Very short or silent recordings | none |

The duplicate check matters: if the same audio file existed twice under
different names, it could land in both training and test sets and inflate
results. It did not happen here, but it was verified rather than assumed.

## 3.7 Known risks recorded in the report

1. **Small dataset.** 37 subjects is few. Results must always be reported
   with fold-to-fold variation, never as a single confident number.
2. **Shared recording conditions within a subject.** Both recordings of a
   person share the same voice, microphone position, and session — so
   subject-independent validation is mandatory, not optional.
3. **Class imbalance.** 42 HC vs 31 PD recordings, so plain accuracy is
   misleading and balanced accuracy is used instead.
4. **No demographic metadata.** The distributed audio carries no verified
   per-subject age or sex information. Since pitch strongly reflects
   speaker sex, this is a potential hidden confounder — addressed by an
   ablation experiment rather than ignored (see
   [06_experiments_and_results.md](06_experiments_and_results.md)).
5. **High-accuracy warning rule.** Any result ≥ 95% is treated as a
   symptom of leakage to be investigated, not a success.

## 3.8 The second dataset (used only for testing)

A completely separate dataset — the **Italian Parkinson's Voice and
Speech** corpus — was later used as an external test set. It is described
in [08_external_validation.md](08_external_validation.md). The model was
**never trained on it**.

## 3.9 Relevant files

| File | Purpose |
|---|---|
| `src/pvoice/dataset.py` | Finds audio files, extracts labels and subject IDs, flags problems |
| `scripts/inspect_dataset.py` | Produces the inspection report |
| `reports/dataset_report.md` | The generated report summarised above |
| `data/raw/mdvr_kcl/README_PLACE_DATASET_HERE.txt` | Download and placement instructions |
