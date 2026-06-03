"""Motore bayesiano di CampusCare AI.

Il modulo implementa una rete bayesiana semplice:

    Guasto -> Sintomo

Lo scopo è stimare la probabilità dei possibili guasti dato un sintomo osservato.

Il modulo non sostituisce il motore simbolico o il modello ML: fornisce una
seconda opinione probabilistica utile nei casi incerti.
"""

from __future__ import annotations

from dataclasses import dataclass

from .domain import FAULTS, SYMPTOMS


@dataclass(frozen=True)
class BayesResult:
    """Risultato dell'inferenza bayesiana."""

    evidence_symptom: str
    probabilities: dict[str, float]
    most_probable_fault: str
    explanation: str


# Probabilità a priori P(Guasto).
# I valori sono scelti in modo coerente con il dominio:
# guasti comuni come sovraccarico rete o configurazione errata hanno priorità
# maggiore rispetto a guasti critici meno frequenti.
FAULT_PRIORS: dict[str, float] = {
    "cavo_hdmi_guasto": 0.11,
    "input_configurato_male": 0.13,
    "router_down": 0.12,
    "sovraccarico_rete": 0.14,
    "alimentazione_guasta": 0.09,
    "climatizzazione_guasta": 0.10,
    "impianto_audio_guasto": 0.10,
    "hardware_pc_guasto": 0.09,
    "nessun_guasto_critico": 0.12,
}


# Probabilità condizionali P(Sintomo | Guasto).
# Per ogni guasto vengono indicati i sintomi più compatibili.
# I sintomi non indicati esplicitamente ricevono una probabilità piccola.
LIKELIHOODS: dict[str, dict[str, float]] = {
    "cavo_hdmi_guasto": {
        "nessun_segnale": 0.65,
        "immagine_distorta": 0.20,
        "non_si_accende": 0.05,
    },
    "input_configurato_male": {
        "nessun_segnale": 0.35,
        "immagine_distorta": 0.45,
        "audio_assente": 0.10,
    },
    "router_down": {
        "connessione_assente": 0.70,
        "connessione_lenta": 0.15,
        "non_si_accende": 0.05,
    },
    "sovraccarico_rete": {
        "connessione_lenta": 0.65,
        "connessione_assente": 0.20,
    },
    "alimentazione_guasta": {
        "non_si_accende": 0.45,
        "odore_bruciato": 0.40,
        "riavvii_frequenti": 0.08,
    },
    "climatizzazione_guasta": {
        "temperatura_alta": 0.75,
        "non_si_accende": 0.10,
    },
    "impianto_audio_guasto": {
        "audio_assente": 0.70,
        "nessun_segnale": 0.10,
    },
    "hardware_pc_guasto": {
        "riavvii_frequenti": 0.55,
        "non_si_accende": 0.20,
        "immagine_distorta": 0.10,
    },
    "nessun_guasto_critico": {
        "connessione_lenta": 0.20,
        "audio_assente": 0.15,
        "immagine_distorta": 0.10,
        "temperatura_alta": 0.10,
    },
}


DEFAULT_LIKELIHOOD = 0.02


def validate_probabilities() -> None:
    """Controlla che priori e sintomi siano coerenti con il dominio."""

    missing_faults = set(FAULTS) - set(FAULT_PRIORS)
    extra_faults = set(FAULT_PRIORS) - set(FAULTS)

    if missing_faults:
        raise ValueError(f"Missing priors for faults: {sorted(missing_faults)}")

    if extra_faults:
        raise ValueError(f"Unknown faults in priors: {sorted(extra_faults)}")

    prior_sum = sum(FAULT_PRIORS.values())

    if abs(prior_sum - 1.0) > 0.0001:
        raise ValueError(f"Fault priors must sum to 1. Current sum: {prior_sum}")

    for fault, symptom_probabilities in LIKELIHOODS.items():
        if fault not in FAULTS:
            raise ValueError(f"Unknown fault in likelihoods: {fault}")

        for symptom in symptom_probabilities:
            if symptom not in SYMPTOMS:
                raise ValueError(f"Unknown symptom in likelihoods: {symptom}")


def likelihood(symptom: str, fault: str) -> float:
    """Restituisce P(Sintomo | Guasto)."""

    return LIKELIHOODS.get(fault, {}).get(symptom, DEFAULT_LIKELIHOOD)


def infer_fault_probabilities(symptom: str) -> dict[str, float]:
    """Calcola P(Guasto | Sintomo) usando la regola di Bayes."""

    if symptom not in SYMPTOMS:
        raise ValueError(f"Unknown symptom: {symptom}")

    validate_probabilities()

    unnormalized: dict[str, float] = {}

    for fault in FAULTS:
        unnormalized[fault] = likelihood(symptom, fault) * FAULT_PRIORS[fault]

    evidence_probability = sum(unnormalized.values())

    if evidence_probability == 0:
        raise ValueError(f"Evidence has zero probability: {symptom}")

    normalized = {
        fault: probability / evidence_probability
        for fault, probability in unnormalized.items()
    }

    return dict(
        sorted(
            normalized.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )


def analyze_symptom(symptom: str, top_k: int = 4) -> BayesResult:
    """Analizza un sintomo e restituisce i guasti più probabili."""

    probabilities = infer_fault_probabilities(symptom)

    top_probabilities = dict(list(probabilities.items())[:top_k])
    most_probable_fault = next(iter(probabilities))

    explanation = (
        f"Dato il sintomo '{symptom}', il guasto più probabile secondo "
        f"il modello bayesiano è '{most_probable_fault}'."
    )

    return BayesResult(
        evidence_symptom=symptom,
        probabilities=top_probabilities,
        most_probable_fault=most_probable_fault,
        explanation=explanation,
    )


def main() -> None:
    """Esegue un test manuale del motore bayesiano."""

    result = analyze_symptom("connessione_assente")

    print("Bayesian inference result:")
    print("Evidence symptom:", result.evidence_symptom)
    print("Most probable fault:", result.most_probable_fault)
    print("Probabilities:")

    for fault, probability in result.probabilities.items():
        print(f"- {fault}: {probability:.4f}")

    print("Explanation:", result.explanation)


if __name__ == "__main__":
    main()