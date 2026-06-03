"""Generazione del dataset sintetico per CampusCare AI.

Il dataset rappresenta segnalazioni tecniche in ambienti universitari.

Ogni riga descrive un caso con:
- ambiente;
- dispositivo coinvolto;
- sintomo osservato;
- contesto didattico;
- numero di utenti coinvolti;
- valori ambientali;
- priorità finale.

La priorità non è generata in modo casuale puro: deriva da regole di dominio
con una piccola quantità di rumore per simulare casi ambigui.
"""

from __future__ import annotations

from pathlib import Path
import random

import pandas as pd

from .domain import DEVICES, ROOM_COORDINATES, ROOM_TYPE_BY_NAME, SYMPTOMS, PRIORITIES


RANDOM_SEED = 42

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
DATASET_PATH = DATA_DIR / "segnalazioni.csv"


def infer_priority(
    room_type: str,
    device: str,
    symptom: str,
    event_in_minutes: int,
    users_involved: int,
    exam_or_lecture: int,
    temperature: float,
    network_load: float,
) -> str:
    """Assegna una priorità usando regole di dominio.

    La funzione produce un punteggio cumulativo. Il punteggio viene poi
    convertito in una classe: bassa, media, alta o critica.
    """

    score = 0

    # Contesto didattico.
    if exam_or_lecture:
        score += 2

    if event_in_minutes <= 30:
        score += 3
    elif event_in_minutes <= 90:
        score += 1

    # Numero di persone coinvolte.
    if users_involved >= 80:
        score += 2
    elif users_involved >= 35:
        score += 1

    # Dispositivi essenziali.
    if device in {
        "proiettore",
        "pc_docente",
        "rete_wifi",
        "router_laboratorio",
        "presa_elettrica",
    }:
        score += 2
    elif device in {
        "lim",
        "impianto_audio",
        "climatizzatore",
    }:
        score += 1

    # Gravità del sintomo.
    if symptom in {
        "odore_bruciato",
        "non_si_accende",
    }:
        score += 3
    elif symptom in {
        "connessione_assente",
        "nessun_segnale",
        "temperatura_alta",
    }:
        score += 2
    elif symptom in {
        "connessione_lenta",
        "audio_assente",
        "immagine_distorta",
        "riavvii_frequenti",
    }:
        score += 1

    if room_type == "laboratorio":
        score += 1

    if device == "climatizzatore" and temperature >= 29:
        score += 2

    if device in {"rete_wifi", "router_laboratorio"} and network_load >= 0.8:
        score += 1

    if score >= 11:
        return "critica"
    if score >= 8:
        return "alta"
    if score >= 5:
        return "media"
    return "bassa"


def generate_dataset(
    n_rows: int = 800,
    output_path: Path = DATASET_PATH,
) -> pd.DataFrame:
    """Genera e salva il dataset sintetico."""

    random.seed(RANDOM_SEED)

    room_names = list(ROOM_COORDINATES.keys())
    rows: list[dict] = []

    for report_id in range(1, n_rows + 1):
        room_name = random.choice(room_names)
        room_type = ROOM_TYPE_BY_NAME[room_name]

        device = random.choice(DEVICES)
        symptom = random.choice(SYMPTOMS)

        event_in_minutes = random.choice(
            [10, 20, 30, 45, 60, 90, 120, 180, 240]
        )
        users_involved = random.randint(1, 120)
        exam_or_lecture = random.choice([0, 0, 0, 1, 1])

        temperature = round(random.uniform(18.0, 33.0), 1)
        network_load = round(random.uniform(0.1, 1.0), 2)

        priority = infer_priority(
            room_type=room_type,
            device=device,
            symptom=symptom,
            event_in_minutes=event_in_minutes,
            users_involved=users_involved,
            exam_or_lecture=exam_or_lecture,
            temperature=temperature,
            network_load=network_load,
        )

        if random.random() < 0.05:
            priority = random.choice(PRIORITIES)

        rows.append(
            {
                "report_id": report_id,
                "room_name": room_name,
                "room_type": room_type,
                "device": device,
                "symptom": symptom,
                "event_in_minutes": event_in_minutes,
                "users_involved": users_involved,
                "exam_or_lecture": exam_or_lecture,
                "temperature": temperature,
                "network_load": network_load,
                "priority": priority,
            }
        )

    dataset = pd.DataFrame(rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_path, index=False)

    return dataset


def main() -> None:
    """Genera il dataset e stampa un piccolo riepilogo."""

    dataset = generate_dataset()

    print(f"Dataset generated: {DATASET_PATH}")
    print()
    print("First rows:")
    print(dataset.head())
    print()
    print("Priority distribution:")
    print(dataset["priority"].value_counts())


if __name__ == "__main__":
    main()