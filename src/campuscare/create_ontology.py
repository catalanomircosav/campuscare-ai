"""Creazione dell'ontologia OWL di CampusCare AI.

L'ontologia rappresenta in modo esplicito il dominio del progetto:
ambienti, dispositivi, sintomi, guasti, interventi e tecnici.

Il file generato viene salvato in:
knowledge_base/campuscare_ontology.owl
"""

from __future__ import annotations

from pathlib import Path

from owlready2 import DataProperty, ObjectProperty, Thing, get_ontology

from .domain import (
    DEVICE_COMPETENCE,
    DEVICES,
    FAULTS,
    INTERVENTIONS,
    ROOM_TYPE_BY_NAME,
    SYMPTOMS,
    TECHNICIANS,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_DIR = ROOT_DIR / "knowledge_base"
ONTOLOGY_PATH = KNOWLEDGE_BASE_DIR / "campuscare_ontology.owl"

ONTOLOGY_IRI = "http://example.org/campuscare.owl#"


def normalize_name(value: str, prefix: str = "ind") -> str:
    """Converte una stringa in un nome adatto per un individuo OWL.

    Il prefisso evita collisioni tra nomi di classi e nomi di individui.
    """

    normalized = value.replace(" ", "_").replace("-", "_")
    return f"{prefix}_{normalized}"

def create_ontology(output_path: Path = ONTOLOGY_PATH) -> None:
    """Crea e salva l'ontologia OWL."""

    ontology = get_ontology(ONTOLOGY_IRI)

    with ontology:
        class Ambiente(Thing):
            pass

        class Aula(Ambiente):
            pass

        class Laboratorio(Ambiente):
            pass

        class Biblioteca(Ambiente):
            pass

        class Ufficio(Ambiente):
            pass

        class Dispositivo(Thing):
            pass

        class Sintomo(Thing):
            pass

        class Guasto(Thing):
            pass

        class Intervento(Thing):
            pass

        class Tecnico(Thing):
            pass

        class Competenza(Thing):
            pass

        class haDispositivo(ObjectProperty):
            domain = [Ambiente]
            range = [Dispositivo]

        class presentaSintomo(ObjectProperty):
            domain = [Dispositivo]
            range = [Sintomo]

        class causaGuasto(ObjectProperty):
            domain = [Sintomo]
            range = [Guasto]

        class richiedeIntervento(ObjectProperty):
            domain = [Guasto]
            range = [Intervento]

        class haCompetenza(ObjectProperty):
            domain = [Tecnico]
            range = [Competenza]

        class richiedeCompetenza(ObjectProperty):
            domain = [Dispositivo]
            range = [Competenza]

        class nome(DataProperty):
            domain = [Thing]
            range = [str]

    # Ambienti
    room_individuals = {}

    for room_name, room_type in ROOM_TYPE_BY_NAME.items():
        normalized_room_name = normalize_name(room_name)

        if room_type == "aula":
            room = ontology.Aula(normalized_room_name)
        elif room_type == "laboratorio":
            room = ontology.Laboratorio(normalized_room_name)
        elif room_type == "biblioteca":
            room = ontology.Biblioteca(normalized_room_name)
        elif room_type == "ufficio":
            room = ontology.Ufficio(normalized_room_name)
        else:
            room = ontology.Ambiente(normalized_room_name)

        room.nome.append(room_name)
        room_individuals[room_name] = room

    # Dispositivi
    device_individuals = {}

    for device in DEVICES:
        individual = ontology.Dispositivo(normalize_name(device))
        individual.nome.append(device)
        device_individuals[device] = individual

    # Sintomi
    symptom_individuals = {}

    for symptom in SYMPTOMS:
        individual = ontology.Sintomo(normalize_name(symptom))
        individual.nome.append(symptom)
        symptom_individuals[symptom] = individual

    # Guasti
    fault_individuals = {}

    for fault in FAULTS:
        individual = ontology.Guasto(normalize_name(fault))
        individual.nome.append(fault)
        fault_individuals[fault] = individual

    # Interventi
    intervention_individuals = {}

    for intervention in set(INTERVENTIONS.values()):
        individual = ontology.Intervento(normalize_name(intervention))
        individual.nome.append(intervention)
        intervention_individuals[intervention] = individual

    # Competenze
    competence_values = sorted(set(DEVICE_COMPETENCE.values()))
    competence_individuals = {}

    for competence in competence_values:
        individual = ontology.Competenza(normalize_name(competence))
        individual.nome.append(competence)
        competence_individuals[competence] = individual

    # Tecnici
    for technician in TECHNICIANS:
        technician_individual = ontology.Tecnico(normalize_name(technician["name"]))
        technician_individual.nome.append(technician["name"])

        for skill in technician["skills"]:
            technician_individual.haCompetenza.append(
                competence_individuals[skill]
            )

    # Collegamento ambienti-dispositivi.
    # In questa versione ogni ambiente contiene tutti i dispositivi principali.
    # È una semplificazione utile per il prototipo.
    for room in room_individuals.values():
        for device_individual in device_individuals.values():
            room.haDispositivo.append(device_individual)

    # Collegamento dispositivi-competenze
    for device, competence in DEVICE_COMPETENCE.items():
        device_individuals[device].richiedeCompetenza.append(
            competence_individuals[competence]
        )

    # Collegamento guasti-interventi
    for fault, intervention in INTERVENTIONS.items():
        fault_individuals[fault].richiedeIntervento.append(
            intervention_individuals[intervention]
        )

    # Collegamenti sintomo-guasto principali.
    symptom_fault_links = {
        "nessun_segnale": "cavo_hdmi_guasto",
        "immagine_distorta": "input_configurato_male",
        "connessione_assente": "router_down",
        "connessione_lenta": "sovraccarico_rete",
        "non_si_accende": "alimentazione_guasta",
        "odore_bruciato": "alimentazione_guasta",
        "temperatura_alta": "climatizzazione_guasta",
        "audio_assente": "impianto_audio_guasto",
        "riavvii_frequenti": "hardware_pc_guasto",
    }

    for symptom, fault in symptom_fault_links.items():
        symptom_individuals[symptom].causaGuasto.append(
            fault_individuals[fault]
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ontology.save(file=str(output_path), format="rdfxml")

    print(f"Ontology saved to: {output_path}")
    print(f"Classes: Ambiente, Aula, Laboratorio, Biblioteca, Ufficio, Dispositivo, Sintomo, Guasto, Intervento, Tecnico, Competenza")
    print(f"Rooms: {len(room_individuals)}")
    print(f"Devices: {len(device_individuals)}")
    print(f"Symptoms: {len(symptom_individuals)}")
    print(f"Faults: {len(fault_individuals)}")
    print(f"Interventions: {len(intervention_individuals)}")
    print(f"Competences: {len(competence_individuals)}")


def main() -> None:
    """Genera l'ontologia."""

    create_ontology()


if __name__ == "__main__":
    main()