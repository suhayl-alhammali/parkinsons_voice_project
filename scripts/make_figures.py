"""Generate presentation/report figures (Phase 6).

Where to run:  project folder, with .venv activated
Command:       python scripts/make_figures.py

Outputs (reports/figures/):
- feature_importance.png   top features of the final Random Forest
- roc_curve.png            ROC from final out-of-fold predictions
- validation_comparison.png  honest subject-independent result vs the
                             inflated numbers leaky splits would report
- score_distribution.png   OOF score histograms per class + uncertain band

The "leaky" numbers are computed here ONLY to demonstrate why subject
grouping matters; they must never be quoted as project results.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
warnings.filterwarnings("ignore", category=FutureWarning)

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import balanced_accuracy_score, roc_curve, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from pvoice import config
from pvoice.features import extended_feature_names, feature_names

# Okabe-Ito pair, CVD-validated (see dataviz palette check).
COLOR_HC = "#0072B2"
COLOR_PD = "#D55E00"
COLOR_NEUTRAL = "#8a8a86"

SEGMENT_TABLE = config.PROCESSED_DATA_DIR / "segment_features.csv"
FINAL_OOF = config.PROCESSED_DATA_DIR / "final_oof_predictions.csv"
FIG = config.FIGURES_DIR

HONEST_SUBJECT_BALACC = 0.822  # from final_model_report.md (3-seed mean)


def rf_pipeline() -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=300,
                                       class_weight="balanced",
                                       random_state=config.RANDOM_STATE)),
    ])


def recording_table(seg: pd.DataFrame) -> pd.DataFrame:
    agg = {f: (f, "mean") for f in extended_feature_names()}
    return (seg.groupby("relative_path")
            .agg(subject_id=("subject_id", "first"),
                 label=("label", "first"), **agg).reset_index())


def fig_feature_importance() -> None:
    model = joblib.load(config.MODEL_FILE)
    importances = model.named_steps["clf"].feature_importances_
    order = np.argsort(importances)[::-1][:15]
    names = [feature_names()[i] for i in order][::-1]
    values = importances[order][::-1]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.barh(names, values, color=COLOR_HC, height=0.62)
    for bar, v in zip(bars, values):
        ax.text(v + importances.max() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{v:.3f}", va="center", fontsize=8, color="#444")
    ax.set_xlabel("Random Forest importance (mean decrease in impurity)")
    ax.set_title("Top 15 features of the final model")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "feature_importance.png", dpi=200)
    plt.close(fig)


def fig_roc() -> None:
    oof = pd.read_csv(FINAL_OOF)
    subj = (oof.groupby("subject_id")
            .agg(label=("label", "first"), prob_pd=("prob_pd", "mean"))
            .reset_index())

    fig, ax = plt.subplots(figsize=(5.2, 5))
    for frame, color, name in ((oof, COLOR_HC, "recording level"),
                               (subj, COLOR_PD, "subject level")):
        fpr, tpr, _ = roc_curve(frame["label"], frame["prob_pd"])
        auc = roc_auc_score(frame["label"], frame["prob_pd"])
        ax.plot(fpr, tpr, color=color, linewidth=2,
                label=f"{name} (AUC = {auc:.2f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color=COLOR_NEUTRAL,
            linewidth=1, label="chance")
    ax.set_xlabel("False positive rate (healthy flagged as PD)")
    ax.set_ylabel("True positive rate (PD correctly flagged)")
    ax.set_title("ROC, out-of-fold predictions (seed 42)")
    ax.legend(frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "roc_curve.png", dpi=200)
    plt.close(fig)


def chunk_model_recording_balacc(seg: pd.DataFrame, grouped: bool) -> float:
    """Recording-level balanced accuracy of a chunk-level RF classifier.

    Identical pipeline and aggregation both times; ONLY the split changes:
    - grouped=True : StratifiedGroupKFold by subject (correct).
    - grouped=False: random chunk split (WRONG on purpose - chunks of the
      same recording land in both train and test, so the model can
      recognize the recording/speaker instead of the disease pattern).
    """
    from sklearn.model_selection import StratifiedGroupKFold

    features = extended_feature_names()
    X, y = seg[features], seg["label"]
    scores = []
    for seed in (42, 7, 2025):
        oof = seg[["relative_path", "label"]].copy()
        oof["prob_pd"] = np.nan
        if grouped:
            splits = StratifiedGroupKFold(5, shuffle=True, random_state=seed
                                          ).split(X, y, groups=seg["subject_id"])
        else:
            splits = StratifiedKFold(5, shuffle=True, random_state=seed
                                     ).split(X, y)
        for tr, te in splits:
            model = rf_pipeline()
            model.fit(X.iloc[tr], y.iloc[tr])
            oof.iloc[te, oof.columns.get_loc("prob_pd")] = (
                model.predict_proba(X.iloc[te])[:, 1])
        rec = (oof.groupby("relative_path")
               .agg(label=("label", "first"), prob_pd=("prob_pd", "mean"))
               .reset_index())
        scores.append(balanced_accuracy_score(
            rec["label"], (rec["prob_pd"] >= 0.5).astype(int)))
    return float(np.mean(scores))


def fig_validation_comparison(seg: pd.DataFrame) -> None:
    honest = chunk_model_recording_balacc(seg, grouped=True)
    leaky = chunk_model_recording_balacc(seg, grouped=False)

    labels = ["Correct: split grouped\nby subject\n(what this project does)",
              "Wrong: random chunk split\n(same recording in\ntrain AND test)"]
    values = [honest, leaky]
    colors = [COLOR_HC, COLOR_PD]

    fig, ax = plt.subplots(figsize=(5.8, 4.6))
    bars = ax.bar(labels, values, color=colors, width=0.5)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.012, f"{v:.3f}",
                ha="center", fontsize=12, fontweight="bold", color="#333")
    ax.set_ylim(0, 1.05)
    ax.axhline(0.5, linestyle="--", color=COLOR_NEUTRAL, linewidth=1)
    ax.text(1.4, 0.505, "chance", fontsize=8, color=COLOR_NEUTRAL,
            va="bottom", ha="right")
    ax.set_ylabel("Balanced accuracy (per recording)")
    ax.set_title("Same data, same model - only the split differs.\n"
                 "The inflated number measures memorization, not detection.")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "validation_comparison.png", dpi=200)
    plt.close(fig)
    print(f"  honest grouped split:  {honest:.3f}")
    print(f"  leaky chunk split:     {leaky:.3f}")


def fig_score_distribution() -> None:
    oof = pd.read_csv(FINAL_OOF)
    bins = np.linspace(0, 1, 21)

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.axvspan(config.UNCERTAIN_LOW, config.UNCERTAIN_HIGH,
               color=COLOR_NEUTRAL, alpha=0.15, zorder=0)
    for label, color, name in ((0, COLOR_HC, "healthy control (HC)"),
                               (1, COLOR_PD, "Parkinson's group (PD)")):
        part = oof[oof["label"] == label]
        ax.hist(part["prob_pd"], bins=bins, alpha=0.65, color=color,
                label=name, edgecolor="white", linewidth=0.5)
    ax.text((config.UNCERTAIN_LOW + config.UNCERTAIN_HIGH) / 2, ax.get_ylim()[1] * 0.95,
            "reported as\ninconclusive", ha="center", va="top", fontsize=8,
            color="#555")
    ax.set_xlabel("Model score for the PD class (out-of-fold, per recording)")
    ax.set_ylabel("Number of recordings")
    ax.set_title("Score distribution by true class")
    ax.legend(frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "score_distribution.png", dpi=200)
    plt.close(fig)


def fig_external_scores() -> None:
    """Speaker-level score distributions on the Italian external set."""
    ext = pd.read_csv(config.PROCESSED_DATA_DIR / "external_predictions.csv")
    speakers = (ext.groupby("speaker")
                .agg(label=("label", "first"),
                     age_group=("age_group", "first"),
                     prob_pd=("prob_pd", "mean"))
                .reset_index())
    groups = [("HC", "elderly", COLOR_HC, "elderly HC"),
              ("PD", "elderly", COLOR_PD, "PD"),
              ("HC", "young", COLOR_NEUTRAL, "young HC")]

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.axvspan(config.UNCERTAIN_LOW, config.UNCERTAIN_HIGH,
               color=COLOR_NEUTRAL, alpha=0.15, zorder=0)
    rng = np.random.default_rng(0)
    for i, (label, age, color, name) in enumerate(groups):
        part = speakers[(speakers["label"] == label)
                        & (speakers["age_group"] == age)]
        y = np.full(len(part), i) + rng.uniform(-0.13, 0.13, len(part))
        ax.scatter(part["prob_pd"], y, s=42, color=color, alpha=0.85,
                   edgecolors="white", linewidths=0.7, label=name)
    ax.text((config.UNCERTAIN_LOW + config.UNCERTAIN_HIGH) / 2, 2.55,
            "inconclusive band", ha="center", fontsize=8, color="#555")
    ax.axvline(0.5, linestyle=":", color=COLOR_NEUTRAL, linewidth=1)
    ax.set_yticks(range(len(groups)),
                  [name for _, _, _, name in groups])
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, 2.8)
    ax.set_xlabel("Model score for the PD class (per speaker, frozen model)")
    ax.set_title("External validation (Italian dataset):\n"
                 "most out-of-domain speakers fall in the inconclusive band")
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "external_scores.png", dpi=200)
    plt.close(fig)


def main() -> int:
    for path in (config.MODEL_FILE, FINAL_OOF, SEGMENT_TABLE):
        if not path.exists():
            print(f"Missing input: {path}")
            return 1
    FIG.mkdir(parents=True, exist_ok=True)
    seg = pd.read_csv(SEGMENT_TABLE)
    rec = recording_table(seg)

    print("Feature importance...")
    fig_feature_importance()
    print("ROC curve...")
    fig_roc()
    print("Validation comparison (computes leaky splits, ~1 min)...")
    fig_validation_comparison(seg)
    print("Score distribution...")
    fig_score_distribution()
    n = 4
    if (config.PROCESSED_DATA_DIR / "external_predictions.csv").exists():
        print("External validation scores...")
        fig_external_scores()
        n = 5
    print(f"\nSaved {n} figures to {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
