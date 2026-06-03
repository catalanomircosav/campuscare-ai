# CampusCare AI  
## Sistema intelligente basato su conoscenza per la gestione di segnalazioni tecniche universitarie

---

## 1. Introduzione

CampusCare AI è un prototipo di sistema intelligente basato su conoscenza progettato per supportare la gestione di segnalazioni tecniche in aule e laboratori universitari.

Il sistema riceve una segnalazione strutturata, ad esempio un problema relativo a un router di laboratorio, a un proiettore o a un impianto audio, e produce una risposta composta da diagnosi, stima probabilistica dei guasti, priorità, intervento consigliato, tecnico assegnato e percorso operativo.

L’obiettivo non è realizzare un semplice classificatore Machine Learning, ma un piccolo Knowledge-Based System ibrido che integri rappresentazione della conoscenza, ragionamento simbolico, ragionamento probabilistico, apprendimento supervisionato, vincoli e ricerca euristica.

---

## 2. Obiettivo del sistema

Il problema affrontato riguarda la gestione di guasti tecnici in ambienti universitari.

Una segnalazione è descritta da informazioni come:

- ambiente in cui si verifica il problema;
- dispositivo coinvolto;
- sintomo osservato;
- tempo mancante a una lezione o a un esame;
- numero di utenti coinvolti;
- temperatura dell’ambiente;
- carico stimato della rete.

Dato un caso in input, il sistema deve produrre:

- una diagnosi simbolica del guasto probabile;
- una stima bayesiana dei guasti compatibili con il sintomo;
- un intervento consigliato;
- una priorità stimata tramite regole;
- una priorità predetta tramite modello supervisionato;
- l’assegnazione di un tecnico compatibile;
- un percorso operativo calcolato con A*;
- una spiegazione delle decisioni.

Il dominio è stato scelto perché consente di rappresentare un problema realistico ma controllabile, in cui non basta una singola predizione statistica: è necessario combinare dati, conoscenza, vincoli, incertezza e pianificazione.

---

## 3. Architettura del sistema

```text
Segnalazione
    |
    +--> Motore simbolico -> diagnosi, priorità logica, spiegazioni
    |
    +--> Rete bayesiana   -> probabilità dei guasti dato il sintomo
    |
    +--> Modello ML       -> priorità predetta
    |
    +--> CSP              -> tecnico assegnato in base al guasto
    |
    +--> A*               -> percorso operativo
    |
    v
Output finale
```

| Modulo | Ruolo |
|---|---|
| `domain.py` | Definizione del vocabolario del dominio |
| `generate_dataset.py` | Generazione del dataset sintetico |
| `validate_dataset.py` | Validazione della coerenza del dataset |
| `create_ontology.py` | Creazione dell’ontologia OWL |
| `logic_engine.py` | Regole simboliche per diagnosi e priorità |
| `bayes_engine.py` | Inferenza probabilistica sui guasti |
| `train_models.py` | Addestramento e valutazione dei modelli |
| `csp_assignment.py` | Assegnazione tecnico tramite vincoli |
| `astar.py` | Calcolo del percorso tramite A* |
| `search_comparison.py` | Confronto sperimentale A* vs Dijkstra |
| `generate_plots.py` | Generazione grafici per dataset e metriche |
| `cli.py` | Interfaccia testuale per casi personalizzati |
| `main.py` | Integrazione end-to-end |

---

## 4. Rappresentazione della conoscenza

La conoscenza di dominio è rappresentata in due modi complementari.

Il primo livello è il file `domain.py`, che contiene il vocabolario controllato del sistema:

- tipi di ambiente;
- dispositivi;
- sintomi;
- guasti;
- interventi;
- tecnici;
- competenze richieste dai dispositivi;
- competenze richieste dai guasti;
- coordinate degli ambienti.

Il secondo livello è l’ontologia OWL generata dal modulo `create_ontology.py`.

L’ontologia contiene classi come `Ambiente`, `Aula`, `Laboratorio`, `Dispositivo`, `Sintomo`, `Guasto`, `Intervento`, `Tecnico` e `Competenza`.

Le principali proprietà rappresentate sono:

