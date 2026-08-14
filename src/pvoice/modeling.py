"""Classical machine learning models for the screening prototype.

All models are wrapped in a scikit-learn Pipeline that includes median
imputation (Praat features can be NaN on difficult recordings) and standard
scaling, so scaling parameters are always fit on training folds only —
this is important to avoid data leakage during cross-validation.
"""

from __future__ import annotations

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from . import config


def build_models() -> dict[str, Pipeline]:
    """Return the dictionary of candidate models, all as full pipelines."""
    common_steps = [
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]

    models: dict[str, Pipeline] = {
        # Majority-class baseline: any useful model must clearly beat this.
        "baseline_majority": Pipeline(
            common_steps + [(
                "clf",
                DummyClassifier(strategy="most_frequent"),
            )]
        ),
        "logistic_regression": Pipeline(
            common_steps + [(
                "clf",
                LogisticRegression(
                    max_iter=5000,
                    class_weight="balanced",
                    random_state=config.RANDOM_STATE,
                ),
            )]
        ),
        "svm_rbf": Pipeline(
            common_steps + [(
                "clf",
                SVC(
                    kernel="rbf",
                    probability=True,
                    class_weight="balanced",
                    random_state=config.RANDOM_STATE,
                ),
            )]
        ),
        "random_forest": Pipeline(
            common_steps + [(
                "clf",
                RandomForestClassifier(
                    n_estimators=300,
                    class_weight="balanced",
                    random_state=config.RANDOM_STATE,
                ),
            )]
        ),
        "mlp": Pipeline(
            common_steps + [(
                "clf",
                MLPClassifier(
                    hidden_layer_sizes=(32, 16),
                    max_iter=2000,
                    random_state=config.RANDOM_STATE,
                ),
            )]
        ),
    }
    return models
