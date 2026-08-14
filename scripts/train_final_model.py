"""Train and save the FINAL model chosen by the accuracy experiments.

Where to run:  project folder, with .venv activated
Command:       python scripts/train_final_model.py

Winning configuration (see reports/experiments_report.md):
- Features: extended set (74) extracted per 10-s chunk, averaged per
  recording ("chunk_feature_mean") - variant V1.
- Model: Random Forest, default project settings (tuning and ensembling
  did not beat it by the pre-declared margin).

This script:
1. Rebuilds the recording-level table from segment_features.csv.
2. Re-runs the fixed 3-seed subject-independent evaluation for the final
   configuration and writes reports/final_model_report.md (with confusion
   matrix and OOF predictions for seed 42).
3. Refits on all data and saves models/model.joblib +
   models/pipeline_config.json (now including segmentation settings).
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

warnings.filterwarnings("ignore", category=FutureWarning,
                        module="sklearn.svm._base")

import joblib
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from pvoice import config
from pvoice.evaluate import compute_metrics
from pvoice.features import extended_feature_names, feature_names
from pvoice.predict import current_pipeline_config

SEGMENT_TABLE = config.PROCESSED_DATA_DIR / "segment_features.csv"
FINAL_OOF_PATH = config.PROCESSED_DATA_DIR / "final_oof_predictions.csv"
REPORT_PATH = config.REPORTS_DIR / "final_model_report.md"
SEEDS = [42, 7, 2025]
MODEL_NAME = "random_forest_extended_chunkmean"


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=300, class_weight="balanced",
            random_state=config.RANDOM_STATE)),
    ])


def recording_table() -> pd.DataFrame:
    seg = pd.read_csv(SEGMENT_TABLE)
    agg = {f: (f, "mean") for f in extended_feature_names()}
    return (seg.groupby("relative_path")
            .agg(subject_id=("subject_id", "first"),
                 label=("label", "first"),
                 task=("task", "first"), **agg)
            .reset_index())


def main() -> int:
    if not SEGMENT_TABLE.exists():
        print(f"Chunk table not found: {SEGMENT_TABLE}")
        print("Run: python scripts/build_segment_features.py")
        return 1
    assert config.FEATURE_SET == "extended", "config.FEATURE_SET must be extended"

    rec = recording_table()
    X = rec[feature_names()]
    y = rec["label"]
    groups = rec["subject_id"]

    per_seed = []
    oof_seed42 = None
    for seed in SEEDS:
        sgkf = StratifiedGroupKFold(n_splits=config.N_SPLITS, shuffle=True,
                                    random_state=seed)
        oof = rec[["relative_path", "subject_id", "task", "label"]].copy()
        oof["prob_pd"] = np.nan
        oof["fold"] = -1
        for fold, (tr, te) in enumerate(sgkf.split(X, y, groups=groups)):
            overlap = set(groups.iloc[tr]) & set(groups.iloc[te])
            if overlap:
                raise RuntimeError(f"LEAKAGE: {overlap}")
            model = build_pipeline()
            model.fit(X.iloc[tr], y.iloc[tr])
            oof.iloc[te, oof.columns.get_loc("prob_pd")] = (
                model.predict_proba(X.iloc[te])[:, 1])
            oof.iloc[te, oof.columns.get_loc("fold")] = fold
        oof["y_pred"] = (oof["prob_pd"] >= 0.5).astype(int)
        rec_metrics = compute_metrics(oof["label"].to_numpy(),
                                      oof["y_pred"].to_numpy(),
                                      oof["prob_pd"].to_numpy())
        subj = (oof.groupby("subject_id")
                .agg(label=("label", "first"), prob_pd=("prob_pd", "mean"))
                .reset_index())
        subj["y_pred"] = (subj["prob_pd"] >= 0.5).astype(int)
        subj_metrics = compute_metrics(subj["label"].to_numpy(),
                                       subj["y_pred"].to_numpy(),
                                       subj["prob_pd"].to_numpy())
        per_seed.append((seed, rec_metrics, subj_metrics))
        if seed == 42:
            oof_seed42 = oof

    config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    oof_seed42.to_csv(FINAL_OOF_PATH, index=False)

    write_report(rec, per_seed, oof_seed42)

    final_model = build_pipeline()
    final_model.fit(X, y)
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, config.MODEL_FILE)
    config.PIPELINE_CONFIG_FILE.write_text(
        json.dumps({**current_pipeline_config(), "model_name": MODEL_NAME},
                   indent=2))
    print(f"Saved final model: {config.MODEL_FILE}")
    print(f"Saved pipeline config: {config.PIPELINE_CONFIG_FILE}")
    return 0


def write_report(rec, per_seed, oof_seed42) -> None:
    from sklearn.metrics import confusion_matrix

    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Final model report (after accuracy-improvement experiments)",
        "",
        "**Research screening-support prototype - not a medical "
        "diagnostic system.**",
        "",
        f"- Model: Random Forest (300 trees, balanced class weights, "
        f"default depth), pipeline = median imputer + standard scaler + RF.",
        "- Features: 74 extended features (F0, jitter, shimmer, HNR, CPPS, "
        "pause statistics, MFCC + delta-MFCC summary) extracted per 10-s "
        "chunk and averaged per recording.",
        f"- Data: {len(rec)} recordings, {rec['subject_id'].nunique()} "
        "subjects.",
        "- Validation: StratifiedGroupKFold (5 folds, subject groups), "
        "3 seeds; identical protocol to the experiments that selected this "
        "configuration.",
        "",
        "| seed | recording bal.acc | subject bal.acc | subject sens. | "
        "subject spec. | subject ROC-AUC |",
        "|--:|--:|--:|--:|--:|--:|",
    ]
    for seed, rm, sm in per_seed:
        lines.append(f"| {seed} | {rm['balanced_accuracy']:.3f} "
                     f"| {sm['balanced_accuracy']:.3f} "
                     f"| {sm['sensitivity_pd']:.3f} "
                     f"| {sm['specificity_hc']:.3f} "
                     f"| {sm['roc_auc']:.3f} |")
    sub_means = np.mean([[sm["balanced_accuracy"], sm["sensitivity_pd"],
                          sm["specificity_hc"], sm["roc_auc"]]
                         for _, _, sm in per_seed], axis=0)
    lines += ["",
              f"Mean subject-level: balanced accuracy {sub_means[0]:.3f}, "
              f"sensitivity {sub_means[1]:.3f}, specificity {sub_means[2]:.3f}, "
              f"ROC-AUC {sub_means[3]:.3f}.",
              ""]

    cm = confusion_matrix(oof_seed42["label"], oof_seed42["y_pred"],
                          labels=[config.LABEL_HC, config.LABEL_PD])
    lines += ["Recording-level confusion matrix (seed 42; rows = true "
              "HC, PD; cols = predicted HC, PD):", "", "```",
              str(cm), "```", "",
              f"Out-of-fold predictions (seed 42): `{FINAL_OOF_PATH.name}`.",
              "",
              "Improvement over Phase 4 (same protocol): subject-level "
              "balanced accuracy 0.780 -> 0.822 (+0.042), driven by the "
              "extended features (CPPS, pauses, delta-MFCC) computed on "
              "10-s chunks and averaged. Hyperparameter tuning, ensembling "
              "and mean+std summaries did not beat this by the "
              "pre-declared +0.02 margin and were rejected to limit "
              "overfitting risk (see experiments_report.md).",
              ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    raise SystemExit(main())
