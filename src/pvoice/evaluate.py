"""Subject-independent evaluation with stratified grouped cross-validation.

The rule that protects scientific validity: recordings from the same subject
must NEVER appear in both the training part and the test part of a fold.
StratifiedGroupKFold with subject_id as the group enforces this while also
keeping the HC/PD ratio similar across folds.  A hard runtime assertion
double-checks every fold and aborts on any overlap.

All metrics are computed from out-of-fold (OOF) predictions, which are also
returned so they can be saved and re-analyzed (per task, per subject, ...).

Subject-level results: each subject has up to 2 recordings (one per task).
The subject-level prediction is the MEAN of the subject's out-of-fold PD
probabilities, thresholded at 0.5.  This simple average is documented in the
report and is the same rule the prototype will use if given several files.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline

from . import config

METRIC_NAMES = ["accuracy", "balanced_accuracy", "sensitivity_pd",
                "specificity_hc", "precision", "f1", "roc_auc"]


def check_grouping(subjects: pd.Series, labels: pd.Series) -> list[str]:
    """Sanity checks before any training.  Returns a list of problems."""
    problems = []
    if subjects.isna().any():
        problems.append("some recordings have no subject ID")
    per_subject_labels = labels.groupby(subjects).nunique()
    mixed = per_subject_labels[per_subject_labels > 1]
    if not mixed.empty:
        problems.append(
            f"subjects with MORE THAN ONE label (impossible, data error): "
            f"{list(mixed.index)}"
        )
    n_subjects = subjects.nunique()
    if n_subjects < config.N_SPLITS:
        problems.append(
            f"only {n_subjects} subjects but {config.N_SPLITS} folds requested"
        )
    return problems


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray,
                    y_prob: np.ndarray | None) -> dict[str, float]:
    """All required metrics for one set of predictions.

    sensitivity_pd = recall of the PD class (how many PD cases are caught).
    specificity_hc = recall of the HC class (how many healthy are cleared).
    """
    tn, fp, fn, tp = confusion_matrix(
        y_true, y_pred, labels=[config.LABEL_HC, config.LABEL_PD]
    ).ravel()
    out = {
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "sensitivity_pd": recall_score(y_true, y_pred, zero_division=0),
        "specificity_hc": tn / (tn + fp) if (tn + fp) else float("nan"),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }
    if y_prob is not None and len(np.unique(y_true)) > 1:
        out["roc_auc"] = roc_auc_score(y_true, y_prob)
    else:
        out["roc_auc"] = float("nan")
    return {k: float(v) for k, v in out.items()}


def cross_validate_grouped(
    model_name: str,
    pipeline: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    meta: pd.DataFrame,
    n_splits: int = config.N_SPLITS,
) -> pd.DataFrame:
    """Stratified GroupKFold CV for one model.

    Returns the out-of-fold prediction table with one row per recording:
    subject_id, task, relative_path, fold, model, true label, predicted
    label, and PD probability.  Every recording is predicted exactly once,
    by a model that never saw that subject during training.

    The pipeline given here contains imputation and scaling as its first
    steps, so those are re-fit inside each training fold only.
    """
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True,
                                random_state=config.RANDOM_STATE)
    rows = []

    for fold_idx, (train_idx, test_idx) in enumerate(
        sgkf.split(X, y, groups=groups)
    ):
        # Hard anti-leakage assertion — belt and braces.
        train_subjects = set(groups.iloc[train_idx])
        test_subjects = set(groups.iloc[test_idx])
        overlap = train_subjects & test_subjects
        if overlap:
            raise RuntimeError(
                f"LEAKAGE: subjects {overlap} appear in train AND test"
            )

        pipeline.fit(X.iloc[train_idx], y.iloc[train_idx])
        y_pred = pipeline.predict(X.iloc[test_idx])
        y_prob = pipeline.predict_proba(X.iloc[test_idx])[:, 1]

        for local, idx in enumerate(test_idx):
            rows.append({
                "model": model_name,
                "fold": fold_idx,
                "subject_id": groups.iloc[idx],
                "task": meta.iloc[idx]["task"],
                "relative_path": meta.iloc[idx]["relative_path"],
                "y_true": int(y.iloc[idx]),
                "y_pred": int(y_pred[local]),
                "prob_pd": float(y_prob[local]),
            })

    oof = pd.DataFrame(rows)
    assert len(oof) == len(X), "every recording must be predicted exactly once"
    return oof


def fold_metric_table(oof: pd.DataFrame) -> pd.DataFrame:
    """Per-fold metrics for one model's OOF table (one row per fold)."""
    rows = []
    for fold, part in oof.groupby("fold"):
        metrics = compute_metrics(
            part["y_true"].to_numpy(), part["y_pred"].to_numpy(),
            part["prob_pd"].to_numpy(),
        )
        rows.append({"fold": fold, "n_recordings": len(part),
                     "n_subjects": part["subject_id"].nunique(), **metrics})
    return pd.DataFrame(rows)


def subject_level_oof(oof: pd.DataFrame) -> pd.DataFrame:
    """Aggregate recording-level OOF predictions to one row per subject.

    Rule (documented in the report): subject PD probability = mean of the
    subject's recording probabilities; predicted class = 1 if mean >= 0.5.
    """
    grouped = oof.groupby("subject_id").agg(
        y_true=("y_true", "first"),
        prob_pd=("prob_pd", "mean"),
        n_recordings=("y_true", "size"),
    ).reset_index()
    grouped["y_pred"] = (grouped["prob_pd"] >= 0.5).astype(int)
    return grouped


def overall_metrics(oof: pd.DataFrame) -> dict[str, float]:
    """Pooled metrics over all OOF predictions (recording level)."""
    return compute_metrics(
        oof["y_true"].to_numpy(), oof["y_pred"].to_numpy(),
        oof["prob_pd"].to_numpy(),
    )
