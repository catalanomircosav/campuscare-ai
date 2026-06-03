"""Assegnazione del tecnico tramite vincoli.

Il modulo implementa un piccolo CSP per scegliere un tecnico compatibile
con una segnalazione tecnica.

Variabile:
- tecnico_assegnato

Dominio:
- insieme dei tecnici disponibili nel sistema

Vincoli:
- il tecnico deve essere disponibile;
- il tecnico deve possedere la competenza richiesta dal dispositivo;
- il tecnico deve trovarsi entro una distanza massima dal luogo della segnalazione.

Criterio di scelta:
- tra i tecnici che soddisfano i vincoli, viene scelto quello più vicino.
"""

from __future__ import annotations

from math import dist
from typing import Any

from .domain import DEVICE_COMPETENCE, FAULT_COMPETENCE, TECHNICIANS

def get_required_competence(device: str, fault: str | None = None) -> str:
    """Restituisce la competenza richiesta.

    Se il guasto è noto, viene usato il mapping guasto -> competenza.
    Altrimenti si usa il mapping dispositivo -> competenza.
    """

    if fault is not None:
        if fault not in FAULT_COMPETENCE:
            raise ValueError(f"Unknown fault: {fault}")

        return FAULT_COMPETENCE[fault]

    if device not in DEVICE_COMPETENCE:
        raise ValueError(f"Unknown device: {device}")

    return DEVICE_COMPETENCE[device]


def is_feasible_technician(
    technician: dict[str, Any],
    required_competence: str,
    target_position: tuple[int, int],
    max_distance: float,
) -> tuple[bool, list[str], float]:
    """Verifica se un tecnico soddisfa i vincoli.

    Restituisce:
    - ammissibilità;
    - lista delle motivazioni;
    - distanza dal target.
    """

    reasons: list[str] = []
    technician_position = technician["position"]
    distance = dist(technician_position, target_position)

    if not technician["available"]:
        reasons.append("tecnico non disponibile")

    if required_competence not in technician["skills"]:
        reasons.append("competenza non compatibile")

    if distance > max_distance:
        reasons.append("distanza superiore al limite massimo")

    return len(reasons) == 0, reasons, distance


def assign_technician(
    device: str,
    target_position: tuple[int, int],
    max_distance: float = 20.0,
    fault: str | None = None,
) -> dict[str, Any]:
    """Assegna un tecnico rispettando i vincoli."""

    required_competence = get_required_competence(device, fault)
    
    feasible_technicians: list[dict[str, Any]] = []
    rejected_technicians: list[dict[str, Any]] = []

    for technician in TECHNICIANS:
        feasible, reasons, distance = is_feasible_technician(
            technician=technician,
            required_competence=required_competence,
            target_position=target_position,
            max_distance=max_distance,
        )

        candidate = {
            "name": technician["name"],
            "position": technician["position"],
            "distance": round(distance, 2),
            "skills": sorted(technician["skills"]),
        }

        if feasible:
            feasible_technicians.append(candidate)
        else:
            candidate["rejected_reasons"] = reasons
            rejected_technicians.append(candidate)

    if not feasible_technicians:
        return {
            "assigned": False,
            "required_competence": required_competence,
            "fault_used": fault,
            "reason": "nessun tecnico soddisfa tutti i vincoli",
            "rejected_technicians": rejected_technicians,
        }

    selected = sorted(
        feasible_technicians,
        key=lambda technician: technician["distance"],
    )[0]

    return {
        "assigned": True,
        "required_competence": required_competence,
        "fault_used": fault,
        "technician": selected["name"],
        "technician_position": selected["position"],
        "distance": selected["distance"],
        "feasible_technicians": feasible_technicians,
        "rejected_technicians": rejected_technicians,
    }


def main() -> None:
    """Esegue un piccolo test manuale del CSP."""

    result = assign_technician(
        device="router_laboratorio",
        target_position=(8, 2),
        max_distance=20.0,
    )

    print("CSP assignment result:")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()