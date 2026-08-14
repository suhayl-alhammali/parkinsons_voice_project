# Phase 5: file-based prototype report

**This is a research screening-support prototype and is not a medical
diagnostic tool. Its result must not replace evaluation by a qualified
healthcare professional.**

## What was built

Two entry points, both calling the exact same prediction function
(`pvoice.predict.predict_file`), which reuses the training pipeline
end-to-end (same preprocessing, same feature extraction, same ordered
feature list):

1. **Streamlit browser app** (`app.py`): select/upload a WAV file, see
   file information, the research classification, the model score, and the
   mandatory disclaimer. Started with `streamlit run app.py`.
2. **Command line** (`scripts/predict_file.py <file.wav>`): prints the same
   result as text; `--debug` adds technical details for troubleshooting.

## Prediction flow

1. `check_pipeline_config()` compares `models/pipeline_config.json`
   (written at training time) against the current code's settings: sample
   rate, trim threshold, pitch floor/ceiling, MFCC settings, and the full
   ordered feature list. Any difference, or a missing/unreadable file,
   aborts with a "retrain the model" message. This runs before EVERY
   prediction.
2. `validate_audio_file()` rejects unusable input with plain-language
   messages: missing file, empty (0-byte) file, unreadable/corrupted audio,
   file with no samples, recording shorter than 1 second, silent recording.
3. The standard pipeline runs: mono, 44.1 kHz, DC removal, edge silence
   trimming, peak normalization, then F0/jitter/shimmer/HNR (Praat) and
   MFCC statistics (librosa) — identical to training.
4. The saved SVM-RBF pipeline (median imputer + scaler + classifier)
   produces the class and a PD-class score.
5. Recordings much shorter than the ~2-minute training recordings get a
   reliability warning attached (threshold: 10 s).

## Safeguards in the interface

- The disclaimer above is shown prominently before and after every result,
  in both interfaces.
- Result wording: "The acoustic pattern was classified by the research
  model as closer to the PD class / HC class." The score is labeled "a
  property of the research model, NOT a person's medical risk".
- HC/PD are explained in plain language as similarity to dataset groups,
  explicitly not as presence/absence of disease.
- No tracebacks reach the user: expected problems show friendly messages;
  unexpected errors show a generic message while full details go to the
  terminal log (Streamlit) or `--debug` (CLI).
- Uploaded audio is written only to a temporary file that is deleted in a
  `finally` block immediately after processing — nothing is kept.
- The trained model was not modified and model selection was not repeated.

## Tests and verification

`tests/test_prediction.py` (run: `python tests/test_prediction.py`), all
passing:

| test | result |
|:--|:--|
| Successful prediction on valid synthetic WAV | PASS (label + score + wording verified) |
| Pipeline-config mismatch (changed sample rate) | PASS - refused with PipelineConfigError |
| Missing pipeline-config file | PASS - refused |
| Truncated feature list in config | PASS - refused |
| Missing / empty / corrupted / silent / too-short audio | PASS - each refused with a friendly message |

`tests/test_pipeline.py` (synthetic-tone pipeline self-check): still passes.

Functional end-to-end checks:

- CLI on one MDVR-KCL recording (`ReadText/HC/ID00_hc_0_0_0.wav`):
  completed the full pipeline and printed the cautious result block.
  **Note:** this file was part of training data; the run verifies only
  that the pipeline works, it is NOT evidence of accuracy.
- Streamlit app launched headless and inspected in a browser: page renders
  with the disclaimer banner, label explanation, and WAV-only uploader; no
  server errors. (The upload path itself is exercised by the automated
  tests, which call the same `predict_file` function the app calls.)

## Additions after the accuracy-improvement phase (2026-08-15)

- **Inconclusive band**: model scores in 0.35-0.65 are displayed as
  "the model could not clearly assign this recording to either class"
  instead of a hard HC/PD call. Rationale: near the decision boundary the
  evidence is weak, and out-of-domain recordings (other microphones,
  languages, rooms) often land exactly there; a hard label would
  overstate certainty. The out-of-fold score distribution shows the class
  overlap concentrated in this band (figures/score_distribution.png).
- **Recording-condition warnings** (never blocking): sample rate differs
  from training (resampled), audible clipping (>0.1% full-scale samples),
  low estimated signal-to-noise ratio (<15 dB), plus the existing
  short-recording warning.
- **Microphone mode** (approved by Hussein): the app can record directly.
  It is framed on-screen as an out-of-domain demonstration - the model
  was trained on one phone in one room, so live recordings mainly show
  the uncertainty handling. Recorded audio follows the exact same
  temporary-file path as uploads and is deleted after processing.
- Tests extended: uncertain-band boundary tests (0.349/0.35/0.5/0.65/
  0.651, and the no-score fallback) all pass.

## Limitations

- The model was trained on ~2-minute continuous-speech recordings from one
  dataset (one microphone setup per group, English speech). Short clips,
  other languages, phone recordings, or noisy rooms may behave differently;
  short recordings only get a warning, other mismatches are undetectable.
- The subject-level evaluation (Phase 4) applies to the dataset, not to any
  individual future user.
- WAV input only in the app (deliberate, to keep decoding predictable).
- Live microphone recording is out of scope (deferred per project rules).

## Files created or updated in Phase 5

- `src/pvoice/predict.py` - validation, config verification, cautious result
- `src/pvoice/config.py` - mandatory disclaimer + label explanation text
- `app.py` - completed Streamlit interface
- `scripts/predict_file.py` - completed CLI with exit codes and --debug
- `tests/test_prediction.py` - new prediction-path tests
- `README.md` - exact run instructions for the student
- `reports/prototype_report.md` - this report
