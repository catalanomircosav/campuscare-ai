"""Motore simbolico di CampusCare AI.

Questo modulo implementa una piccola base di regole per:
- diagnosticare il guasto probabile;
- stimare una priorità logica;
- produrre spiegazioni testuali.

Le regole sono volutamente semplici e leggibili, perché il loro scopo principale
è mostrare il ragionamento simbolico del sistema.
"""

from __future__ import annotations

from dataclasses import dataclass

from .domain import INTERVENTIONS


@dataclass(frozen=True)
class LogicResult:
    """Risultato prodotto dal motore simbolico."""

    fault: str
    intervention: str
    rule_priority: str
    explanations: list[str]


def diagnose_fault(device: str, symptom: str) -> tuple[str, str]:
    """Diagnostica il guasto probabile a partire da dispositivo e sintomo.

    Restituisce:
    - guasto ipotizzato;
    - spiegazione della regola attivata.
    """

    rules: dict[tuple[str, str], tuple[str, str]] = {
        (
            "proiettore",
            "nessun_segnale",
        ): (
            "cavo_hdmi_guasto",
            "Il proiettore non riceve segnale: possibile cavo HDMI guasto.",
        ),
        (
            "proiettore",
            "immagine_distorta",
        ): (
            "input_configurato_male",
            "L'immagine del proiettore è distorta: probabile configurazione errata dell'input.",
        ),
        (
            "pc_docente",
            "riavvii_frequenti",
        ): (
            "hardware_pc_guasto",
            "Il PC docente si riavvia frequentemente: possibile problema hardware.",
        ),
        (
            "pc_docente",
            "non_si_accende",
        ): (
            "alimentazione_guasta",
            "Il PC docente non si accende: possibile problema di alimentazione.",
        ),
        (
            "rete_wifi",
            "connessione_assente",
        ): (
            "router_down",
            "La rete Wi-Fi è assente: possibile router o access point non funzionante.",
        ),
        (
            "router_laboratorio",
            "connessione_assente",
        ): (
            "router_down",
            "Il laboratorio non ha connessione: probabile router di laboratorio non funzionante.",
        ),
        (
            "rete_wifi",
            "connessione_lenta",
        ): (
            "sovraccarico_rete",
            "La connessione è lenta: possibile sovraccarico della rete.",
        ),
        (
            "router_laboratorio",
            "connessione_lenta",
        ): (
            "sovraccarico_rete",
            "La rete del laboratorio è lenta: possibile congestione o sovraccarico.",
        ),
        (
            "climatizzatore",
            "temperatura_alta",
        ): (
            "climatizzazione_guasta",
            "La temperatura è alta e il climatizzatore è coinvolto: probabile guasto di climatizzazione.",
        ),
        (
            "impianto_audio",
            "audio_assente",
        ): (
            "impianto_audio_guasto",
            "L'audio è assente: probabile problema all'impianto audio.",
        ),
        (
            "presa_elettrica",
            "odore_bruciato",
        ): (
            "alimentazione_guasta",
            "È presente odore di bruciato: possibile guasto elettrico critico.",
        ),
        (
            "presa_elettrica",
            "non_si_accende",
        ): (
            "alimentazione_guasta",
            "La presa o il dispositivo collegato non si accende: possibile guasto elettrico.",
        ),
        (
            "lim",
            "nessun_segnale",
        ): (
            "input_configurato_male",
            "La LIM non riceve segnale: possibile configurazione errata o collegamento non corretto.",
        ),
    }

    default_fault = "nessun_guasto_critico"
    default_explanation = (
        "Nessuna regola specifica attivata: il caso richiede monitoraggio o verifica manuale."
    )

    return rules.get((device, symptom), (default_fault, default_explanation))


def infer_rule_priority(
    device: str,
    symptom: str,
    event_in_minutes: int,
    users_involved: int,
    exam_or_lecture: int,
) -> tuple[str, list[str]]:
    """Stima la priorità con regole simboliche.

    La priorità è calcolata tramite un punteggio cumulativo.
    Ogni regola attivata aggiunge una spiegazione.
    """

    score = 0
    explanations: list[str] = []

    if exam_or_lecture:
        score += 2
        explanations.append("è prevista una lezione o un esame")

    if event_in_minutes <= 30:
        score += 3
        explanations.append("l'evento didattico è imminente")
    elif event_in_minutes <= 90:
        score += 1
        explanations.append("l'evento didattico è vicino")

    if users_involved >= 80:
        score += 2
        explanations.append("sono coinvolti molti utenti")
    elif users_involved >= 35:
        score += 1
        explanations.append("è coinvolto un gruppo numeroso di utenti")

    if device in {
        "proiettore",
        "pc_docente",
        "rete_wifi",
        "router_laboratorio",
        "presa_elettrica",
    }:
        score += 2
        explanations.append("il dispositivo è essenziale per l'attività didattica")
    elif device in {
        "lim",
        "impianto_audio",
        "climatizzatore",
    }:
        score += 1
        explanations.append("il dispositivo incide sul servizio o sul comfort dell'aula")

    if symptom in {
        "odore_bruciato",
        "non_si_accende",
    }:
        score += 3
        explanations.append("il sintomo può indicare un guasto grave")
    elif symptom in {
        "connessione_assente",
        "nessun_segnale",
        "temperatura_alta",
    }:
        score += 2
        explanations.append("il sintomo compromette il servizio")
    elif symptom in {
        "connessione_lenta",
        "audio_assente",
        "immagine_distorta",
        "riavvii_frequenti",
    }:
        score += 1
        explanations.append("il sintomo degrada il servizio")

    if score >= 11:
        return "critica", explanations
    if score >= 8:
        return "alta", explanations
    if score >= 5:
        return "media", explanations
    return "bassa", explanations


def analyze_case(case: dict) -> LogicResult:
    """Analizza un caso usando le regole simboliche."""

    fault, fault_explanation = diagnose_fault(
        device=case["device"],
        symptom=case["symptom"],
    )

    rule_priority, priority_explanations = infer_rule_priority(
        device=case["device"],
        symptom=case["symptom"],
        event_in_minutes=int(case["event_in_minutes"]),
        users_involved=int(case["users_involved"]),
        exam_or_lecture=int(case["exam_or_lecture"]),
    )

    explanations = [fault_explanation]
    explanations.extend(priority_explanations)

    return LogicResult(
        fault=fault,
        intervention=INTERVENTIONS[fault],
        rule_priority=rule_priority,
        explanations=explanations,
    )


def main() -> None:
    """Esegue un piccolo test manuale del motore simbolico."""

    case = {
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

    result = analyze_case(case)

    print("Fault:", result.fault)
    print("Intervention:", result.intervention)
    print("Rule priority:", result.rule_priority)
    print("Explanations:")
    for explanation in result.explanations:
        print("-", explanation)


if __name__ == "__main__":
    main()