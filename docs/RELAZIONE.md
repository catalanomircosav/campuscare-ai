# CampusCare AI  
## Sistema intelligente basato su conoscenza per la gestione di segnalazioni tecniche universitarie

---

## 1. Introduzione

CampusCare AI è un prototipo di sistema intelligente basato su conoscenza progettato per supportare la gestione di segnalazioni tecniche in aule e laboratori universitari.

Il sistema riceve una segnalazione strutturata, ad esempio un problema relativo a un router di laboratorio, a un proiettore o a un impianto audio, e produce una risposta composta da diagnosi, priorità, intervento consigliato, tecnico assegnato e percorso operativo.

L’obiettivo non è realizzare un semplice classificatore Machine Learning, ma un piccolo Knowledge-Based System ibrido che integri rappresentazione della conoscenza, ragionamento simbolico, apprendimento supervisionato, vincoli e ricerca euristica.

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
- un intervento consigliato;
- una priorità stimata tramite regole;
- una priorità predetta tramite modello supervisionato;
- l’assegnazione di un tecnico compatibile;
- un percorso operativo calcolato con A*;
- una spiegazione delle decisioni.

Il dominio è stato scelto perché consente di rappresentare un problema realistico ma controllabile, in cui non basta una singola predizione statistica: è necessario combinare dati, conoscenza, vincoli e pianificazione.

---

## 3. Architettura del sistema

Il sistema è organizzato in moduli indipendenti ma integrati.

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

I moduli principali sono:

| Modulo | Ruolo |
|---|---|
| `domain.py` | Definizione del vocabolario del dominio |
| `generate_dataset.py` | Generazione del dataset sintetico |
| `create_ontology.py` | Creazione dell’ontologia OWL |
| `logic_engine.py` | Regole simboliche per diagnosi e priorità |
| `train_models.py` | Addestramento e valutazione dei modelli |
| `csp_assignment.py` | Assegnazione tecnico tramite vincoli |
| `astar.py` | Calcolo del percorso tramite A* |
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
- competenze;
- coordinate degli ambienti.

Il secondo livello è l’ontologia OWL generata dal modulo `create_ontology.py`.

L’ontologia contiene classi come:

- `Ambiente`;
- `Aula`;
- `Laboratorio`;
- `Biblioteca`;
- `Ufficio`;
- `Dispositivo`;
- `Sintomo`;
- `Guasto`;
- `Intervento`;
- `Tecnico`;
- `Competenza`.

Le principali proprietà rappresentate sono:

| Proprietà | Significato |
|---|---|
| `haDispositivo` | collega un ambiente a un dispositivo |
| `presentaSintomo` | collega un dispositivo a un sintomo |
| `causaGuasto` | collega un sintomo a un possibile guasto |
| `richiedeIntervento` | collega un guasto a un intervento |
| `haCompetenza` | collega un tecnico alle sue competenze |
| `richiedeCompetenza` | collega un dispositivo alla competenza richiesta |

Questa rappresentazione consente di separare la conoscenza del dominio dalla logica procedurale del sistema.

---

## 5. Generazione del dataset

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

La priorità non viene assegnata in modo casuale puro. Viene calcolata tramite regole di dominio basate su:

- importanza del dispositivo;
- gravità del sintomo;
- imminenza dell’evento;
- numero di utenti coinvolti;
- tipo di ambiente;
- temperatura;
- carico della rete.

È stata inoltre introdotta una piccola componente di rumore per simulare casi ambigui o valutazioni non perfette.

La distribuzione ottenuta nel dataset generato è:

| Priorità | Numero di esempi |
|---|---:|
| media | 355 |
| alta | 299 |
| bassa | 98 |
| critica | 48 |

La distribuzione non è perfettamente bilanciata, ma è coerente con il dominio: i casi critici sono meno frequenti rispetto a quelli medi o alti.

---

## 6. Motore simbolico

Il motore simbolico è implementato nel file `logic_engine.py`.

Il modulo svolge tre compiti:

1. diagnosi del guasto probabile;
2. stima della priorità tramite regole;
3. produzione di spiegazioni testuali.

Esempio di regola di diagnosi:

```text
se dispositivo = router_laboratorio
e sintomo = connessione_assente
allora guasto = router_down
```

Esempio di output simbolico:

```text
Fault: router_down
Intervention: riavvio_o_sostituzione_router
Rule priority: alta
```

Il sistema produce anche spiegazioni come:

- il laboratorio non ha connessione;
- è prevista una lezione o un esame;
- l’evento didattico è imminente;
- il dispositivo è essenziale per l’attività didattica;
- il sintomo compromette il servizio.

Questa parte rende il sistema più interpretabile rispetto a una classificazione puramente statistica.

---

## 7. Apprendimento supervisionato e valutazione

Il modulo `train_models.py` addestra modelli supervisionati per predire la priorità della segnalazione.

Sono stati confrontati quattro modelli:

- Decision Tree;
- Random Forest;
- Logistic Regression;
- Naive Bayes.

Le feature categoriche sono codificate tramite One-Hot Encoding, mentre le feature numeriche sono standardizzate.

