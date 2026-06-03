"""Esportazione della Knowledge Base in formato Prolog.

Il modulo genera un file Prolog leggibile a partire dal dominio e dalle regole
simboliche del sistema.

Il file generato non è necessario per eseguire la pipeline Python, ma rappresenta
un artefatto esplicito di knowledge representation utile per documentazione,
controlli e possibili estensioni con un interprete Prolog.
"""

from __future__ import annotations

from pathlib import Path

from .domain import (
    DEVICE_COMPETENCE,
    DEVICES,
    FAULT_COMPETENCE,
    INTERVENTIONS,
    ROOM_TYPE_BY_NAME,
    SYMPTOMS,
    TECHNICIANS,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = ROOT_DIR / "knowledge_base"
PROLOG_KB_PATH = KNOWLEDGE_BASE_DIR / "kb.pl"


DIAGNOSIS_RULES = {
    ("proiettore", "nessun_segnale"): "cavo_hdmi_guasto",
    ("proiettore", "immagine_distorta"): "input_configurato_male",
    ("proiettore", "non_si_accende"): "alimentazione_guasta",
    ("pc_docente", "riavvii_frequenti"): "hardware_pc_guasto",
    ("pc_docente", "non_si_accende"): "alimentazione_guasta",
    ("pc_docente", "connessione_assente"): "router_down",
    ("pc_docente", "connessione_lenta"): "sovraccarico_rete",
    ("rete_wifi", "connessione_assente"): "router_down",
    ("rete_wifi", "connessione_lenta"): "sovraccarico_rete",
    ("router_laboratorio", "connessione_assente"): "router_down",
    ("router_laboratorio", "connessione_lenta"): "sovraccarico_rete",
    ("climatizzatore", "temperatura_alta"): "climatizzazione_guasta",
    ("climatizzatore", "non_si_accende"): "alimentazione_guasta",
    ("impianto_audio", "audio_assente"): "impianto_audio_guasto",
    ("impianto_audio", "non_si_accende"): "alimentazione_guasta",
    ("presa_elettrica", "odore_bruciato"): "alimentazione_guasta",
    ("presa_elettrica", "non_si_accende"): "alimentazione_guasta",
    ("lim", "nessun_segnale"): "input_configurato_male",
    ("lim", "non_si_accende"): "alimentazione_guasta",
}


def fact(name: str, *args: str) -> str:
    """Costruisce un fatto Prolog."""

    joined_args = ", ".join(args)
    return f"{name}({joined_args})."


def generate_prolog_kb() -> str:
    """Genera il contenuto testuale della KB Prolog."""

    lines: list[str] = []

    lines.append("% CampusCare AI - Knowledge Base Prolog")
    lines.append("% File generato automaticamente da src/campuscare/prolog_export.py")
    lines.append("")

    lines.append("% Ambienti")
    for room_name, room_type in sorted(ROOM_TYPE_BY_NAME.items()):
        lines.append(fact("ambiente", room_name.lower(), room_type))
    lines.append("")

    lines.append("% Dispositivi")
    for device in sorted(DEVICES):
        lines.append(fact("dispositivo", device))
    lines.append("")

    lines.append("% Sintomi")
    for symptom in sorted(SYMPTOMS):
        lines.append(fact("sintomo", symptom))
    lines.append("")

    lines.append("% Diagnosi simboliche: diagnosi(Dispositivo, Sintomo, Guasto).")
    for (device, symptom), fault in sorted(DIAGNOSIS_RULES.items()):
        lines.append(fact("diagnosi", device, symptom, fault))
    lines.append("")

    lines.append("% Interventi: intervento(Guasto, Intervento).")
    for fault, intervention in sorted(INTERVENTIONS.items()):
        lines.append(fact("intervento", fault, intervention))
    lines.append("")

    lines.append("% Competenze richieste dai dispositivi.")
    for device, competence in sorted(DEVICE_COMPETENCE.items()):
        lines.append(fact("competenza_dispositivo", device, competence))
    lines.append("")

    lines.append("% Competenze richieste dai guasti.")
    for fault, competence in sorted(FAULT_COMPETENCE.items()):
        lines.append(fact("competenza_guasto", fault, competence))
    lines.append("")

    lines.append("% Tecnici e competenze.")
    for technician in TECHNICIANS:
        technician_name = technician["name"]

        if technician["available"]:
            lines.append(fact("disponibile", technician_name))
        else:
            lines.append(fact("non_disponibile", technician_name))

        for skill in sorted(technician["skills"]):
            lines.append(fact("competenza_tecnico", technician_name, skill))
    lines.append("")

    lines.append("% Regole derivate.")
    lines.append("puo_intervenire(Tecnico, Guasto) :-")
    lines.append("    competenza_guasto(Guasto, Competenza),")
    lines.append("    competenza_tecnico(Tecnico, Competenza),")
    lines.append("    disponibile(Tecnico).")
    lines.append("")

    lines.append("cura_per(Dispositivo, Sintomo, Intervento) :-")
    lines.append("    diagnosi(Dispositivo, Sintomo, Guasto),")
    lines.append("    intervento(Guasto, Intervento).")
    lines.append("")

    lines.append("tecnico_per(Dispositivo, Sintomo, Tecnico) :-")
    lines.append("    diagnosi(Dispositivo, Sintomo, Guasto),")
    lines.append("    puo_intervenire(Tecnico, Guasto).")
    lines.append("")

    return "\n".join(lines)


def save_prolog_kb(output_path: Path = PROLOG_KB_PATH) -> None:
    """Salva la KB Prolog su file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_prolog_kb(), encoding="utf-8")


def main() -> None:
    """Genera il file kb.pl."""

    save_prolog_kb()

    print(f"Prolog KB saved to: {PROLOG_KB_PATH}")
    print("Example queries:")
    print("- diagnosi(router_laboratorio, connessione_assente, Guasto).")
    print("- cura_per(proiettore, non_si_accende, Intervento).")
    print("- tecnico_per(proiettore, non_si_accende, Tecnico).")


if __name__ == "__main__":
    main()