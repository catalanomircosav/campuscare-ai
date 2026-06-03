"""Ricerca A* su griglia per CampusCare AI.

Il modulo rappresenta il campus come una griglia bidimensionale.
Un tecnico deve raggiungere l'aula o il laboratorio della segnalazione.

Formulazione del problema:
- stato iniziale: posizione del tecnico;
- stato goal: posizione della stanza target;
- azioni: movimenti nelle quattro direzioni cardinali;
- costo: 1 per ogni movimento;
- euristica: distanza di Manhattan;
- ostacoli: celle non attraversabili.
"""

from __future__ import annotations

from heapq import heappop, heappush


GridPosition = tuple[int, int]


def manhattan_distance(a: GridPosition, b: GridPosition) -> int:
    """Calcola la distanza di Manhattan tra due celle."""

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(
    position: GridPosition,
    rows: int,
    cols: int,
) -> list[GridPosition]:
    """Restituisce i vicini validi di una posizione nella griglia."""

    row, col = position

    candidates = [
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]

    valid_neighbors = []

    for candidate_row, candidate_col in candidates:
        if 0 <= candidate_row < rows and 0 <= candidate_col < cols:
            valid_neighbors.append((candidate_row, candidate_col))

    return valid_neighbors


def reconstruct_path(
    came_from: dict[GridPosition, GridPosition],
    current: GridPosition,
) -> list[GridPosition]:
    """Ricostruisce il percorso dal goal allo start."""

    path = [current]

    while current in came_from:
        current = came_from[current]
        path.append(current)

    path.reverse()

    return path


def astar_search(
    start: GridPosition,
    goal: GridPosition,
    rows: int = 10,
    cols: int = 10,
    obstacles: set[GridPosition] | None = None,
) -> list[GridPosition]:
    """Esegue A* e restituisce il percorso trovato.

    Se non esiste un percorso, restituisce una lista vuota.
    """

    if obstacles is None:
        obstacles = set()

    if start in obstacles:
        raise ValueError("Start position cannot be an obstacle")

    if goal in obstacles:
        raise ValueError("Goal position cannot be an obstacle")

    open_set: list[tuple[int, GridPosition]] = []
    heappush(open_set, (0, start))

    came_from: dict[GridPosition, GridPosition] = {}

    g_score: dict[GridPosition, int] = {start: 0}
    f_score: dict[GridPosition, int] = {
        start: manhattan_distance(start, goal),
    }

    visited: set[GridPosition] = set()

    while open_set:
        _, current = heappop(open_set)

        if current in visited:
            continue

        visited.add(current)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current, rows, cols):
            if neighbor in obstacles:
                continue

            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + manhattan_distance(
                    neighbor,
                    goal,
                )

                heappush(open_set, (f_score[neighbor], neighbor))

    return []


def format_grid(
    path: list[GridPosition],
    start: GridPosition,
    goal: GridPosition,
    rows: int,
    cols: int,
    obstacles: set[GridPosition] | None = None,
) -> str:
    """Restituisce una rappresentazione testuale della griglia."""

    if obstacles is None:
        obstacles = set()

    path_set = set(path)
    lines = []

    for row in range(rows):
        cells = []

        for col in range(cols):
            position = (row, col)

            if position == start:
                cells.append("S")
            elif position == goal:
                cells.append("G")
            elif position in obstacles:
                cells.append("#")
            elif position in path_set:
                cells.append("*")
            else:
                cells.append(".")

        lines.append(" ".join(cells))

    return "\n".join(lines)


def main() -> None:
    """Esegue un piccolo test manuale di A*."""

    start = (7, 2)
    goal = (8, 2)

    obstacles = {
        (3, 3),
        (3, 4),
        (3, 5),
        (4, 5),
    }

    path = astar_search(
        start=start,
        goal=goal,
        rows=10,
        cols=10,
        obstacles=obstacles,
    )

    print("A* path:")
    print(path)
    print()
    print("Path length:", max(len(path) - 1, 0))
    print()
    print(format_grid(path, start, goal, rows=10, cols=10, obstacles=obstacles))


if __name__ == "__main__":
    main()