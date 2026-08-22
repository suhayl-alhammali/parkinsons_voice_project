# 7. The prototype

## 7.1 What was built

Two ways to use the trained model, both calling **one shared function**,
`predict_file()` in `src/pvoice/predict.py`:

1. **Browser app** (`app.py`, built with Streamlit) — started with
   `streamlit run app.py`. Offers file upload or microphone recording.
2. **Command line** (`scripts/predict_file.py`) — for quick tests and for
   demonstrating that the pipeline is scriptable.

Because both call the same function, they can never disagree, and testing
that function tests both interfaces.

## 7.2 What happens when a file is analysed

| Step | Action | On failure |
|---|---|---|
| 1 | **Verify pipeline compatibility** — compare `models/pipeline_config.json` against the current code (sample rate, pitch range, MFCC settings, feature set, aggregation rule, and the full ordered feature list) | Refuse to predict; tell the user to retrain |
| 2 | **Validate the audio** — exists, non-empty, decodable, has samples, at least 1 second, not silent | Refuse with a plain-language explanation |
| 3 | **Preprocess** — mono, 44.1 kHz, DC removal, silence trim, peak normalise | — |
| 4 | **Split into 10-second chunks** | — |
| 5 | **Extract 74 features per chunk, average them** | — |
| 6 | **Apply the model** → class and PD-class score | — |
| 7 | **Interpret the score** — apply the inconclusive band | — |
| 8 | **Collect warnings** — short recording, sample-rate mismatch, clipping, low SNR | — |

Analysis takes roughly one minute for a two-minute recording; CPPS
extraction is the expensive part.

## 7.3 The inconclusive band

Scores between **0.35 and 0.65** are not reported as a class at all.
Instead the system says:

> "The research model could not clearly assign this recording to either
> class (the score is in the inconclusive middle range)."

**Why this exists.** The supervisor recorded himself and a healthy friend;
both scored about 0.65 and were labelled "PD". Investigation showed the
cause was not illness but *domain shift* — different microphone, room, and
language from the training data. Near the 0.5 boundary the evidence is
genuinely weak, and printing a confident class label there overstates what
the model knows.

The score distribution figure (`reports/figures/score_distribution.png`)
justifies the specific band: the overlap between the healthy and
Parkinson's score distributions is concentrated in exactly this region.

The external validation later confirmed the design: **71% of Italian
recordings landed in this band**, including **100% of elderly healthy
speakers** — the system said "I cannot tell" instead of confidently
mislabelling foreign speakers.

## 7.4 Recording-condition warnings

These never block a prediction; they attach plain-language notes.

| Warning | Trigger | Reason |
|---|---|---|
| Short recording | analysed audio under 10 s | Training recordings were 70+ seconds; short clips give unstable measurements |
| Sample-rate mismatch | native rate ≠ 44100 Hz | The file was resampled, which can subtly shift features |
| Clipping | more than 0.1% of samples at full scale | Microphone too loud/close; distortion inflates voice-quality measures |
| Noisy recording | estimated signal-to-noise ratio below 15 dB | Background noise pushes results toward unreliability |

The SNR estimate compares loud-frame energy with quiet-frame energy using
RMS percentiles over 50 ms frames — a rough but effective heuristic.

## 7.5 Microphone mode

Added after supervisor approval (it had been deliberately deferred by the
project rules until dataset results were good).

The app displays this before recording:

> "Microphone note: the research model was trained on recordings made with
> one specific phone in one quiet room. Your microphone, room, and
> language are different, so this mode mainly demonstrates how the system
> handles unfamiliar recordings — expect an inconclusive or unreliable
> result. Speak continuously for at least 30–60 seconds for the most
> stable measurements."

A second warning appears with the result. Recorded audio takes exactly the
same temporary-file path as uploads and is deleted immediately after
processing.

## 7.6 The mandatory wording

Shown prominently before **and** after every result, in both interfaces:

> **"This is a research screening-support prototype and is not a medical
> diagnostic tool. Its result must not replace evaluation by a qualified
> healthcare professional."**

The result sentence is deliberately phrased as a statement about the
*model*, not the person:

> "The acoustic pattern was classified by the research model as closer to
> the PD class / HC class."

And the score:

> "Model score for the PD class: 0.16 (0 = closer to HC, 1 = closer to
> PD). This score is a property of the research model, **not** a person's
> medical risk."

HC and PD are explained in plain language as similarity to dataset groups,
"it does not establish whether a person does or does not have any medical
condition."

## 7.7 Privacy and error handling

- **No audio is kept.** Uploaded or recorded audio is written to a
  temporary file that is deleted in a `finally` block — so it is removed
  even if analysis crashes.
- **No technical errors reach the user.** Expected problems produce
  friendly messages; unexpected ones produce a generic message while the
  full technical detail goes to the terminal log (app) or is available via
  `--debug` (command line). The command line also returns meaningful exit
  codes: 0 success, 1 file problem, 2 model/configuration problem,
  3 unexpected error.

## 7.8 Automated tests

`tests/test_prediction.py` — all passing:

| Test | Purpose |
|---|---|
| Successful prediction on a synthetic WAV | The whole path works and returns the required cautious wording |
| Inconclusive-band boundaries | 0.349 → HC, 0.35 / 0.50 / 0.65 → inconclusive, 0.651 → PD, no-score → fallback |
| Pipeline-config mismatch | A changed sample rate is refused |
| Missing pipeline-config file | Refused |
| Truncated feature list | Refused |
| Missing / empty / corrupted / silent / too-short audio | Each refused with a readable message |

`tests/test_pipeline.py` — verifies preprocessing and feature extraction
on a synthetic 150 Hz tone: pitch is tracked near 150 Hz, jitter and
shimmer are very low, HNR is high, feature order is stable, and no
unexpected missing values appear.

An end-to-end run on a real MDVR-KCL recording confirms the full path
works. **That run is a functional test only** — the file was in the
training data, so it is not evidence of accuracy.

## 7.9 Relevant files

| File | Purpose |
|---|---|
| `src/pvoice/predict.py` | Shared prediction logic, validation, config check, score interpretation |
| `app.py` | Streamlit browser interface |
| `scripts/predict_file.py` | Command-line interface |
| `tests/test_prediction.py` | Prediction-path tests |
| `tests/test_pipeline.py` | Pipeline self-test |
| `models/pipeline_config.json` | The compatibility contract |
| `reports/prototype_report.md` | The generated prototype report |
