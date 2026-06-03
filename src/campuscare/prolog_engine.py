"""Motore di consultazione della Knowledge Base Prolog.

Il modulo legge knowledge_base/kb.pl e consente query semplici sui fatti Prolog
generati dal progetto.

Non richiede SWI-Prolog o pyswip: interpreta solo un sottoinsieme controllato
dei fatti generati da prolog_export.py.

Serve a collegare la KB Prolog al resto della pipeline Python.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .prolog_export import PROLOG_KB_PATH, save_prolog_kb


@dataclass(frozen=True)
class PrologResult:
    """Risultato del controllo sulla KB Prolog."""

    device: str
    symptom: str
    fault: str | None
    intervention: str | None
    compatible_technicians: list[str]
    explanation: str


def parse_fact(line: str) -> tuple[str, list[str]] | None:
    """Esegue il parsing di un fatto Prolog semplice.

    Esempio:
    diagnosi(router_laboratorio, connessione_assente, router_down).
    ->
    ("diagnosi", ["router_laboratorio", "connessione_assente", "router_down"])
    """

    line = line.strip()

    if not line or line.startswith("%"):
        return None

    if ":-" in line:
        return None

    if not line.endswith("."):
        return None

    line = line[:-1]

    if "(" not in line or ")" not in line:
        return None

    predicate = line.split("(", 1)[0].strip()
    args_text = line.split("(", 1)[1].rsplit(")", 1)[0]

    args = [
        arg.strip()
        for arg in args_text.split(",")
        if arg.strip()
    ]

    return predicate, args


def load_facts(path: Path = PROLOG_KB_PATH) -> dict[str, list[list[str]]]:
    """Carica i fatti Prolog dal file kb.pl."""

    if not path.exists():
        save_prolog_kb(path)

    facts: dict[str, list[list[str]]] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = parse_fact(line)

        if parsed is None:
            continue

        predicate, args = parsed
        facts.setdefault(predicate, []).append(args)

    return facts


def query_diagnosis(
    device: str,
    symptom: str,
    facts: dict[str, list[list[str]]],
) -> str | None:
    """Cerca diagnosi(Dispositivo, Sintomo, Guasto)."""

    for fact_args in facts.get("diagnosi", []):
        fact_device, fact_symptom, fault = fact_args

        if fact_device == device and fact_symptom == symptom:
            return fault

    return None


def query_intervention(
    fault: str,
    facts: dict[str, list[list[str]]],
) -> str | None:
    """Cerca intervento(Guasto, Intervento)."""

    for fact_args in facts.get("intervento", []):
        fact_fault, intervention = fact_args

        if fact_fault == fault:
            return intervention

    return None


def query_fault_competence(
    fault: str,
    facts: dict[str, list[list[str]]],
) -> str | None:
    """Cerca competenza_guasto(Guasto, Competenza)."""

    for fact_args in facts.get("competenza_guasto", []):
        fact_fault, competence = fact_args

        if fact_fault == fault:
            return competence

    return None


def query_compatible_technicians(
    fault: str,
    facts: dict[str, list[list[str]]],
) -> list[str]:
    """Restituisce i tecnici compatibili con un guasto."""

    required_competence = query_fault_competence(fault, facts)

    if required_competence is None:
        return []

    available_technicians = {
        args[0]
        for args in facts.get("disponibile", [])
    }

    compatible = []

    for fact_args in facts.get("competenza_tecnico", []):
        technician, competence = fact_args

        if (
            technician in available_technicians
            and competence == required_competence
        ):
            compatible.append(technician)

    return sorted(compatible)


def analyze_with_prolog_kb(
    device: str,
    symptom: str,
    kb_path: Path = PROLOG_KB_PATH,
) -> PrologResult:
    """Analizza dispositivo e sintomo consultando kb.pl."""

    facts = load_facts(kb_path)

    fault = query_diagnosis(device, symptom, facts)

    if fault is None:
        return PrologResult(
            device=device,
            symptom=symptom,
            fault=None,
            intervention=None,
            compatible_technicians=[],
            explanation=(
                "Nessuna diagnosi trovata nella Knowledge Base Prolog "
                "per la coppia dispositivo/sintomo."
            ),
        )

    intervention = query_intervention(fault, facts)
    compatible_technicians = query_compatible_technicians(fault, facts)

    explanation = (
        f"La Knowledge Base Prolog associa ({device}, {symptom}) "
        f"al guasto {fault}."
    )

    return PrologResult(
        device=device,
        symptom=symptom,
        fault=fault,
        intervention=intervention,
        compatible_technicians=compatible_technicians,
        explanation=explanation,
    )


def main() -> None:
    """Esegue un test manuale della KB Prolog."""

    result = analyze_with_prolog_kb(
        device="router_laboratorio",
        symptom="connessione_assente",
    )

    print("Prolog KB result:")
    print("Device:", result.device)
    print("Symptom:", result.symptom)
    print("Fault:", result.fault)
    print("Intervention:", result.intervention)
    print("Compatible technicians:", result.compatible_technicians)
    print("Explanation:", result.explanation)


if __name__ == "__main__":
    main()