# 10. Repository structure and reproduction

## 10.1 Folder map

```
parkinsons_voice_project/
├── app.py                     Streamlit browser prototype
├── requirements.txt           Python dependencies
├── README.md                  Setup, results summary, run commands
├── CLAUDE.md                  The project's fixed rules and constraints
│
├── src/pvoice/                Reusable pipeline code (the heart)
│   ├── config.py              EVERY setting lives here
│   ├── dataset.py             File discovery, labels, subject IDs
│   ├── preprocess.py          Audio conditioning + chunk splitting
│   ├── features.py            All 74 feature computations
│   ├── modeling.py            Model definitions
│   ├── evaluate.py            Grouped validation + metrics
│   └── predict.py             Single-file prediction + safety checks
│
├── scripts/                   One script per pipeline stage
├── tests/                     Automated tests
├── docs/                      This documentation set
├── reports/                   All generated reports and figures
├── models/                    Trained model + pipeline configuration
├── data/
│   ├── raw/mdvr_kcl/          Training dataset (NOT in git)
│   ├── raw/italian_pvs/       External test dataset (NOT in git)
│   └── processed/             Generated feature tables and caches
└── prompts/                   Prompts used with AI assistants
```

## 10.2 What each script does

| Script | Purpose | Approx. runtime |
|---|---|---|
| `inspect_dataset.py` | Inspects MDVR-KCL, writes `dataset_report.md` | seconds |
| `build_features.py` | 43 features per whole recording → `features.csv` | ~12 min |
| `validate_features.py` | Quality checks → `feature_report.md` | seconds |
| `train_models.py` | Phase 4 baseline evaluation → `metrics_report.md` | ~2 min |
| `build_segment_features.py` | 74 features per 10-s chunk → `segment_features.csv` | ~32 min |
| `run_experiments.py` | The 19-configuration study → `experiments_report.md` | ~30 min |
| `train_final_model.py` | Trains and saves the final model | ~1 min |
| `make_figures.py` | All report figures | ~2 min |
| `inspect_italian_dataset.py` | Inspects the external dataset | ~1 min |
| `evaluate_external.py` | Frozen-model external validation | ~75 min |
| `predict_file.py` | Command-line prediction for one file | ~1 min |

The long feature-extraction scripts **cache their results per file**
(`data/processed/*_cache/`). If a run is interrupted, simply run it again
and it resumes. Delete a cache folder to force full re-extraction after
changing pipeline settings.

## 10.3 Reproducing everything from scratch

All commands run in the project folder with the virtual environment
active. Activate it first:

```bash
.venv\Scripts\activate
```

The prompt should then start with `(.venv)`.

**Step 1 — install dependencies**

```bash
pip install -r requirements.txt
```

**Step 2 — place the dataset**

Download MDVR-KCL from https://zenodo.org/record/2867216 and extract it
into `data/raw/mdvr_kcl/` (see the README file in that folder).

**Step 3 — verify the pipeline works**

```bash
python tests/test_pipeline.py
```

Expected: `All tests passed.`

**Step 4 — inspect the dataset**

```bash
python scripts/inspect_dataset.py
```

**Step 5 — extract chunk features (the long step)**

```bash
python scripts/build_segment_features.py
```

**Step 6 — train and save the final model**

```bash
python scripts/train_final_model.py
```

**Step 7 — generate figures**

```bash
python scripts/make_figures.py
```

**Step 8 — run the prototype**

```bash
streamlit run app.py
```

Optional: `build_features.py` + `validate_features.py` + `train_models.py`
reproduce the Phase 3–4 baseline; `run_experiments.py` reproduces the
19-configuration study; `inspect_italian_dataset.py` +
`evaluate_external.py` reproduce the external validation (requires
downloading the Italian dataset first).

## 10.4 Generated outputs

| File | Contents |
|---|---|
| `data/processed/features.csv` | 73 recordings × 43 features |
| `data/processed/segment_features.csv` | 1001 chunks × 74 features |
| `data/processed/oof_predictions.csv` | Phase 4 out-of-fold predictions (all models) |
| `data/processed/final_oof_predictions.csv` | Final model out-of-fold predictions |
| `data/processed/external_predictions.csv` | Italian dataset predictions |
| `models/model.joblib` | The trained final model |
| `models/pipeline_config.json` | The pipeline compatibility contract |

## 10.5 The figures

| Figure | Shows |
|---|---|
| `validation_comparison.png` | Correct grouped split (0.775) vs leaky chunk split (0.909) |
| `feature_importance.png` | The 15 most important features |
| `roc_curve.png` | ROC at recording and subject level |
| `score_distribution.png` | Score histograms per class with the inconclusive band |
| `external_scores.png` | All 61 Italian speakers' scores by group |
| `confusion_*.png` | Confusion matrices for each Phase 4 model |

## 10.6 Version control

Repository: **https://github.com/suhayl-alhammali/parkinsons_voice_project**

Committed: all code, tests, documentation, reports, figures, the pipeline
configuration, and the dependency list.

Deliberately **not** committed (via `.gitignore`): the audio datasets
(large, own licences), the virtual environment, feature caches, generated
CSV tables, and trained model binaries — all regenerable from the scripts
above.

This means anyone can clone the repository and reproduce every number from
scratch, which is itself a contribution worth stating in the report.

## 10.7 Environment notes

- Python 3.14.5 in a project-local virtual environment (`.venv`); no
  global installs.
- Key libraries: `praat-parselmouth` (F0, jitter, shimmer, HNR, CPPS),
  `librosa` (MFCC, resampling, silence detection), `scikit-learn`
  (models, validation), `pandas`/`numpy` (tables and maths),
  `matplotlib` (figures), `streamlit` (interface), `soundfile` (audio
  input/output), `huggingface_hub` (external dataset download).
- Streamlit telemetry is disabled via `.streamlit/config.toml`.
- A known harmless warning: scikit-learn 1.9 deprecates
  `SVC(probability=True)`. It does not affect results; if scikit-learn is
  upgraded to 1.11, switch to `CalibratedClassifierCV`.
