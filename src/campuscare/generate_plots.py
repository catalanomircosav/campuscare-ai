"""Generazione dei grafici per CampusCare AI.

Il modulo produce grafici semplici per documentare:
- distribuzione delle classi di priorità;
- confronto dei modelli sulle metriche principali.

I grafici vengono salvati nella cartella plots/.
"""

from __future__ import annotations

from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd

from .generate_dataset import DATASET_PATH, generate_dataset
from .train_models import METRICS_PATH, main as train_models_main


ROOT_DIR = Path(__file__).resolve().parents[2]
PLOTS_DIR = ROOT_DIR / "plots"


def load_or_generate_dataset() -> pd.DataFrame:
    """Carica il dataset oppure lo genera se non esiste."""

    if not DATASET_PATH.exists():
        return generate_dataset()

    return pd.read_csv(DATASET_PATH)


def load_or_generate_metrics() -> dict:
    """Carica le metriche oppure esegue il training se non esistono."""

    if not METRICS_PATH.exists():
        train_models_main()

    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def save_priority_distribution(dataset: pd.DataFrame) -> None:
    """Salva il grafico della distribuzione delle priorità."""

    counts = dataset["priority"].value_counts().sort_index()

    plt.figure(figsize=(7, 4))
    counts.plot(kind="bar")
    plt.title("Distribuzione delle classi di priorità")
    plt.xlabel("Priorità")
    plt.ylabel("Numero di segnalazioni")
    plt.tight_layout()

    output_path = PLOTS_DIR / "priority_distribution.png"
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_metric_comparison(metrics: dict, metric_name: str, output_filename: str) -> None:
    """Salva un grafico di confronto tra modelli per una metrica."""

    model_names = []
    means = []
    stds = []

    for model_name, model_metrics in metrics.items():
        model_names.append(model_name)
        means.append(model_metrics[metric_name]["mean"])
        stds.append(model_metrics[metric_name]["std"])

    plt.figure(figsize=(8, 4))
    plt.bar(model_names, means, yerr=stds, capsize=5)
    plt.title(f"Confronto modelli - {metric_name}")
    plt.xlabel("Modello")
    plt.ylabel(metric_name)
    plt.ylim(0, 1)
    plt.xticks(rotation=20)
    plt.tight_layout()

    output_path = PLOTS_DIR / output_filename
    plt.savefig(output_path, dpi=150)
    plt.close()


def generate_plots() -> None:
    """Genera tutti i grafici."""

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    dataset = load_or_generate_dataset()
    metrics = load_or_generate_metrics()

    save_priority_distribution(dataset)
    save_metric_comparison(metrics, "accuracy", "model_accuracy.png")
    save_metric_comparison(metrics, "macro_f1", "model_macro_f1.png")
    save_metric_comparison(metrics, "weighted_f1", "model_weighted_f1.png")


def main() -> None:
    """Esegue la generazione dei grafici."""

    generate_plots()

    print("Plots generated:")
    print(f"- {PLOTS_DIR / 'priority_distribution.png'}")
    print(f"- {PLOTS_DIR / 'model_accuracy.png'}")
    print(f"- {PLOTS_DIR / 'model_macro_f1.png'}")
    print(f"- {PLOTS_DIR / 'model_weighted_f1.png'}")


if __name__ == "__main__":
    main()