La valutazione è stata effettuata tramite Stratified K-Fold Cross-Validation a 5 fold.

Le metriche considerate sono:

- accuracy;
- macro-F1;
- weighted-F1;
- precision macro;
- recall macro.

I risultati principali sono:

| Modello | Accuracy media ± std | Macro-F1 media ± std | Weighted-F1 media ± std |
|---|---:|---:|---:|
| Decision Tree | 0.6987 ± 0.0462 | 0.6302 ± 0.0610 | 0.6979 ± 0.0447 |
| Random Forest | 0.7225 ± 0.0140 | 0.5117 ± 0.0504 | 0.6839 ± 0.0186 |
| Logistic Regression | 0.7450 ± 0.0312 | 0.6055 ± 0.0540 | 0.7292 ± 0.0329 |
| Naive Bayes | 0.2388 ± 0.0528 | 0.2340 ± 0.0558 | 0.2017 ± 0.0727 |

Il modello operativo scelto è Logistic Regression, perché ottiene il miglior compromesso complessivo tra accuracy, macro-F1 e weighted-F1.

La scelta del modello non è quindi fissata a priori, ma deriva dal confronto sperimentale.

---

## 8. CSP per assegnazione del tecnico

Il modulo `csp_assignment.py` implementa un semplice problema di soddisfacimento di vincoli.

La variabile da assegnare è:

```text
tecnico_assegnato
```

Il dominio è l’insieme dei tecnici disponibili nel sistema.

I vincoli sono:

- il tecnico deve essere disponibile;
- il tecnico deve avere la competenza richiesta dal dispositivo;
- il tecnico deve trovarsi entro una distanza massima dal luogo della segnalazione.

Tra i tecnici che soddisfano i vincoli, il sistema sceglie quello più vicino.

Esempio:

```text
Dispositivo: router_laboratorio
Competenza richiesta: rete
Tecnico assegnato: tecnico_rete
Distanza: 1.0
```

Il modulo restituisce anche i tecnici scartati e le motivazioni dello scarto, ad esempio competenza non compatibile.

---

## 9. A* per pianificazione del percorso

Il modulo `astar.py` implementa l’algoritmo A* su una griglia.

La formulazione del problema è:

| Elemento | Descrizione |
|---|---|
| Stato iniziale | posizione del tecnico |
| Stato goal | posizione della stanza target |
| Azioni | movimento nelle quattro direzioni cardinali |
| Costo | costo unitario per ogni movimento |
| Euristica | distanza di Manhattan |
| Ostacoli | celle non attraversabili |

Esempio di percorso:

```text
[(7, 2), (8, 2)]
```

In questo caso il tecnico parte dalla posizione `(7, 2)` e raggiunge il laboratorio in `(8, 2)` con costo 1.

La rappresentazione a griglia è volutamente semplificata, ma permette di esplicitare chiaramente spazio degli stati, azioni, costo ed euristica.

---

## 10. Demo integrata

La demo integrata è implementata nel file `main.py`.

Il caso di esempio è:

```json
{
  "room_name": "Lab_1",
  "room_type": "laboratorio",
  "device": "router_laboratorio",
  "symptom": "connessione_assente",
  "event_in_minutes": 20,
  "users_involved": 72,
  "exam_or_lecture": 1,
  "temperature": 26.0,
  "network_load": 0.88
}
```

Il sistema produce:

- diagnosi simbolica: `router_down`;
- intervento: `riavvio_o_sostituzione_router`;
- priorità da regole: `alta`;
- priorità ML: `critica`;
- tecnico assegnato: `tecnico_rete`;
- percorso A*: `[(7, 2), (8, 2)]`.

La differenza tra priorità simbolica e priorità ML non viene considerata un errore, ma un’informazione utile: il sistema mantiene separati il ragionamento basato su regole e la predizione statistica.

---

## 11. Test

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

## 12. Limiti e sviluppi futuri

Il sistema è un prototipo e presenta alcuni limiti:

- il dataset è sintetico;
- l’ontologia è limitata;
- il campus è rappresentato come griglia semplificata;
- viene gestita una segnalazione alla volta;
- non è presente una rete bayesiana nella versione attuale;
- non vengono usati dati reali di ticketing.

Possibili sviluppi futuri:

- introduzione di una rete bayesiana per diagnosi probabilistica;
- gestione di più segnalazioni simultanee;
- ottimizzazione multi-obiettivo;
- uso di dati reali;
- interfaccia grafica o dashboard;
- espansione dell’ontologia;
- rappresentazione del campus come grafo realistico.

---

## 13. Conclusioni

CampusCare AI mostra come un problema pratico di gestione tecnica possa essere modellato tramite un sistema intelligente basato su conoscenza.

Il progetto integra:

- conoscenza di dominio;
- ontologia OWL;
- regole simboliche;
- apprendimento supervisionato;
- vincoli;
- ricerca euristica;
- spiegazione delle decisioni.

Il valore principale del prototipo non è la complessità di un singolo algoritmo, ma l’integrazione coerente di più tecniche in un sistema unico e verificabile.