| Proprietà | Significato |
|---|---|
| `haDispositivo` | collega un ambiente a un dispositivo |
| `presentaSintomo` | collega un dispositivo a un sintomo |
| `causaGuasto` | collega un sintomo a un possibile guasto |
| `richiedeIntervento` | collega un guasto a un intervento |
| `haCompetenza` | collega un tecnico alle sue competenze |
| `richiedeCompetenza` | collega un dispositivo alla competenza richiesta |

Dataset e ontologia derivano dallo stesso vocabolario controllato, riducendo incoerenze tra dati, regole e rappresentazione semantica.

---

## 5. Generazione e validazione del dataset

Il dataset è generato tramite lo script `generate_dataset.py`.

Ogni riga rappresenta una segnalazione tecnica. Le feature principali sono:

| Feature | Descrizione |
|---|---|
| `room_name` | nome dell’ambiente |
| `room_type` | tipo di ambiente |
| `device` | dispositivo coinvolto |
| `symptom` | sintomo osservato |
| `event_in_minutes` | minuti mancanti all’evento |
| `users_involved` | numero di utenti coinvolti |
| `exam_or_lecture` | presenza di lezione o esame |
| `temperature` | temperatura dell’ambiente |
| `network_load` | carico stimato della rete |
| `priority` | classe target |

La priorità non viene assegnata in modo casuale puro. Viene calcolata tramite regole di dominio basate su importanza del dispositivo, gravità del sintomo, imminenza dell’evento, numero di utenti coinvolti, tipo di ambiente, temperatura e carico della rete.

Distribuzione del dataset:

| Priorità | Numero di esempi |
|---|---:|
| media | 355 |
| alta | 299 |
| bassa | 98 |
| critica | 48 |

Il modulo `validate_dataset.py` controlla colonne, valori categorici, coerenza stanza/tipo e intervalli numerici. La validazione produce:

```text
Valid: True
Errors: none
Warnings: none
```

---

## 6. Motore simbolico

Il motore simbolico è implementato nel file `logic_engine.py`.

Il modulo svolge tre compiti:

1. diagnosi del guasto probabile;
2. stima della priorità tramite regole;
3. produzione di spiegazioni testuali.

Esempio:

```text
se dispositivo = proiettore
e sintomo = non_si_accende
allora guasto = alimentazione_guasta
```

Questa parte rende il sistema interpretabile rispetto a una classificazione puramente statistica.

---

## 7. Inferenza bayesiana

Il modulo `bayes_engine.py` implementa una rete bayesiana semplice con struttura:

```text
Guasto -> Sintomo
```

Lo scopo è stimare:

```text
P(Guasto | Sintomo)
```

dato un sintomo osservato.

Esempio per `connessione_assente`:

| Guasto | Probabilità |
|---|---:|
| `router_down` | 0.6625 |
| `sovraccarico_rete` | 0.2208 |
| `input_configurato_male` | 0.0205 |
| `nessun_guasto_critico` | 0.0189 |

Il modulo bayesiano non sostituisce il motore simbolico, ma fornisce una seconda opinione probabilistica.

---

## 8. Apprendimento supervisionato e valutazione

Il modulo `train_models.py` addestra modelli supervisionati per predire la priorità della segnalazione.

Sono stati confrontati:

- Decision Tree;
- Random Forest;
- Logistic Regression;
- Naive Bayes.

La valutazione è stata effettuata tramite Stratified K-Fold Cross-Validation a 5 fold.

| Modello | Accuracy media ± std | Macro-F1 media ± std | Weighted-F1 media ± std |
|---|---:|---:|---:|
| Decision Tree | 0.6987 ± 0.0462 | 0.6302 ± 0.0610 | 0.6979 ± 0.0447 |
| Random Forest | 0.7225 ± 0.0140 | 0.5117 ± 0.0504 | 0.6839 ± 0.0186 |
| Logistic Regression | 0.7450 ± 0.0312 | 0.6055 ± 0.0540 | 0.7292 ± 0.0329 |
| Naive Bayes | 0.2388 ± 0.0528 | 0.2340 ± 0.0558 | 0.2017 ± 0.0727 |

Il modello operativo scelto è Logistic Regression, perché ottiene il miglior compromesso complessivo tra accuracy, macro-F1 e weighted-F1.

Il modulo `generate_plots.py` produce grafici relativi alla distribuzione delle classi e al confronto tra modelli.

