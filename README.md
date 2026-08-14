# Voice Signal Analysis for Early Detection of Parkinson's Disease

Biomedical engineering graduation project. The system analyzes raw voice
recordings, extracts acoustic features (F0, jitter, shimmer, HNR, CPPS,
pause statistics, MFCC + delta-MFCC), trains classical machine learning
models with subject-independent validation, and provides a screening
prototype (browser app + command line).

> **Important:** This is a research screening prototype. It does **not**
> diagnose Parkinson's disease. Any result requires clinical evaluation.

## Results (subject-independent validation)

Final model: Random Forest on 74 acoustic features extracted per
10-second chunk and averaged per recording. Evaluated with
StratifiedGroupKFold (5 folds, grouped by subject, 3 seeds) on MDVR-KCL
(73 recordings, 37 subjects) — recordings of the same person are never
split between training and test:

| level | balanced accuracy | sensitivity (PD) | specificity (HC) | ROC-AUC |
|:--|--:|--:|--:|--:|
| per recording | 0.806 ± 0.013 | — | — | 0.86 |
| per subject | 0.822 ± 0.032 | 0.77 | 0.87 | 0.864 |

With a deliberately wrong split (random 10-s chunks, same recording in
train and test) the same pipeline reports 0.909 — a +0.13 inflation from
memorization. This is why grouped validation is non-negotiable
(`reports/figures/validation_comparison.png`).

Details: [reports/final_model_report.md](reports/final_model_report.md),
[reports/experiments_report.md](reports/experiments_report.md),
[reports/methodology.md](reports/methodology.md).

## Project structure

```
parkinsons_voice_project/
├── app.py                  # Streamlit prototype (Phase 5)
├── requirements.txt        # Python dependencies
├── data/
│   ├── raw/mdvr_kcl/       # <- place the MDVR-KCL dataset here
│   └── processed/          # generated feature tables and indexes
├── models/                 # saved trained models
├── reports/                # generated reports and figures
├── scripts/
│   ├── inspect_dataset.py  # Phase 2: dataset inspection report
│   ├── build_features.py   # Phase 3: build the feature table
│   ├── train_models.py     # Phase 4: train + evaluate models
│   └── predict_file.py     # Phase 5: command-line prediction
├── src/pvoice/             # reusable pipeline code (config, preprocessing,
│                           #   features, models, evaluation, prediction)
└── tests/                  # pipeline self-checks (no dataset needed)
```

## Setup (one time)

All commands are run **inside the project folder**, in a terminal
(PowerShell on Windows).

1. Create the virtual environment (already done if `.venv` exists):

   ```
   python -m venv .venv
   ```

2. Activate it (do this every time you open a new terminal):

   ```
   .venv\Scripts\activate
   ```

   Success looks like: the prompt now starts with `(.venv)`.

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

   Success looks like: it ends with `Successfully installed ...`.
   If it fails, copy the full output into ChatGPT.

4. Check the pipeline works (uses a synthetic tone, no dataset needed):

   ```
   python tests/test_pipeline.py
   ```

   Success looks like: `All tests passed.`

## Dataset

The project uses the **MDVR-KCL** dataset (Mobile Device Voice Recordings
at King's College London): voice recordings of people with Parkinson's
disease (PD) and healthy controls (HC).

Place the extracted dataset inside `data/raw/mdvr_kcl/`.
Detailed instructions: `data/raw/mdvr_kcl/README_PLACE_DATASET_HERE.txt`.

Then run the inspection:

```
python scripts/inspect_dataset.py
```

This writes `reports/dataset_report.md` — read it (or paste it into
ChatGPT) before continuing to feature extraction.

## Pipeline (run in order)

| Step | Command | Output |
|------|---------|--------|
| Inspect dataset | `python scripts/inspect_dataset.py` | `reports/dataset_report.md` |
| Extract features | `python scripts/build_features.py` | `data/processed/features.csv` |
| Validate features | `python scripts/validate_features.py` | `reports/feature_report.md` |
| Phase 4 baseline eval | `python scripts/train_models.py` | `reports/metrics_report.md`, `models/phase4_model.joblib` |
| Chunk features | `python scripts/build_segment_features.py` | `data/processed/segment_features.csv` |
| Experiments | `python scripts/run_experiments.py` | `reports/experiments_report.md` |
| **Train final model** | `python scripts/train_final_model.py` | `reports/final_model_report.md`, `models/model.joblib` |
| Report figures | `python scripts/make_figures.py` | `reports/figures/*.png` |
| Predict (CLI) | `python scripts/predict_file.py path\to\file.wav` | printed result |
| Prototype app | `streamlit run app.py` | browser app |

## Running the prototype (Phase 5)

All commands below are typed **in the project folder**, with the virtual
environment active (the prompt starts with `(.venv)` — if not, run
`.venv\Scripts\activate` first). The trained model must already exist
(`models\model.joblib`); if it does not, run the pipeline steps above first.

**Browser app (recommended for the demonstration):**

```
streamlit run app.py
```

Success looks like: the terminal prints `Local URL: http://localhost:...`
and a browser page opens. Two input modes:

- **Upload a WAV file** — choose a file with the **Browse files** button.
- **Record with the microphone** — for demonstrations. The app clearly
  warns that microphone conditions differ from the training data, so this
  mode mainly shows how the system handles unfamiliar recordings.

Analysis takes about 1 minute for a 2-minute recording. Scores between
0.35 and 0.65 are reported as **inconclusive** instead of a class label,
and the app warns about short, noisy, clipped, or resampled recordings.
To stop the app, press `Ctrl+C` in the terminal.

**Command line:**

```
python scripts\predict_file.py "data\raw\mdvr_kcl\ReadText\HC\ID00_hc_0_0_0.wav"
```

Success looks like: a block starting with `RESEARCH MODEL RESULT
(non-diagnostic)`. You can replace the path with any WAV recording.
If a file cannot be analyzed, the message explains why in plain words;
add `--debug` to see technical details.

**Prediction tests:**

```
python tests\test_prediction.py
```

Success looks like: `All prediction tests passed.`

Uploaded files are analyzed in a temporary copy that is deleted right
after processing — the app keeps no audio.

## Methodology summary

- **Preprocessing:** mono, fixed 44.1 kHz sample rate, DC offset removal,
  silence trimming, peak normalization. No aggressive denoising (it would
  distort jitter/shimmer/HNR).
- **Features (final model):** each recording is split into 10-second
  chunks; per chunk we extract F0 statistics, jitter variants, shimmer
  variants, HNR, CPPS (Praat via Parselmouth), pause statistics, and
  MFCC + delta-MFCC mean/std (librosa) — 74 features, averaged over chunks
  into one vector per recording.
- **Models:** Logistic Regression, SVM (RBF), Random Forest, MLP compared;
  final model = Random Forest chosen by pre-declared subject-independent
  experiments (`reports/experiments_report.md`). All models are
  scikit-learn pipelines with median imputation and standard scaling.
- **Validation:** subject-independent GroupKFold — recordings from the same
  person are never split between training and testing. The code raises an
  error if this rule is ever violated.
- **Metrics:** accuracy, precision, recall, F1, confusion matrix, ROC-AUC,
  per-fold mean and standard deviation.

## Limitations

- Small, controlled research dataset — results may not generalize to other
  microphones, languages, or populations.
- Screening indication only; **not** a medical diagnosis.
