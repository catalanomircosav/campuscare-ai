# CampusCare AI

CampusCare AI è un prototipo di sistema intelligente basato su conoscenza per la gestione di segnalazioni tecniche in aule e laboratori universitari.

Il sistema analizza una segnalazione, stima la priorità, produce una diagnosi, consulta una Knowledge Base Prolog, stima probabilisticamente i guasti tramite Bayes, propone un intervento, assegna un tecnico compatibile e calcola un percorso operativo tramite A*.

Il progetto è sviluppato per l’esame di Ingegneria della Conoscenza.

---

## Obiettivo del progetto

L’obiettivo è realizzare un piccolo Knowledge-Based System ibrido che integri più tecniche di Intelligenza Artificiale e Ingegneria della Conoscenza.

Dato un caso come:

```text
Laboratorio, router non funzionante, connessione assente, lezione imminente, molti utenti coinvolti
```

il sistema produce:

- diagnosi simbolica del guasto;
- controllo tramite Knowledge Base Prolog;
- inferenza bayesiana sui guasti più probabili;
- intervento consigliato;
- priorità stimata tramite regole;
- priorità predetta tramite Machine Learning;
- assegnazione di un tecnico tramite vincoli;
- percorso calcolato con A*;
- spiegazione delle decisioni.

---

## Temi ricoperti

| Tema | Implementazione |
|---|---|
| Sistemi basati su conoscenza | Integrazione di conoscenza, regole, dati e decisioni |
| Ontologie | Rappresentazione OWL del dominio |
| Knowledge Base Prolog | Esportazione e consultazione di `knowledge_base/kb.pl` |
| Ragionamento simbolico | Regole per diagnosi, priorità e spiegazioni |
| Ragionamento probabilistico | Rete bayesiana semplice `Guasto -> Sintomo` |
| Apprendimento supervisionato | Classificazione della priorità delle segnalazioni |
| Valutazione dei modelli | Cross-validation con media e deviazione standard |
| Validazione dati | Controllo automatico della coerenza del dataset |
| CSP | Assegnazione del tecnico compatibile, guidata dal guasto diagnosticato |
| Ricerca euristica | A* per il percorso del tecnico |
| Confronto algoritmi | Confronto A* vs Dijkstra su griglia |
| CLI | Interfaccia testuale per casi personalizzati |
| Spiegabilità | Motivazioni testuali delle decisioni |

---

## Architettura del sistema

```text
Segnalazione
    |
    +--> Motore simbolico      -> diagnosi, priorità logica, spiegazioni
    |
    +--> KB Prolog             -> controllo diagnosi, intervento e tecnici compatibili
    |
    +--> Rete bayesiana        -> probabilità dei guasti dato il sintomo
    |
    +--> Modello ML            -> priorità predetta
    |
    +--> CSP                   -> tecnico assegnato in base al guasto
    |
    +--> A*                    -> percorso operativo
    |
    v
Output finale
```

---

## Struttura della repository

```text
campuscare-ai/
├── README.md
├── LICENSE
├── requirements.txt
├── pytest.ini
├── data/
├── knowledge_base/
│   ├── campuscare_ontology.owl
│   └── kb.pl
├── models/
├── plots/
├── results/
├── src/
│   └── campuscare/
│       ├── domain.py
│       ├── generate_dataset.py
│       ├── validate_dataset.py
│       ├── create_ontology.py
│       ├── logic_engine.py
│       ├── prolog_export.py
│       ├── prolog_engine.py
│       ├── bayes_engine.py
│       ├── train_models.py
│       ├── csp_assignment.py
│       ├── astar.py
│       ├── search_comparison.py
│       ├── generate_plots.py
│       ├── cli.py
│       └── main.py
├── docs/
└── tests/
    ├── test_astar.py
    └── test_logic_engine.py
```

---

## Installazione

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Dipendenze principali

- `pandas`
- `numpy`
- `scikit-learn`
- `joblib`
- `owlready2`
- `matplotlib`
- `pytest`

---

## Demo e comandi principali

Generare il dataset:

```bash
python -m src.campuscare.generate_dataset
```

Validare il dataset:

```bash
python -m src.campuscare.validate_dataset
```

Generare l’ontologia OWL:

```bash
python -m src.campuscare.create_ontology
```

Generare la Knowledge Base Prolog:

```bash
python -m src.campuscare.prolog_export
```

Consultare la Knowledge Base Prolog:

```bash
python -m src.campuscare.prolog_engine
```

Eseguire il motore simbolico:

```bash
python -m src.campuscare.logic_engine
```

Eseguire il motore bayesiano:

```bash
python -m src.campuscare.bayes_engine
```

Addestrare e valutare i modelli:

```bash
python -m src.campuscare.train_models
```

Generare i grafici:

```bash
python -m src.campuscare.generate_plots
```

Confrontare A* e Dijkstra:

```bash
python -m src.campuscare.search_comparison
```

Eseguire la demo integrata:

```bash
python -m src.campuscare.main
```

Eseguire la CLI interattiva:

```bash
python -m src.campuscare.cli
```

Eseguire i test:

```bash
python -m pytest
```

---

## Output generati

```text
data/segnalazioni.csv
knowledge_base/campuscare_ontology.owl
knowledge_base/kb.pl
results/metrics.json
results/search_comparison.csv
plots/priority_distribution.png
plots/model_accuracy.png
plots/model_macro_f1.png
plots/model_weighted_f1.png
models/priority_model.joblib
```

Il file `models/priority_model.joblib` è un artefatto binario rigenerabile tramite `train_models.py`.

---

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

Il progetto include inoltre:

- validazione automatica del dataset;
- consultazione della KB Prolog;
- confronto A* vs Dijkstra;
- test automatici con `pytest`.

---

## Licenza

Distribuito con licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.