---

## 9. CSP per assegnazione del tecnico

Il modulo `csp_assignment.py` implementa un problema di soddisfacimento di vincoli.

La variabile da assegnare è `tecnico_assegnato`.

I vincoli sono:

- il tecnico deve essere disponibile;
- il tecnico deve avere la competenza richiesta;
- il tecnico deve trovarsi entro una distanza massima dal luogo della segnalazione.

Nella versione attuale, se il guasto è noto, la competenza richiesta viene ricavata dal guasto diagnosticato.

Esempio:

```text
Dispositivo: proiettore
Sintomo: non_si_accende
Guasto diagnosticato: alimentazione_guasta
Competenza richiesta: elettrico
Tecnico assegnato: manutentore_elettrico
```

Questo rende il sistema più integrato: la diagnosi simbolica influenza la decisione operativa successiva.

---

## 10. A* e confronto con Dijkstra

Il modulo `astar.py` implementa A* su una griglia.

| Elemento | Descrizione |
|---|---|
| Stato iniziale | posizione del tecnico |
| Stato goal | posizione della stanza target |
| Azioni | movimento nelle quattro direzioni cardinali |
| Costo | costo unitario per ogni movimento |
| Euristica | distanza di Manhattan |
| Ostacoli | celle non attraversabili |

Il modulo `search_comparison.py` confronta A* con Dijkstra.

| Algoritmo | Lunghezza percorso | Nodi espansi | Tempo |
|---|---:|---:|---:|
| A* | 20 | 109 | 0.1531 ms |
| Dijkstra | 20 | 128 | 0.1299 ms |

Entrambi trovano un percorso ottimo della stessa lunghezza. A* espande meno nodi grazie all’euristica Manhattan.

---

## 11. Demo integrata e CLI

La demo integrata è implementata nel file `main.py`.

Il caso di esempio produce:

- diagnosi simbolica: `router_down`;
- inferenza bayesiana: `router_down` come guasto più probabile;
- intervento: `riavvio_o_sostituzione_router`;
- priorità da regole: `alta`;
- priorità ML: `critica`;
- tecnico assegnato: `tecnico_rete`;
- percorso A*: `[(7, 2), (8, 2)]`.

Il file `cli.py` permette di inserire casi personalizzati da terminale. Nel caso `proiettore + non_si_accende`, il sistema diagnostica `alimentazione_guasta`, richiede competenza `elettrico` e assegna `manutentore_elettrico`.

---

## 12. Test

Sono stati implementati test minimi tramite `pytest`.

I test verificano:

- correttezza della diagnosi simbolica per un caso noto;
- comportamento del caso di default;
- correttezza della distanza di Manhattan;
- capacità di A* di trovare un percorso;
- capacità di A* di evitare ostacoli;
- gestione di uno start non valido.

L’esecuzione dei test produce:

```text
6 passed
```

---

## 13. Limiti e sviluppi futuri

Il sistema è un prototipo e presenta alcuni limiti:

- il dataset è sintetico;
- l’ontologia è limitata;
- il campus è rappresentato come griglia semplificata;
- viene gestita una segnalazione alla volta;
- le probabilità bayesiane sono definite manualmente;
- non vengono usati dati reali di ticketing.

Possibili sviluppi futuri:

- uso di dati reali;
- apprendimento delle probabilità bayesiane dai dati;
- gestione di più segnalazioni simultanee;
- ottimizzazione multi-obiettivo;
- interfaccia grafica o dashboard;
- espansione dell’ontologia;
- rappresentazione del campus come grafo realistico;
- reasoning OWL più avanzato.

---

## 14. Conclusioni

CampusCare AI mostra come un problema pratico di gestione tecnica possa essere modellato tramite un sistema intelligente basato su conoscenza.

Il progetto integra:

- conoscenza di dominio;
- ontologia OWL;
- regole simboliche;
- inferenza bayesiana;
- apprendimento supervisionato;
- validazione del dataset;
- vincoli;
- ricerca euristica;
- confronto sperimentale tra algoritmi di ricerca;
- spiegazione delle decisioni.

Il valore principale del prototipo non è la complessità di un singolo algoritmo, ma l’integrazione coerente di più tecniche in un sistema unico e verificabile.
