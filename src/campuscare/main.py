"""Demo integrata di CampusCare AI.

Questo modulo collega tutti i componenti principali del sistema:
- motore simbolico;
- modello supervisionato;
- assegnazione tramite vincoli;
- ricerca A*.

L'obiettivo è mostrare una singola esecuzione end-to-end su una segnalazione
tecnica di esempio.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from .astar import astar_search
from .csp_assignment import assign_technician
from .domain import ROOM_COORDINATES
from .generate_dataset import generate_dataset
from .logic_engine import analyze_case
from .train_models import (
    ALL_FEATURES,
    MODEL_PATH,
    train_final_model,
)


def load_or_train_model():
    """Carica il modello operativo oppure lo addestra se non esiste."""

    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)

    dataset = generate_dataset()
    model = train_final_model(dataset)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    return model


def predict_priority(model: Any, case: dict[str, Any]) -> str:
    """Predice la priorità usando il modello supervisionato."""

    row = pd.DataFrame(
        [
            {
                feature: case[feature]
                for feature in ALL_FEATURES
            }
        ]
    )

    prediction = model.predict(row)[0]

    return str(prediction)


def build_demo_case() -> dict[str, Any]:
    """Costruisce una segnalazione di esempio."""

    return {
        "room_name": "Lab_1",
        "room_type": "laboratorio",
        "device": "router_laboratorio",
        "symptom": "connessione_assente",
        "event_in_minutes": 20,
        "users_involved": 72,
        "exam_or_lecture": 1,
        "temperature": 26.0,
        "network_load": 0.88,
    }


def analyze_report(case: dict[str, Any]) -> dict[str, Any]:
    """Esegue l'analisi completa di una segnalazione."""

    model = load_or_train_model()

    logic_result = analyze_case(case)
    ml_priority = predict_priority(model, case)

    target_position = ROOM_COORDINATES[case["room_name"]]

    assignment = assign_technician(
        device=case["device"],
        target_position=target_position,
    )

    path = []

    if assignment["assigned"]:
        technician_position = tuple(assignment["technician_position"])

        obstacles = {
            (3, 3),
            (3, 4),
            (3, 5),
            (4, 5),
        }

        path = astar_search(
            start=technician_position,
            goal=target_position,
            rows=10,
            cols=10,
            obstacles=obstacles,
        )

    return {
        "case": case,
        "symbolic_reasoning": {
            "fault": logic_result.fault,
            "intervention": logic_result.intervention,
            "rule_priority": logic_result.rule_priority,
            "explanations": logic_result.explanations,
        },
        "machine_learning": {
            "predicted_priority": ml_priority,
        },
        "csp_assignment": assignment,
        "astar_path": {
            "path": path,
            "path_length": max(len(path) - 1, 0),
        },
    }


def main() -> None:
    """Esegue la demo e stampa il risultato in formato JSON."""

    case = build_demo_case()
    result = analyze_report(case)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()