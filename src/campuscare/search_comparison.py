"""Confronto tra A* e Dijkstra per CampusCare AI.

Il modulo confronta due algoritmi di ricerca su griglia:
- A*, che usa l'euristica Manhattan;
- Dijkstra, che non usa euristica.

Per ciascun algoritmo vengono misurati:
- lunghezza del percorso;
- numero di nodi espansi;
- tempo di esecuzione.

Il confronto serve a mostrare il vantaggio dell'euristica in un problema
di pianificazione del percorso.
"""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from pathlib import Path
from time import perf_counter
import csv

from .astar import GridPosition, manhattan_distance, get_neighbors, reconstruct_path


ROOT_DIR = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT_DIR / "results"
COMPARISON_PATH = RESULTS_DIR / "search_comparison.csv"


@dataclass(frozen=True)
class SearchResult:
    """Risultato di un algoritmo di ricerca."""

    algorithm: str
    path: list[GridPosition]
    path_length: int
    expanded_nodes: int
    execution_time_ms: float


def astar_with_stats(
    start: GridPosition,
    goal: GridPosition,
    rows: int,
    cols: int,
    obstacles: set[GridPosition],
) -> SearchResult:
    """Esegue A* restituendo anche statistiche di ricerca."""

    start_time = perf_counter()

    open_set: list[tuple[int, GridPosition]] = []
    heappush(open_set, (0, start))

    came_from: dict[GridPosition, GridPosition] = {}
    g_score: dict[GridPosition, int] = {start: 0}
    visited: set[GridPosition] = set()

    expanded_nodes = 0

    while open_set:
        _, current = heappop(open_set)

        if current in visited:
            continue

        visited.add(current)
        expanded_nodes += 1

        if current == goal:
            path = reconstruct_path(came_from, current)
            elapsed = (perf_counter() - start_time) * 1000
            return SearchResult(
                algorithm="astar",
                path=path,
                path_length=len(path) - 1,
                expanded_nodes=expanded_nodes,
                execution_time_ms=round(elapsed, 4),
            )

        for neighbor in get_neighbors(current, rows, cols):
            if neighbor in obstacles:
                continue

            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + manhattan_distance(neighbor, goal)
                heappush(open_set, (f_score, neighbor))

    elapsed = (perf_counter() - start_time) * 1000

    return SearchResult(
        algorithm="astar",
        path=[],
        path_length=0,
        expanded_nodes=expanded_nodes,
        execution_time_ms=round(elapsed, 4),
    )


def dijkstra_with_stats(
    start: GridPosition,
    goal: GridPosition,
    rows: int,
    cols: int,
    obstacles: set[GridPosition],
) -> SearchResult:
    """Esegue Dijkstra restituendo anche statistiche di ricerca."""

    start_time = perf_counter()

    open_set: list[tuple[int, GridPosition]] = []
    heappush(open_set, (0, start))

    came_from: dict[GridPosition, GridPosition] = {}
    distance: dict[GridPosition, int] = {start: 0}
    visited: set[GridPosition] = set()

    expanded_nodes = 0

    while open_set:
        current_distance, current = heappop(open_set)

        if current in visited:
            continue

        visited.add(current)
        expanded_nodes += 1

        if current == goal:
            path = reconstruct_path(came_from, current)
            elapsed = (perf_counter() - start_time) * 1000
            return SearchResult(
                algorithm="dijkstra",
                path=path,
                path_length=len(path) - 1,
                expanded_nodes=expanded_nodes,
                execution_time_ms=round(elapsed, 4),
            )

        for neighbor in get_neighbors(current, rows, cols):
            if neighbor in obstacles:
                continue

            new_distance = current_distance + 1

            if new_distance < distance.get(neighbor, float("inf")):
                came_from[neighbor] = current
                distance[neighbor] = new_distance
                heappush(open_set, (new_distance, neighbor))

    elapsed = (perf_counter() - start_time) * 1000

    return SearchResult(
        algorithm="dijkstra",
        path=[],
        path_length=0,
        expanded_nodes=expanded_nodes,
        execution_time_ms=round(elapsed, 4),
    )


def build_obstacles() -> set[GridPosition]:
    """Crea ostacoli per rendere il confronto più significativo."""

    obstacles = {
        (3, 3),
        (3, 4),
        (3, 5),
        (4, 5),
        (5, 5),
        (6, 5),
        (7, 5),
        (7, 4),
        (7, 3),
        (2, 7),
        (3, 7),
        (4, 7),
    }

    return obstacles


def compare_search_algorithms() -> list[SearchResult]:
    """Confronta A* e Dijkstra su uno scenario fisso."""

    rows = 12
    cols = 12
    start = (0, 0)
    goal = (10, 10)
    obstacles = build_obstacles()

    astar_result = astar_with_stats(
        start=start,
        goal=goal,
        rows=rows,
        cols=cols,
        obstacles=obstacles,
    )

    dijkstra_result = dijkstra_with_stats(
        start=start,
        goal=goal,
        rows=rows,
        cols=cols,
        obstacles=obstacles,
    )

    return [astar_result, dijkstra_result]


def save_results(results: list[SearchResult]) -> None:
    """Salva i risultati del confronto in CSV."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with COMPARISON_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "algorithm",
                "path_length",
                "expanded_nodes",
                "execution_time_ms",
            ],
        )

        writer.writeheader()

        for result in results:
            writer.writerow(
                {
                    "algorithm": result.algorithm,
                    "path_length": result.path_length,
                    "expanded_nodes": result.expanded_nodes,
                    "execution_time_ms": result.execution_time_ms,
                }
            )


def main() -> None:
    """Esegue il confronto e stampa i risultati."""

    results = compare_search_algorithms()
    save_results(results)

    print("Search comparison")
    print("-----------------")

    for result in results:
        print(f"Algorithm: {result.algorithm}")
        print(f"Path length: {result.path_length}")
        print(f"Expanded nodes: {result.expanded_nodes}")
        print(f"Execution time: {result.execution_time_ms} ms")
        print()

    print(f"Results saved to: {COMPARISON_PATH}")


if __name__ == "__main__":
    main()