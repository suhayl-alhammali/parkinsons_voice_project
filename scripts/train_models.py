"""Train and evaluate all models with subject-independent validation (Phase 4).

Where to run:  project folder, with .venv activated
Command:       python scripts/train_models.py

What it does:
1. Loads data/processed/features.csv (run scripts/build_features.py first).
2. Runs sanity checks on labels and subject grouping.
3. Cross-validates a majority-class baseline plus 4 models with
   StratifiedGroupKFold (groups = subject_id, 5 folds).
4. Saves all out-of-fold predictions to data/processed/oof_predictions.csv.
5. Reports recording-level AND subject-level metrics, per fold and pooled.
6. Runs a confounder check: performance without absolute-F0 features and
   per-task performance.
7. Writes reports/metrics_report.md + confusion matrix figures.
8. Refits the selected model on ALL data and saves it to models/.

Model selection rule (documented in the report): highest robust score
    score = mean balanced accuracy across folds - 1 x std across folds
at recording level.  Balanced accuracy is used because classes are
imbalanced (42 HC vs 31 PD recordings); subtracting the std prefers models
that are stable across folds, not just good on average.  Ties are broken by
mean ROC-AUC.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pvoice import config
from pvoice.evaluate import (
    METRIC_NAMES,
    check_grouping,
    compute_metrics,
    cross_validate_grouped,
    fold_metric_table,
    overall_metrics,
    subject_level_oof,
)
# This script reproduces the PHASE 4 baseline evaluation (43 base features,
# recording-level).  The production model is trained by
# scripts/train_final_model.py; this script must not touch its artifacts.
from pvoice.features import base_feature_names as feature_names
from pvoice.modeling import build_models
from pvoice.predict import current_pipeline_config

OOF_PATH = config.PROCESSED_DATA_DIR / "oof_predictions.csv"
REPORT_PATH = config.REPORTS_DIR / "metrics_report.md"

# Absolute-pitch features carry speaker sex information (male vs female F0
# ranges).  MDVR-KCL ships no per-subject sex metadata we could verify, so
# instead we measure how much performance depends on these features.
ABSOLUTE_F0_FEATURES = ["f0_mean_hz", "f0_median_hz", "f0_min_hz", "f0_max_hz"]

SUSPICIOUS_THRESHOLD = 0.95


def run_all_models(X, y, groups, meta) -> dict[str, pd.DataFrame]:
    """Cross-validate every model; returns model name -> OOF table."""
    oofs = {}
    for name, pipeline in build_models().items():
        print(f"Cross-validating {name}...")
        oofs[name] = cross_validate_grouped(name, pipeline, X, y, groups, meta)
        pooled = overall_metrics(oofs[name])
        print(f"  balanced accuracy {pooled['balanced_accuracy']:.3f} | "
              f"ROC-AUC {pooled['roc_auc']:.3f}")
    return oofs


def selection_score(fold_table: pd.DataFrame) -> float:
    """Robust selection score: mean balanced accuracy minus its std."""
    return float(fold_table["balanced_accuracy"].mean()
                 - fold_table["balanced_accuracy"].std(ddof=0))


def fmt_mean_std(values: pd.Series) -> str:
    return f"{values.mean():.3f} +/- {values.std(ddof=0):.3f}"


def confusion_from(oof: pd.DataFrame) -> np.ndarray:
    from sklearn.metrics import confusion_matrix
    return confusion_matrix(oof["y_true"], oof["y_pred"],
                            labels=[config.LABEL_HC, config.LABEL_PD])


def save_confusion_figure(matrix: np.ndarray, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(matrix, cmap="Blues")
    for (i, j), value in np.ndenumerate(matrix):
        ax.text(j, i, str(value), ha="center", va="center")
    ax.set_xticks([0, 1], ["HC", "PD"])
    ax.set_yticks([0, 1], ["HC", "PD"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> int:
    if not config.FEATURE_TABLE_PATH.exists():
        print(f"Feature table not found: {config.FEATURE_TABLE_PATH}")
        print("Run: python scripts/build_features.py")
        return 1

    table = pd.read_csv(config.FEATURE_TABLE_PATH)
    X = table[feature_names()]
    y = table["label"]
    groups = table["subject_id"]
    meta = table[["task", "relative_path"]]

    problems = check_grouping(groups, y)
    if problems:
        print("STOP: grouping problems detected. Do not train until resolved:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    # ------------------------------------------------------------------
    # Main evaluation
    # ------------------------------------------------------------------
    oofs = run_all_models(X, y, groups, meta)

    all_oof = pd.concat(oofs.values(), ignore_index=True)
    config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    all_oof.to_csv(OOF_PATH, index=False)
    print(f"Saved out-of-fold predictions: {OOF_PATH}")

    # ------------------------------------------------------------------
    # Confounder check 1: drop absolute-F0 features, re-run real models.
    # ------------------------------------------------------------------
    reduced_features = [f for f in feature_names()
                        if f not in ABSOLUTE_F0_FEATURES]
    print("\nConfounder check: repeating CV without absolute-F0 features "
          f"({', '.join(ABSOLUTE_F0_FEATURES)})...")
    ablation_pooled = {}
    for name, pipeline in build_models().items():
        if name == "baseline_majority":
            continue
        oof_reduced = cross_validate_grouped(
            name, pipeline, X[reduced_features], y, groups, meta)
        ablation_pooled[name] = overall_metrics(oof_reduced)

    # ------------------------------------------------------------------
    # Model selection (baseline excluded)
    # ------------------------------------------------------------------
    fold_tables = {name: fold_metric_table(oof) for name, oof in oofs.items()}
    candidates = {n: selection_score(t) for n, t in fold_tables.items()
                  if n != "baseline_majority"}
    auc_means = {n: fold_tables[n]["roc_auc"].mean() for n in candidates}
    best_name = max(candidates,
                    key=lambda n: (round(candidates[n], 6), auc_means[n]))
    print(f"\nSelected model: {best_name} "
          f"(robust score {candidates[best_name]:.3f})")

    # ------------------------------------------------------------------
    # Suspicious-result rule (>= 95% on any headline metric, any model)
    # ------------------------------------------------------------------
    suspicious = []
    for name, oof in oofs.items():
        if name == "baseline_majority":
            continue
        pooled = overall_metrics(oof)
        subj = subject_level_oof(oof)
        subj_pooled = compute_metrics(subj["y_true"].to_numpy(),
                                      subj["y_pred"].to_numpy(),
                                      subj["prob_pd"].to_numpy())
        for level, metrics in (("recording", pooled), ("subject", subj_pooled)):
            for metric in ("accuracy", "balanced_accuracy", "roc_auc"):
                if metrics[metric] >= SUSPICIOUS_THRESHOLD:
                    suspicious.append(
                        f"{name}: {level}-level {metric} = "
                        f"{metrics[metric]:.3f} >= {SUSPICIOUS_THRESHOLD}")
    if suspicious:
        print("\nWARNING - suspiciously high results (project rule: "
              "investigate before trusting):")
        for s in suspicious:
            print(f"  {s}")

    # ------------------------------------------------------------------
    # Report + artifacts
    # ------------------------------------------------------------------
    write_report(table, oofs, fold_tables, ablation_pooled, candidates,
                 auc_means, best_name, suspicious)

    # Save under a phase4_ prefix so the production artifacts written by
    # train_final_model.py are never overwritten by this baseline script.
    best_pipeline = build_models()[best_name]
    best_pipeline.fit(X, y)
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    phase4_model = config.MODELS_DIR / "phase4_model.joblib"
    phase4_config = config.MODELS_DIR / "phase4_pipeline_config.json"
    joblib.dump(best_pipeline, phase4_model)
    saved_config = {**current_pipeline_config(), "model_name": best_name,
                    "feature_set": "base",
                    "feature_names": feature_names()}
    phase4_config.write_text(json.dumps(saved_config, indent=2))
    print(f"Saved Phase 4 baseline model: {phase4_model}")
    print(f"Saved pipeline config: {phase4_config}")
    return 0


def write_report(table, oofs, fold_tables, ablation_pooled, candidates,
                 auc_means, best_name, suspicious) -> None:
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    add = lines.append

    add("# Phase 4: model evaluation report")
    add("")
    add("**This is a research screening-support prototype. It is not a "
        "medical diagnostic system, and none of the numbers below are "
        "claims of diagnostic performance.**")
    add("")

    add("## Evaluation design and leakage safeguards")
    add("")
    add(f"- Data: {len(table)} recordings, "
        f"{table['subject_id'].nunique()} subjects "
        f"(HC {int((table['label'] == 0).sum())} recordings / "
        f"PD {int((table['label'] == 1).sum())} recordings).")
    add(f"- Validation: StratifiedGroupKFold, {config.N_SPLITS} folds, "
        "groups = subject_id, shuffled with fixed random seed "
        f"({config.RANDOM_STATE}).")
    add("- No subject ever appears in both training and test of a fold; a "
        "hard runtime assertion re-checks every fold and aborts on overlap "
        "(it never triggered).")
    add("- Imputation (median) and scaling are steps INSIDE each model "
        "pipeline, so they are re-fit on the training part of every fold "
        "only. No preprocessing was fit on the full dataset before CV. No "
        "feature selection was performed on the full dataset.")
    add("- Every recording is predicted exactly once, by a model that never "
        "saw that subject. All metrics below are computed from these "
        "out-of-fold predictions "
        f"(saved with subject IDs to `{OOF_PATH.name}`).")
    add("- Subject-level prediction rule: mean of the subject's "
        "recording-level PD probabilities, class = PD if mean >= 0.5.")
    add("")

    add("## Results per model")
    add("")
    for name, oof in oofs.items():
        ft = fold_tables[name]
        subj = subject_level_oof(oof)
        subj_metrics = compute_metrics(subj["y_true"].to_numpy(),
                                       subj["y_pred"].to_numpy(),
                                       subj["prob_pd"].to_numpy())
        add(f"### {name}")
        add("")
        add("| metric | per-fold mean +/- std | pooled recording-level | subject-level |")
        add("|:--|:--|--:|--:|")
        pooled = overall_metrics(oof)
        for metric in METRIC_NAMES:
            add(f"| {metric} | {fmt_mean_std(ft[metric])} "
                f"| {pooled[metric]:.3f} | {subj_metrics[metric]:.3f} |")
        add("")
        add("Per-fold balanced accuracy: "
            + ", ".join(f"{v:.3f}" for v in ft["balanced_accuracy"]))
        add("")
        rec_cm = confusion_from(oof)
        subj_cm = confusion_from(subj)
        add("Pooled confusion matrices (rows = true HC, PD; "
            "cols = predicted HC, PD):")
        add("")
        add("```")
        add(f"recording level:      subject level:")
        for i in range(2):
            add(f"  {rec_cm[i][0]:3d} {rec_cm[i][1]:3d}             "
                f"  {subj_cm[i][0]:3d} {subj_cm[i][1]:3d}")
        add("```")
        add("")
        save_confusion_figure(
            rec_cm, f"{name} (recording level)",
            config.FIGURES_DIR / f"confusion_{name}.png")

    add("## Baseline comparison")
    add("")
    base = overall_metrics(oofs["baseline_majority"])
    add(f"The majority-class baseline (always predicts HC) reaches "
        f"accuracy {base['accuracy']:.3f} but balanced accuracy "
        f"{base['balanced_accuracy']:.3f} and sensitivity for PD "
        f"{base['sensitivity_pd']:.3f}: it never finds a PD case. Any "
        "useful model must clearly beat 0.5 balanced accuracy; comparisons "
        "above use balanced accuracy for exactly this reason.")
    add("")

    add("## Model selection")
    add("")
    add("Rule: highest robust score = (mean balanced accuracy across folds) "
        "- (std across folds), recording level; ties broken by mean "
        "ROC-AUC. The std penalty prefers models that are stable across "
        "folds rather than occasionally lucky.")
    add("")
    add("| model | robust score | mean ROC-AUC |")
    add("|:--|--:|--:|")
    for name, score in sorted(candidates.items(), key=lambda kv: -kv[1]):
        add(f"| {name} | {score:.3f} | {auc_means[name]:.3f} |")
    add("")
    add(f"**Selected model: {best_name}**. It was refit on all 73 "
        "recordings and saved for the Phase 5 prototype.")
    add("")

    add("## Confounder and task analysis")
    add("")
    add("### Absolute F0 and (unrecorded) speaker sex")
    add("")
    add("MDVR-KCL provides no verified per-subject sex/age metadata in the "
        "audio distribution, so a direct check of group composition is not "
        "possible without guessing - which we do not do. Absolute pitch "
        "features (F0 mean/median/min/max) are the features most likely to "
        "encode speaker sex. The HC group's mean F0 is ~180 Hz vs ~154 Hz "
        "for PD, a difference more plausibly explained by group composition "
        "than by disease. To measure how much the models depend on this, "
        "CV was repeated without those 4 features:")
    add("")
    add("| model | balanced accuracy (all features) | balanced accuracy "
        "(without absolute F0) |")
    add("|:--|--:|--:|")
    for name, metrics in ablation_pooled.items():
        full = overall_metrics(oofs[name])
        add(f"| {name} | {full['balanced_accuracy']:.3f} "
            f"| {metrics['balanced_accuracy']:.3f} |")
    add("")
    add("If performance collapses without absolute F0, the models were "
        "leaning on a potential sex confound; if it holds, the "
        "perturbation/MFCC features carry the real signal.")
    add("")

    add("### Performance by task")
    add("")
    add("Recording-level accuracy of each model split by task "
        "(from the same OOF predictions):")
    add("")
    add("| model | ReadText | SpontaneousDialogue |")
    add("|:--|--:|--:|")
    for name, oof in oofs.items():
        parts = []
        for task in ("ReadText", "SpontaneousDialogue"):
            sub = oof[oof["task"] == task]
            parts.append(f"{(sub['y_true'] == sub['y_pred']).mean():.3f}")
        add(f"| {name} | {parts[0]} | {parts[1]} |")
    add("")

    add("## Warnings and suspicious results")
    add("")
    if suspicious:
        add("**The following results reached the >= 95% suspicion "
            "threshold and must be reviewed (project rule) before being "
            "presented as success:**")
        for s in suspicious:
            add(f"- {s}")
    else:
        add("No model reached the 95% suspicion threshold on accuracy, "
            "balanced accuracy, or ROC-AUC.")
    add("")

    add("## Limitations")
    add("")
    add("- 37 subjects is small; fold-to-fold variation above is large and "
        "any single headline number should be read with its std.")
    add("- Recording conditions are homogeneous per class group; results "
        "may not transfer to other microphones, rooms, or languages.")
    add("- Continuous speech makes jitter/shimmer/HNR noisier than "
        "sustained-vowel protocols.")
    add("- Speaker sex/age are not available, so demographic confounding "
        "cannot be fully excluded - only bounded by the ablation above.")
    add("- This is a research screening prototype; it must not be used for "
        "medical decisions.")
    add("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    raise SystemExit(main())
