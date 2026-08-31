"""Dark-theme slide figures for the PowerPoint deck.

Same data sources as make_slide_figs.py (saved prediction tables only,
no recomputation); restyled for a dark navy background with brighter
line colors and light text. Transparent figure background so the deck's
own panel color shows through.

Run from the project root:
    .venv/Scripts/python.exe report/defence/make_dark_figs.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, roc_auc_score

from pvoice import config
from pvoice.features import feature_names

OUT = ROOT / "report" / "defence" / "figs"
OUT.mkdir(parents=True, exist_ok=True)

HONEST = "#5AB4F0"    # bright blue on dark  = honest / correct
WRONG = "#FF8C42"     # bright vermillion    = inflated / wrong
NEUTRAL = "#8fa1b8"
TEXT = "#DCE6F2"
GRID = "#33445c"

plt.rcParams.update({
    "font.size": 16, "axes.labelsize": 16, "xtick.labelsize": 14,
    "ytick.labelsize": 14, "legend.fontsize": 14,
    "text.color": TEXT, "axes.labelcolor": TEXT,
    "xtick.color": TEXT, "ytick.color": TEXT,
    "axes.edgecolor": GRID,
    "axes.spines.top": False, "axes.spines.right": False,
})


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=200, transparent=True)
    plt.close(fig)


def fig_roc():
    oof = pd.read_csv(ROOT / "data/processed/final_oof_predictions.csv")
    subj = (oof.groupby("subject_id")
            .agg(label=("label", "first"), prob_pd=("prob_pd", "mean"))
            .reset_index())
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    for frame, color, name, lw in ((oof, NEUTRAL, "recording level", 2.4),
                                   (subj, HONEST, "subject level", 3.4)):
        fpr, tpr, _ = roc_curve(frame["label"], frame["prob_pd"])
        auc = roc_auc_score(frame["label"], frame["prob_pd"])
        ax.plot(fpr, tpr, color=color, linewidth=lw,
                label=f"{name} (AUC = {auc:.2f})")
    ax.plot([0, 1], [0, 1], "--", color=NEUTRAL, linewidth=1.4,
            label="chance")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    leg = ax.legend(frameon=False, loc="lower right")
    for t in leg.get_texts():
        t.set_color(TEXT)
    _save(fig, "roc_dark.png")


def fig_importance():
    model = joblib.load(ROOT / "models/model.joblib")
    imp = model.named_steps["clf"].feature_importances_
    order = np.argsort(imp)[::-1][:10]
    names = [feature_names()[i] for i in order][::-1]
    vals = imp[order][::-1]
    pretty = {"f0_range_hz": "pitch range", "f0_max_hz": "pitch maximum",
              "f0_mean_hz": "pitch mean", "f0_median_hz": "pitch median",
              "jitter_local_abs": "jitter (absolute)"}
    labels = [pretty.get(n, n) for n in names]
    colors = [HONEST if i == len(vals) - 1 else NEUTRAL
              for i in range(len(vals))]
    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    ax.barh(range(len(vals)), vals, color=colors, height=0.62)
    ax.set_yticks(range(len(vals)), labels)
    ax.set_xlabel("Random Forest importance")
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.012, i, f"{v:.3f}", va="center",
                fontsize=13, color=TEXT)
    _save(fig, "importance_dark.png")


def fig_external():
    ext = pd.read_csv(ROOT / "data/processed/external_predictions.csv")
    speakers = (ext.groupby("speaker")
                .agg(label=("label", "first"),
                     age_group=("age_group", "first"),
                     prob_pd=("prob_pd", "mean"))
                .reset_index())
    groups = [("HC", "elderly", HONEST, "elderly healthy"),
              ("PD", "elderly", WRONG, "Parkinson's"),
              ("HC", "young", NEUTRAL, "young healthy")]
    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.axvspan(config.UNCERTAIN_LOW, config.UNCERTAIN_HIGH,
               color="#c8d4e4", alpha=0.13, zorder=0)
    rng = np.random.default_rng(0)
    for i, (label, age, color, name) in enumerate(groups):
        part = speakers[(speakers["label"] == label)
                        & (speakers["age_group"] == age)]
        y = np.full(len(part), i) + rng.uniform(-0.14, 0.14, len(part))
        ax.scatter(part["prob_pd"], y, s=110, color=color, alpha=0.95,
                   edgecolors="#0B1526", linewidths=1.0)
    ax.text((config.UNCERTAIN_LOW + config.UNCERTAIN_HIGH) / 2, 2.62,
            "inconclusive band", ha="center", fontsize=14, color=TEXT)
    ax.axvline(0.5, linestyle=":", color=NEUTRAL, linewidth=1.4)
    ax.set_yticks(range(3), [g[3] for g in groups])
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, 2.9)
    ax.set_xlabel("model score for the PD class (per speaker)")
    ax.spines["left"].set_visible(False)
    _save(fig, "external_dark.png")


if __name__ == "__main__":
    fig_roc()
    fig_importance()
    fig_external()
    print("wrote", sorted(p.name for p in OUT.glob("*_dark.png")))
