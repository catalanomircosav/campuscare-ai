# CampusCare AI

CampusCare AI è un prototipo di sistema intelligente basato su conoscenza per la gestione di segnalazioni tecniche in aule e laboratori universitari.

Il sistema analizza una segnalazione, stima la priorità, propone un intervento, assegna un tecnico compatibile e calcola un percorso operativo tramite A*.

Il progetto è sviluppato per l’esame di Ingegneria della Conoscenza.

---

## Obiettivo del progetto

L’obiettivo è realizzare un piccolo Knowledge-Based System ibrido che integri più tecniche di Intelligenza Artificiale e Ingegneria della Conoscenza.

Dato un caso come:

```text
Laboratorio, router non funzionante, connessione assente, lezione imminente, molti utenti coinvolti
```

Il sistema produce:

- diagnosi simbolica del guasto;
- intervento consigliato;
- priorità stimata tramite regole;
- priorità predetta tramite Machine Learning;
- assegnazione di un tecnico tramite vincoli;
- percorso calcolato con A*;
- spiegazione delle decisioni.

___

---

## Temi ricoperti

| Tema                         | Implementazione                                      |
| ---------------------------- | ---------------------------------------------------- |
| Sistemi basati su conoscenza | Integrazione di conoscenza, regole, dati e decisioni |
| Ontologie                    | Rappresentazione OWL del dominio                     |
| Ragionamento simbolico       | Regole per diagnosi, priorità e spiegazioni          |
| Apprendimento supervisionato | Classificazione della priorità delle segnalazioni    |
| Valutazione dei modelli      | Cross-validation con media e deviazione standard     |
| CSP                          | Assegnazione del tecnico compatibile                 |
| Ricerca euristica            | A* per il percorso del tecnico                       |
| Spiegabilità                 | Motivazioni testuali delle decisioni                 |

## Architettura del sistema
```text
Segnalazione
    |
    +--> Motore simbolico -> diagnosi, priorità logica, spiegazioni
    |
    +--> Modello ML       -> priorità predetta
    |
    +--> CSP              -> tecnico assegnato
    |
    +--> A*               -> percorso operativo
    |
    v
Output finale
```

## Struttura della repository
```text
campuscare-ai/
├── README.md
├── LICENSE
├── requirements.txt
├── pytest.ini
├── data/
├── knowledge_base/
├── models/
├── results/
├── src/
│   └── campuscare/
│       ├── domain.py
│       ├── generate_dataset.py
│       ├── create_ontology.py
│       ├── logic_engine.py
│       ├── train_models.py
│       ├── csp_assignment.py
│       ├── astar.py
│       └── main.py
├── docs/
└── tests/
    ├── test_astar.py
    └── test_logic_engine.py
```
___

## Installazione

- Creare e attivare un ambiente virtuale:

```
python -m venv .venv
source .venv/bin/activate
```

- Installare le dipendenze:

```
pip install -r requirements.txt
```
___

## Dipendenze principali
Il progetto utilizza:

- `pandas`
- `numpy`
- `scikit-learn`
- `joblib`
- `owlready2`
- `pytest`
___

## Demo
- Generare il dataset:

```bash
python -m src.campuscare.generate_dataset
```

- Generare l’ontologia OWL:

```bash
python -m src.campuscare.create_ontology
```

- Addestrare e valutare i modelli:

```bash
python -m src.campuscare.train_models
```

- Eseguire i test:

```
pytest
```

- Eseguire la demo integrata:

```
python -m src.campuscare.main
```

___

## Output generati

Durante l’esecuzione vengono generati:

- data/segnalazioni.csv
- knowledge_base/campuscare_ontology.owl
- models/priority_model.joblib
- results/metrics.json

## Valutazione

Il modulo di apprendimento supervisionato confronta:

- Decision Tree;
- Random Forest;
- Logistic Regression;
- Naive Bayes.

La valutazione usa Stratified K-Fold Cross-Validation a 5 fold.

Le metriche considerate sono:

- accuracy;
- macro-F1;
- weighted-F1;
- precision macro;
- recall macro.

I risultati vengono salvati in: `results/metrics.json`

Il modello operativo viene scelto in base al miglior compromesso tra le metriche, non fissato a priori.

___

### Licenza

Distribuito con licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.