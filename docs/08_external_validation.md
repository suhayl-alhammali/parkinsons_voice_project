# 8. External validation on the Italian dataset

## 8.1 Why this step is the strongest scientific evidence

All results up to this point came from one dataset. Cross-validation
proves the model works on *new people*, but every one of those people was
recorded with the same phone, in the same room, speaking the same
language.

A model can pass that test and still fail completely on a different
microphone or a different language — it may have learned the recording
setup rather than the disease. The only way to know is to test on data
from a genuinely different source.

Very few undergraduate projects do this. It is also risky: the number
almost always drops. We did it anyway, and report the drop.

## 8.2 The dataset

**Italian Parkinson's Voice and Speech** (Dimauro & Girardi), obtained
from a public Hugging Face mirror under a CC-BY-4.0 licence.

| Property | Value |
|---|---|
| Audio files | 831 (all WAV, all mono) |
| Speakers | 61 total |
| Young healthy controls | 15 speakers, 45 files |
| Elderly healthy controls | 22 speakers, 349 files |
| Parkinson's patients | 24 speakers, 437 files |
| Sample rates | 16000 Hz (671 files), 44100 Hz (160 files) |
| Durations | 3.4 s to 250.3 s (median 11.6 s), 5.6 hours total |
| Corrupt or unreadable files | none |

The dataset includes several task types: read passages, sustained vowels,
and syllable repetitions.

**The model was never trained or tuned on any of it.**

## 8.3 The trap we caught before running anything

The inspection report revealed a dangerous pattern:

| Group | 16000 Hz files | 44100 Hz files |
|---|---|---|
| Young healthy | 45 | 0 |
| Elderly healthy | 349 | 0 |
| Parkinson's | 277 | **160** |

**Every single 44.1 kHz file belongs to the Parkinson's group.** All
healthy files are 16 kHz.

Why this matters: a 16 kHz recording physically cannot contain any sound
above 8 kHz, while a 44.1 kHz recording can contain up to 22 kHz. Our
MFCC features see the whole spectrum. A model could therefore separate the
groups almost perfectly by detecting **recording bandwidth** — a property
of the microphone, not the person — and we would have reported a
flattering, meaningless result.

**The fix:** every included file is first downsampled to 16 kHz, removing
all content above 8 kHz for *everyone* equally, then resampled back up to
the pipeline's standard 44.1 kHz. After this bandwidth harmonisation, no
group can be identified by its recording bandwidth.

This is a good example of the project's general discipline: inspect
before evaluating, and assume nothing.

## 8.4 The evaluation design (agreed before running)

1. **Inclusion rule:** only recordings of at least **30 seconds** — the
   continuous read-speech tasks. The short vowel and syllable recordings
   do not match our pipeline's assumptions. Result: **216 recordings from
   61 speakers**.
2. **Bandwidth harmonisation** to 16 kHz as described above.
3. **The model is frozen**: no retraining, no threshold adjustment, no
   adaptation of any kind.
4. **Aggregation:** score per recording, then averaged per speaker,
   threshold 0.5 — identical to internal evaluation.
5. **Headline comparison: elderly healthy vs Parkinson's**, because the
   Parkinson's group is elderly and comparing them against *young* healthy
   speakers would confuse age with disease. Young controls are reported
   separately.

Zero extraction failures occurred across all 216 recordings.

## 8.5 Results

### Headline: elderly healthy vs Parkinson's (per speaker)

| Metric | Internal (MDVR-KCL) | External (Italian) |
|---|---|---|
| Balanced accuracy | 0.822 | **0.629** |
| ROC-AUC | 0.864 | **0.701** |
| Sensitivity (PD caught) | 0.771 | 0.667 |
| Specificity (HC cleared) | 0.873 | 0.591 |

Confusion at speaker level: of 22 elderly healthy speakers, 13 were
correctly cleared and 9 wrongly flagged; of 24 Parkinson's speakers, 16
were caught and 8 missed.

### What this means

**The good news:** an AUC of 0.701 means that given a random Parkinson's
speaker and a random healthy speaker, the model still ranks the patient
higher 70% of the time — despite a different country, language,
microphone, room, and bandwidth, with zero adaptation. The acoustic signal
it learned is therefore *not* pure dataset memorisation. Some genuine,
transferable voice information is being captured.

**The honest news:** hard classification near the 0.5 threshold degrades
badly. Balanced accuracy of 0.629 and specificity of 0.591 mean that in
this foreign setting, roughly 4 in 10 healthy people would be wrongly
flagged. The model as it stands is not usable outside its training
conditions — which is exactly why the prototype refuses to give confident
answers there.

## 8.6 Two findings more valuable than the headline number

### Finding 1 — the inconclusive band worked exactly as designed

| Group | Fraction in the inconclusive band |
|---|---|
| All recordings | 71.3% |
| Elderly healthy speakers | **100%** |
| Parkinson's speakers | 62.5% |
| Young healthy speakers | 53.3% |

Every single elderly healthy speaker fell in the inconclusive band. The
system did not confidently mislabel foreign healthy speakers as
Parkinson's patients — it said "I cannot tell", which is the correct
answer for input this far outside its experience.

### Finding 2 — the young healthy anomaly proves domain shift

Mean PD score by group:

| Group | Mean score |
|---|---|
| Elderly healthy | 0.489 |
| **Parkinson's** | **0.566** |
| **Young healthy** | **0.626** |

Young, healthy speakers scored *more* Parkinson's-like than actual
Parkinson's patients, and only 3 of 15 were classified healthy
(specificity 0.200).

This is impossible as a medical result — healthy young people cannot be
"more Parkinsonian" than patients. It therefore proves that in
out-of-domain conditions, the score is substantially driven by
**recording channel and speaking style**, not by disease. Rather than
hiding this, we report it as direct evidence for why the cautious
interface design is necessary.

(A plausible contributing explanation: the young control recordings differ
from the others in speaking style and recording setup, and our features
are sensitive to those differences.)

## 8.7 Interpretation notes for the report

- Bandwidth harmonisation makes the comparison fair *within* the Italian
  dataset, but it also removes high-frequency content that the model saw
  during training. This shifts absolute scores, so **AUC is the most
  meaningful cross-dataset number** — it measures ranking ability
  independently of where the threshold falls.
- The number of included recordings per speaker varies, so speaker-level
  results are the primary ones.
- Language differs (Italian vs English). Perturbation features (jitter,
  shimmer, HNR, CPPS) and pause statistics are relatively
  language-independent; MFCC features are not, which likely explains much
  of the drop.

## 8.8 Relevant files

| File | Purpose |
|---|---|
| `scripts/inspect_italian_dataset.py` | Structure inspection, confound detection |
| `scripts/evaluate_external.py` | The frozen-model evaluation |
| `reports/italian_dataset_report.md` | Dataset inspection report |
| `reports/external_validation_report.md` | Results report |
| `reports/figures/external_scores.png` | All 61 speakers' scores in one figure |
| `data/processed/external_predictions.csv` | Per-recording predictions |
