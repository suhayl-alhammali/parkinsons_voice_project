"""Accuracy-improvement experiments (pre-declared protocol).

Where to run:  project folder, with .venv activated
Command:       python scripts/run_experiments.py

Protocol, fixed BEFORE looking at any results (guards against overfitting
the model choice to the dataset):

- Validation: StratifiedGroupKFold, 5 folds, groups = subject_id, repeated
  with 3 seeds (42, 7, 2025).  All variants use the exact same splits.
- Primary metric: SUBJECT-level balanced accuracy, mean across seeds.
- Adoption rule: a more complex variant must beat the simpler one by more
  than 0.02 primary metric, otherwise the simpler variant is kept.
- Any result >= 0.95 stops the process for leakage investigation.
- The saved model in models/ is NOT touched by this script.

Variants:
  V0  recording-level, base 43 features, default models      (Phase 4 ref)
  V1  recording-level (chunk-mean features), extended 74
  V2  chunk-level, base 43, mean-prob aggregation
  V3  chunk-level, extended 74, mean-prob aggregation
  V4  best-of-V0..V3 + grouped nested hyperparameter tuning
  V5  V4's data + soft-voting ensemble of tuned SVM + RF

Models per variant: logistic regression, SVM-RBF, random forest (MLP was
dropped: it collapsed in the Phase 4 F0-ablation robustness check).
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# sklearn 1.9 deprecation notice about SVC(probability=True); noted in the
# project docs, irrelevant to results, and it floods multi-seed logs.
warnings.filterwarnings("ignore", category=FutureWarning,
                        module="sklearn.svm._base")

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, GroupKFold, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from pvoice import config
from pvoice.evaluate import compute_metrics
from pvoice.features import base_feature_names, extended_feature_names

SEEDS = [42, 7, 2025]
ADOPTION_MARGIN = 0.02
SUSPICIOUS = 0.95
SEGMENT_TABLE = config.PROCESSED_DATA_DIR / "segment_features.csv"
REPORT_PATH = config.REPORTS_DIR / "experiments_report.md"

SVM_GRID = {"clf__C": [0.1, 1, 10, 100],
            "clf__gamma": ["scale", 0.01, 0.001]}
RF_GRID = {"clf__max_depth": [None, 5, 10],
           "clf__max_features": ["sqrt", 0.3]}
LR_GRID = {"clf__C": [0.01, 0.1, 1, 10]}


def make_models(tuned: bool = False) -> dict:
    steps = [("imputer", SimpleImputer(strategy="median")),
             ("scaler", StandardScaler())]
    models = {
        "logistic_regression": (
            Pipeline(steps + [("clf", LogisticRegression(
                max_iter=5000, class_weight="balanced",
                random_state=config.RANDOM_STATE))]),
            LR_GRID),
        "svm_rbf": (
            Pipeline(steps + [("clf", SVC(
                kernel="rbf", probability=True, class_weight="balanced",
                random_state=config.RANDOM_STATE))]),
            SVM_GRID),
        "random_forest": (
            Pipeline(steps + [("clf", RandomForestClassifier(
                n_estimators=300, class_weight="balanced",
                random_state=config.RANDOM_STATE))]),
            RF_GRID),
    }
    if not tuned:
        return {name: pipe for name, (pipe, _grid) in models.items()}
    return models


def make_ensemble(tuned_params: dict) -> Pipeline:
    """Soft-voting ensemble of SVM and RF with fold-tuned parameters."""
    steps = [("imputer", SimpleImputer(strategy="median")),
             ("scaler", StandardScaler())]
    svm = SVC(kernel="rbf", probability=True, class_weight="balanced",
              random_state=config.RANDOM_STATE,
              **tuned_params.get("svm_rbf", {}))
    rf = RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                random_state=config.RANDOM_STATE,
                                **tuned_params.get("random_forest", {}))
    return Pipeline(steps + [("clf", VotingClassifier(
        estimators=[("svm", svm), ("rf", rf)], voting="soft"))])


def evaluate_variant(frame: pd.DataFrame, features: list[str],
                     model_factory, aggregate_chunks: bool) -> dict:
    """Run the fixed multi-seed protocol for one variant + one model.

    model_factory(train_groups, X_train, y_train) -> fitted-able pipeline;
    for tuned variants it runs grouped GridSearchCV inside the training
    fold only (nested tuning, no leakage).
    Returns per-seed subject-level and recording-level metrics.
    """
    per_seed = []
    for seed in SEEDS:
        sgkf = StratifiedGroupKFold(n_splits=config.N_SPLITS, shuffle=True,
                                    random_state=seed)
        X = frame[features]
        y = frame["label"]
        groups = frame["subject_id"]
        oof = frame[["subject_id", "relative_path", "label"]].copy()
        oof["prob_pd"] = np.nan

        for train_idx, test_idx in sgkf.split(X, y, groups=groups):
            train_subj = set(groups.iloc[train_idx])
            test_subj = set(groups.iloc[test_idx])
            if train_subj & test_subj:
                raise RuntimeError(f"LEAKAGE: {train_subj & test_subj}")
            model = model_factory(groups.iloc[train_idx],
                                  X.iloc[train_idx], y.iloc[train_idx])
            model.fit(X.iloc[train_idx], y.iloc[train_idx])
            oof.iloc[test_idx, oof.columns.get_loc("prob_pd")] = (
                model.predict_proba(X.iloc[test_idx])[:, 1])

        assert not oof["prob_pd"].isna().any()

        # Aggregate: chunks -> recording -> subject (mean of means), or
        # recording -> subject directly for recording-level variants.
        rec = (oof.groupby("relative_path")
                  .agg(subject_id=("subject_id", "first"),
                       label=("label", "first"),
                       prob_pd=("prob_pd", "mean"))
                  .reset_index()) if aggregate_chunks else oof
        rec_metrics = compute_metrics(
            rec["label"].to_numpy(),
            (rec["prob_pd"] >= 0.5).astype(int).to_numpy(),
            rec["prob_pd"].to_numpy())

        subj = (rec.groupby("subject_id")
                   .agg(label=("label", "first"), prob_pd=("prob_pd", "mean"))
                   .reset_index())
        subj_metrics = compute_metrics(
            subj["label"].to_numpy(),
            (subj["prob_pd"] >= 0.5).astype(int).to_numpy(),
            subj["prob_pd"].to_numpy())
        per_seed.append({"seed": seed, "recording": rec_metrics,
                         "subject": subj_metrics})
    return summarize_seeds(per_seed)


def summarize_seeds(per_seed: list[dict]) -> dict:
    out = {"per_seed": per_seed}
    for level in ("recording", "subject"):
        for metric in ("balanced_accuracy", "accuracy", "sensitivity_pd",
                       "specificity_hc", "f1", "roc_auc"):
            values = [s[level][metric] for s in per_seed]
            out[f"{level}_{metric}_mean"] = float(np.mean(values))
            out[f"{level}_{metric}_std"] = float(np.std(values))
    return out


def default_factory(pipeline):
    return lambda train_groups, X, y: pipeline


def tuned_factory(pipeline, grid):
    """Nested tuning: grouped 3-fold grid search INSIDE the training fold."""
    def factory(train_groups, X, y):
        inner = list(GroupKFold(n_splits=3).split(X, y, groups=train_groups))
        search = GridSearchCV(pipeline, grid, cv=inner,
                              scoring="balanced_accuracy", n_jobs=-1)
        search.fit(X, y)
        return search.best_estimator_
    return factory


def main() -> int:
    if not SEGMENT_TABLE.exists():
        print(f"Chunk table not found: {SEGMENT_TABLE}")
        print("Run: python scripts/build_segment_features.py")
        return 1

    rec_table = pd.read_csv(config.FEATURE_TABLE_PATH)      # Phase 3, 43 f.
    seg_table = pd.read_csv(SEGMENT_TABLE)                  # chunks, 74 f.

    # Recording-level table with extended features = mean over chunks.
    agg = {f: (f, "mean") for f in extended_feature_names()}
    rec_ext = (seg_table.groupby("relative_path")
               .agg(subject_id=("subject_id", "first"),
                    label=("label", "first"), **agg).reset_index())

    results: dict[str, dict] = {}

    def run(variant: str, frame, features, factory_map, aggregate):
        for model_name, factory in factory_map.items():
            key = f"{variant}/{model_name}"
            print(f"Running {key}...")
            results[key] = evaluate_variant(frame, features, factory,
                                            aggregate)
            m = results[key]
            print(f"  subject bal.acc {m['subject_balanced_accuracy_mean']:.3f} "
                  f"+/- {m['subject_balanced_accuracy_std']:.3f} | "
                  f"recording {m['recording_balanced_accuracy_mean']:.3f}")

    default_models = {n: default_factory(p)
                      for n, p in make_models(tuned=False).items()}

    run("V0_rec_base", rec_table, base_feature_names(), default_models, False)
    run("V1_rec_extended", rec_ext, extended_feature_names(), default_models,
        False)
    run("V2_chunk_base", seg_table, base_feature_names(), default_models,
        True)
    run("V3_chunk_extended", seg_table, extended_feature_names(),
        default_models, True)

    # Pick the best variant so far (primary metric) for tuning.
    def best_of(prefixes):
        keys = [k for k in results if any(k.startswith(p) for p in prefixes)]
        return max(keys,
                   key=lambda k: results[k]["subject_balanced_accuracy_mean"])

    best_untuned = best_of(["V0", "V1", "V2", "V3"])
    variant_name = best_untuned.split("/")[0]
    if variant_name in ("V2_chunk_base", "V3_chunk_extended"):
        tune_frame, aggregate = seg_table, True
        tune_features = (base_feature_names()
                         if variant_name == "V2_chunk_base"
                         else extended_feature_names())
    elif variant_name == "V1_rec_extended":
        tune_frame, aggregate = rec_ext, False
        tune_features = extended_feature_names()
    else:
        tune_frame, aggregate = rec_table, False
        tune_features = base_feature_names()
    print(f"\nBest untuned variant: {best_untuned} -> tuning on "
          f"{variant_name} data")

    tuned_models = {n: tuned_factory(p, g)
                    for n, (p, g) in make_models(tuned=True).items()}
    run("V4_tuned", tune_frame, tune_features, tuned_models, aggregate)

    # Ensemble: tune SVM and RF per fold, then soft-vote.
    def ensemble_factory(train_groups, X, y):
        inner = list(GroupKFold(n_splits=3).split(X, y, groups=train_groups))
        params = {}
        for name, (pipe, grid) in make_models(tuned=True).items():
            if name == "logistic_regression":
                continue
            search = GridSearchCV(pipe, grid, cv=inner,
                                  scoring="balanced_accuracy", n_jobs=-1)
            search.fit(X, y)
            params[name] = {k.replace("clf__", ""): v
                            for k, v in search.best_params_.items()}
        return make_ensemble(params)

    run("V5_ensemble", tune_frame, tune_features,
        {"svm_plus_rf": ensemble_factory}, aggregate)

    write_report(results, best_untuned)
    return 0


def write_report(results: dict, best_untuned: str) -> None:
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = ["# Accuracy-improvement experiments", "",
             "Protocol: StratifiedGroupKFold (5 folds, subject groups), "
             "3 seeds; primary metric = subject-level balanced accuracy "
             "(mean +/- std across seeds). Adoption needs > "
             f"{ADOPTION_MARGIN} improvement over the simpler variant. "
             "The saved production model is unchanged by this script.", "",
             "| variant/model | subject bal.acc | recording bal.acc | "
             "subject AUC | subject sens. | subject spec. |",
             "|:--|--:|--:|--:|--:|--:|"]
    for key, m in results.items():
        lines.append(
            f"| {key} "
            f"| {m['subject_balanced_accuracy_mean']:.3f} +/- "
            f"{m['subject_balanced_accuracy_std']:.3f} "
            f"| {m['recording_balanced_accuracy_mean']:.3f} +/- "
            f"{m['recording_balanced_accuracy_std']:.3f} "
            f"| {m['subject_roc_auc_mean']:.3f} "
            f"| {m['subject_sensitivity_pd_mean']:.3f} "
            f"| {m['subject_specificity_hc_mean']:.3f} |")
    lines += ["", f"Best untuned variant: **{best_untuned}**", ""]
    suspicious = [k for k, m in results.items()
                  if m["subject_balanced_accuracy_mean"] >= SUSPICIOUS
                  or m["recording_balanced_accuracy_mean"] >= SUSPICIOUS]
    if suspicious:
        lines += ["**SUSPICIOUS (>= 0.95) - investigate before use:** "
                  + ", ".join(suspicious), ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    raise SystemExit(main())
