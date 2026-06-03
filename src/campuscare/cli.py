"""CLI interattiva per CampusCare AI.

Permette di inserire una segnalazione tecnica da terminale e ottenere
l'analisi completa del sistema.
"""

from __future__ import annotations

import json
from typing import Any

from .domain import DEVICES, ROOM_COORDINATES, ROOM_TYPE_BY_NAME, SYMPTOMS
from .main import analyze_report


def choose_from_list(title: str, values: list[str]) -> str:
    """Mostra una lista numerata e restituisce il valore scelto."""

    print()
    print(title)

    for index, value in enumerate(values, start=1):
        print(f"{index}. {value}")

    while True:
        raw_choice = input("Scelta: ").strip()

        if not raw_choice.isdigit():
            print("Inserisci un numero valido.")
            continue

        choice = int(raw_choice)

        if 1 <= choice <= len(values):
            return values[choice - 1]

        print("Scelta fuori intervallo.")


def read_int(
    prompt: str,
    default: int,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    """Legge un intero da input con valore di default."""

    while True:
        raw_value = input(f"{prompt} [{default}]: ").strip()

        if raw_value == "":
            value = default
        else:
            if not raw_value.isdigit():
                print("Inserisci un numero intero valido.")
                continue

            value = int(raw_value)

        if minimum is not None and value < minimum:
            print(f"Il valore deve essere almeno {minimum}.")
            continue

        if maximum is not None and value > maximum:
            print(f"Il valore deve essere al massimo {maximum}.")
            continue

        return value


def read_float(
    prompt: str,
    default: float,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    """Legge un float da input con valore di default."""

    while True:
        raw_value = input(f"{prompt} [{default}]: ").strip()

        if raw_value == "":
            value = default
        else:
            try:
                value = float(raw_value)
            except ValueError:
                print("Inserisci un numero valido.")
                continue

        if minimum is not None and value < minimum:
            print(f"Il valore deve essere almeno {minimum}.")
            continue

        if maximum is not None and value > maximum:
            print(f"Il valore deve essere al massimo {maximum}.")
            continue

        return value


def read_binary(prompt: str, default: int = 1) -> int:
    """Legge un valore binario 0/1."""

    while True:
        value = read_int(prompt, default=default, minimum=0, maximum=1)

        if value in {0, 1}:
            return value

        print("Inserisci 0 oppure 1.")


def build_case_from_input() -> dict[str, Any]:
    """Costruisce una segnalazione leggendo i dati da terminale."""

    room_names = list(ROOM_COORDINATES.keys())

    room_name = choose_from_list("Seleziona ambiente:", room_names)
    room_type = ROOM_TYPE_BY_NAME[room_name]

    device = choose_from_list("Seleziona dispositivo:", DEVICES)
    symptom = choose_from_list("Seleziona sintomo:", SYMPTOMS)

    print()
    print("Contesto della segnalazione")

    event_in_minutes = read_int(
        "Minuti mancanti a lezione/esame",
        default=30,
        minimum=0,
    )

    users_involved = read_int(
        "Numero utenti coinvolti",
        default=50,
        minimum=0,
    )

    exam_or_lecture = read_binary(
        "Lezione/esame previsto? 1=sì, 0=no",
        default=1,
    )

    temperature = read_float(
        "Temperatura ambiente",
        default=26.0,
        minimum=0.0,
        maximum=50.0,
    )

    network_load = read_float(
        "Carico rete stimato da 0 a 1",
        default=0.75,
        minimum=0.0,
        maximum=1.0,
    )

    return {
        "room_name": room_name,
        "room_type": room_type,
        "device": device,
        "symptom": symptom,
        "event_in_minutes": event_in_minutes,
        "users_involved": users_involved,
        "exam_or_lecture": exam_or_lecture,
        "temperature": temperature,
        "network_load": network_load,
    }

def format_priority(priority: str) -> str:
    """Formatta una priorità per la stampa."""

    return priority.upper()


def format_path(path: list[list[int]] | list[tuple[int, int]]) -> str:
    """Formatta il percorso A* in modo leggibile."""

    if not path:
        return "nessun percorso trovato"

    return " -> ".join(f"({position[0]}, {position[1]})" for position in path)


def print_analysis_report(result: dict[str, Any]) -> None:
    """Stampa il risultato dell'analisi in formato leggibile."""

    case = result["case"]
    symbolic = result["symbolic_reasoning"]
    bayes = result["bayesian_reasoning"]
    ml = result["machine_learning"]
    assignment = result["csp_assignment"]
    astar = result["astar_path"]

    print()
    print("Risultato analisi")
    print("=================")

    print()
    print("Caso analizzato")
    print("---------------")
    print(f"- Ambiente: {case['room_name']} ({case['room_type']})")
    print(f"- Dispositivo: {case['device']}")
    print(f"- Sintomo: {case['symptom']}")
    print(f"- Evento tra: {case['event_in_minutes']} minuti")
    print(f"- Utenti coinvolti: {case['users_involved']}")
    print(f"- Lezione/esame previsto: {'sì' if case['exam_or_lecture'] else 'no'}")
    print(f"- Temperatura: {case['temperature']}")
    print(f"- Carico rete: {case['network_load']}")

    print()
    print("Diagnosi simbolica")
    print("------------------")
    print(f"- Guasto: {symbolic['fault']}")
    print(f"- Intervento: {symbolic['intervention']}")
    print(f"- Priorità da regole: {format_priority(symbolic['rule_priority'])}")

    print()
    print("Spiegazioni")
    print("-----------")
    for explanation in symbolic["explanations"]:
        print(f"- {explanation}")

    print()
    print("Inferenza bayesiana")
    print("-------------------")
    print(f"- Sintomo osservato: {bayes['evidence_symptom']}")
    print(f"- Guasto più probabile: {bayes['most_probable_fault']}")
    print("- Probabilità principali:")
    for fault, probability in bayes["probabilities"].items():
        print(f"  - {fault}: {probability * 100:.2f}%")

    print()
    print("Machine Learning")
    print("----------------")
    print(f"- Priorità predetta: {format_priority(ml['predicted_priority'])}")

    print()
    print("Assegnazione tecnico")
    print("--------------------")
    if assignment["assigned"]:
        print(f"- Tecnico assegnato: {assignment['technician']}")
        print(f"- Competenza richiesta: {assignment['required_competence']}")
        print(f"- Guasto usato per assegnazione: {assignment['fault_used']}")
        print(f"- Posizione tecnico: {tuple(assignment['technician_position'])}")
        print(f"- Distanza: {assignment['distance']}")
    else:
        print("- Nessun tecnico assegnato")
        print(f"- Motivo: {assignment['reason']}")
    print()
    print("Percorso A*")
    print("-----------")
    print(f"- Lunghezza percorso: {astar['path_length']}")
    print(f"- Percorso: {format_path(astar['path'])}")

def main() -> None:
    """Esegue la CLI."""

    print("CampusCare AI - CLI")
    print("===================")

    case = build_case_from_input()
    result = analyze_report(case)

    print_analysis_report(result)

if __name__ == "__main__":
    main()