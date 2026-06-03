"""Addestramento e valutazione dei modelli supervisionati.

Il modulo usa il dataset sintetico generato da generate_dataset.py
per predire la priorità di una segnalazione tecnica.

La valutazione viene fatta con Stratified K-Fold Cross-Validation,
riportando media e deviazione standard delle metriche.
"""

from __future__ import annotations

from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import make_scorer, precision_score

from .generate_dataset import DATASET_PATH, generate_dataset


ROOT_DIR = Path(__file__).resolve().parents[2]

MODELS_DIR = ROOT_DIR / "models"
RESULTS_DIR = ROOT_DIR / "results"

MODEL_PATH = MODELS_DIR / "priority_model.joblib"
METRICS_PATH = RESULTS_DIR / "metrics.json"

TARGET = "priority"

CATEGORICAL_FEATURES = [
    "room_name",
    "room_type",
    "device",
    "symptom",
]

NUMERIC_FEATURES = [
    "event_in_minutes",
    "users_involved",
    "exam_or_lecture",
    "temperature",
    "network_load",
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES


def load_dataset() -> pd.DataFrame:
    """Carica il dataset oppure lo genera se non esiste."""

    if not DATASET_PATH.exists():
        return generate_dataset()

    return pd.read_csv(DATASET_PATH)

def build_preprocessor() -> ColumnTransformer:
    """Costruisce il preprocessing per feature categoriche e numeriche."""

    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
            (
                "numeric",
                StandardScaler(),
                NUMERIC_FEATURES,
            ),
        ]
    )


def get_models() -> dict[str, object]:
    """Restituisce i modelli da confrontare."""

    return {
        "decision_tree": DecisionTreeClassifier(
            max_depth=8,
            random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            random_state=42,
        ),
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            random_state=42,
        ),
        "naive_bayes": GaussianNB(),
    }


def evaluate_models(dataset: pd.DataFrame) -> dict:
    """Valuta più modelli tramite cross-validation."""

    x = dataset[ALL_FEATURES]
    y = dataset[TARGET]

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    scoring = {
        "accuracy": "accuracy",
        "macro_f1": "f1_macro",
        "weighted_f1": "f1_weighted",
        "precision_macro": make_scorer(
            precision_score,
            average="macro",
            zero_division=0,
        ),
        "recall_macro": "recall_macro",
    }

    results: dict[str, dict] = {}

    for model_name, model in get_models().items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                ("classifier", model),
            ]
        )

        scores = cross_validate(
            estimator=pipeline,
            X=x,
            y=y,
            cv=cv,
            scoring=scoring,
            error_score="raise",
        )

        model_results = {}

        for metric_name, values in scores.items():
            if not metric_name.startswith("test_"):
                continue

            clean_name = metric_name.replace("test_", "")

            model_results[clean_name] = {
                "mean": round(float(values.mean()), 4),
                "std": round(float(values.std()), 4),
            }

        results[model_name] = model_results

    return results


def train_final_model(dataset: pd.DataFrame) -> Pipeline:
    """Addestra il modello operativo finale.

    Per la versione base viene scelta Logistic Regression, perché nella valutazione
    ha ottenuto il miglior compromesso tra accuracy, macro-F1 e weighted-F1.
    """

    x = dataset[ALL_FEATURES]
    y = dataset[TARGET]

    pipeline = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )

    pipeline.fit(x, y)

    return pipeline


def save_metrics(metrics: dict) -> None:
    """Salva le metriche in formato JSON."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_model(model: Pipeline) -> None:
    """Salva il modello operativo."""

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)


def main() -> None:
    """Esegue valutazione e addestramento finale."""

    dataset = load_dataset()

    print("Dataset loaded:", DATASET_PATH)
    print("Rows:", len(dataset))
    print()

    print("Priority distribution:")
    print(dataset[TARGET].value_counts())
    print()

    print("Evaluating models...")
    metrics = evaluate_models(dataset)

    save_metrics(metrics)

    print("Training final model...")
    model = train_final_model(dataset)
    save_model(model)

    print()
    print("Metrics saved to:", METRICS_PATH)
    print("Model saved to:", MODEL_PATH)
    print()

    print("Evaluation summary:")
    for model_name, model_metrics in metrics.items():
        accuracy = model_metrics["accuracy"]
        macro_f1 = model_metrics["macro_f1"]
        weighted_f1 = model_metrics["weighted_f1"]

        print(
            f"- {model_name}: "
            f"accuracy={accuracy['mean']}±{accuracy['std']}, "
            f"macro_f1={macro_f1['mean']}±{macro_f1['std']}, "
            f"weighted_f1={weighted_f1['mean']}±{weighted_f1['std']}"
        )


if __name__ == "__main__":
    main()