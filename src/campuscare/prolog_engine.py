"""Motore di consultazione della Knowledge Base Prolog di CampusCare AI.

Questo modulo legge knowledge_base/kb.pl e risponde alle interrogazioni
applicando una procedura di RISOLUZIONE SLD (ragionamento top-down) sulle
clausole definite della KB: non si limita a cercare i fatti, ma valuta
anche le regole (clausole di Horn) tramite unificazione e backtracking.

Vengono quindi effettivamente utilizzate le regole della KB:
- puo_intervenire(Tecnico, Guasto)
- cura_per(Dispositivo, Sintomo, Intervento)
- tecnico_per(Dispositivo, Sintomo, Tecnico)

Il risolutore e' implementato in puro Python (nessuna dipendenza esterna) e
gestisce il sottoinsieme di Prolog usato dal progetto: clausole definite su
costanti e variabili, senza simboli di funzione. Cio' corrisponde al
ragionamento relazionale a regole (Datalog) e alla procedura di prova
top-down con variabili visti nel programma.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from .prolog_export import PROLOG_KB_PATH, save_prolog_kb


# Una literal e' rappresentata come (funtore, (arg1, arg2, ...)).
# Una clausola e' una coppia (testa, corpo), con corpo lista di literal.
# Una variabile e' una stringa che inizia con maiuscola o con '_'.
Literal = tuple
Clause = tuple
Substitution = dict


@dataclass(frozen=True)
class PrologResult:
    """Risultato del ragionamento sulla KB Prolog."""

    device: str
    symptom: str
    fault: str | None
    intervention: str | None
    compatible_technicians: list
    explanation: str


# --------------------------------------------------------------------------
# Parsing del programma Prolog (fatti + regole)
# --------------------------------------------------------------------------

def is_variable(term: str) -> bool:
    """Una variabile inizia con una lettera maiuscola o con '_'."""
    return bool(term) and (term[0].isupper() or term[0] == "_")


def split_top_level(text: str, separator: str) -> list:
    """Divide una stringa sul separatore, ignorando cio' che e' tra parentesi."""
    parts = []
    depth = 0
    current = ""

    for char in text:
        if char == "(":
            depth += 1
            current += char
        elif char == ")":
            depth -= 1
            current += char
        elif char == separator and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += char

    parts.append(current)

    return [part.strip() for part in parts if part.strip()]


def parse_literal(text: str) -> Literal:
    """Esegue il parsing di una literal del tipo funtore(arg1, arg2, ...)."""
    text = text.strip()

    functor = text.split("(", 1)[0].strip()
    args_text = text.split("(", 1)[1].rsplit(")", 1)[0]
    args = tuple(split_top_level(args_text, ","))

    return functor, args


def parse_program(text: str) -> list:
    """Esegue il parsing della KB Prolog in una lista di clausole definite.

    Gestisce sia i fatti sia le regole (clausole con ':-'), anche su piu' righe.
    Le righe di commento (che iniziano con '%') vengono ignorate.
    """
    cleaned_lines = []

    for line in text.splitlines():
        comment_index = line.find("%")
        if comment_index != -1:
            line = line[:comment_index]
        cleaned_lines.append(line)

    program_text = " ".join(cleaned_lines)
    raw_clauses = [c.strip() for c in program_text.split(".") if c.strip()]

    clauses = []

    for raw_clause in raw_clauses:
        if ":-" in raw_clause:
            head_text, body_text = raw_clause.split(":-", 1)
            head = parse_literal(head_text)
            body = [parse_literal(goal) for goal in split_top_level(body_text, ",")]
        else:
            head = parse_literal(raw_clause)
            body = []

        clauses.append((head, body))

    return clauses


def load_program(path: Path = PROLOG_KB_PATH) -> list:
    """Carica e analizza il programma Prolog da kb.pl."""
    if not path.exists():
        save_prolog_kb(path)

    return parse_program(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Unificazione e risoluzione SLD
# --------------------------------------------------------------------------

def walk(term: str, substitution: Substitution) -> str:
    """Segue le sostituzioni fino al valore corrente di un termine."""
    while is_variable(term) and term in substitution:
        term = substitution[term]
    return term


def unify_arguments(arg1: str, arg2: str, substitution: Substitution):
    """Unifica due argomenti atomici (costanti o variabili)."""
    arg1 = walk(arg1, substitution)
    arg2 = walk(arg2, substitution)

    if arg1 == arg2:
        return substitution

    if is_variable(arg1):
        extended = dict(substitution)
        extended[arg1] = arg2
        return extended

    if is_variable(arg2):
        extended = dict(substitution)
        extended[arg2] = arg1
        return extended

    return None


def unify(goal: Literal, head: Literal, substitution: Substitution):
    """Unifica due literal (stesso funtore e arieta', argomenti compatibili)."""
    goal_functor, goal_args = goal
    head_functor, head_args = head

    if goal_functor != head_functor or len(goal_args) != len(head_args):
        return None

    current = substitution

    for goal_arg, head_arg in zip(goal_args, head_args):
        result = unify_arguments(goal_arg, head_arg, current)
        if result is None:
            return None
        current = result

    return current


_rename_counter = [0]


def rename_clause(clause: Clause) -> Clause:
    """Rinomina le variabili di una clausola (standardizzazione a parte).

    Evita che le variabili di una regola entrino in conflitto con quelle
    della query o di altre attivazioni della stessa regola.
    """
    head, body = clause
    mapping = {}

    def rename_term(term: str) -> str:
        if not is_variable(term):
            return term
        if term not in mapping:
            _rename_counter[0] += 1
            mapping[term] = "_G%d" % _rename_counter[0]
        return mapping[term]

    def rename_literal(literal: Literal) -> Literal:
        functor, args = literal
        return functor, tuple(rename_term(arg) for arg in args)

    return rename_literal(head), [rename_literal(goal) for goal in body]


def solve(goals: list, program: list, substitution: Substitution) -> Iterator:
    """Procedura di prova top-down (risoluzione SLD) con backtracking."""
    if not goals:
        yield substitution
        return

    goal = goals[0]
    remaining = goals[1:]

    resolved_goal = (
        goal[0],
        tuple(walk(arg, substitution) for arg in goal[1]),
    )

    for clause in program:
        head, body = rename_clause(clause)

        unified = unify(resolved_goal, head, substitution)
        if unified is None:
            continue

        yield from solve(body + remaining, program, unified)


def query(goal: Literal, program: list) -> list:
    """Restituisce tutte le soluzioni (binding delle variabili) per un goal."""
    solutions = []
    seen = set()

    for substitution in solve([goal], program, {}):
        binding = {
            arg: walk(arg, substitution)
            for arg in goal[1]
            if is_variable(arg)
        }
        key = tuple(sorted(binding.items()))
        if key not in seen:
            seen.add(key)
            solutions.append(binding)

    return solutions


# --------------------------------------------------------------------------
# Interfaccia di alto livello usata dal resto della pipeline
# --------------------------------------------------------------------------

def analyze_with_prolog_kb(
    device: str,
    symptom: str,
    kb_path: Path = PROLOG_KB_PATH,
) -> PrologResult:
    """Analizza dispositivo e sintomo interrogando la KB Prolog per risoluzione.

    A differenza di una semplice ricerca di fatti, l'intervento e i tecnici
    compatibili sono derivati VALUTANDO le regole della KB:
    - cura_per/3 deriva l'intervento dalla diagnosi;
    - tecnico_per/3 (che attiva puo_intervenire/2) deriva i tecnici idonei.
    """
    program = load_program(kb_path)

    diagnosis_solutions = query(("diagnosi", (device, symptom, "Guasto")), program)

    if not diagnosis_solutions:
        return PrologResult(
            device=device,
            symptom=symptom,
            fault=None,
            intervention=None,
            compatible_technicians=[],
            explanation=(
                "Nessuna diagnosi derivabile dalla Knowledge Base Prolog "
                "per la coppia dispositivo/sintomo."
            ),
        )

    fault = diagnosis_solutions[0]["Guasto"]

    intervention_solutions = query(
        ("cura_per", (device, symptom, "Intervento")),
        program,
    )
    intervention = (
        intervention_solutions[0]["Intervento"] if intervention_solutions else None
    )

    technician_solutions = query(
        ("tecnico_per", (device, symptom, "Tecnico")),
        program,
    )
    compatible_technicians = sorted(
        {solution["Tecnico"] for solution in technician_solutions}
    )

    explanation = (
        "Per risoluzione sulla KB Prolog, da (%s, %s) si deriva il guasto %s; "
        "le regole cura_per e tecnico_per determinano intervento e tecnici idonei."
        % (device, symptom, fault)
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
    """Esegue un test manuale del motore di risoluzione sulla KB Prolog."""
    result = analyze_with_prolog_kb(
        device="router_laboratorio",
        symptom="connessione_assente",
    )

    print("Prolog KB result (risoluzione SLD):")
    print("Device:", result.device)
    print("Symptom:", result.symptom)
    print("Fault:", result.fault)
    print("Intervention:", result.intervention)
    print("Compatible technicians:", result.compatible_technicians)
    print("Explanation:", result.explanation)


if __name__ == "__main__":
    main()
