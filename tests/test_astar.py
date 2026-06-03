import pytest

from campuscare.astar import astar_search, manhattan_distance


def test_manhattan_distance():
    assert manhattan_distance((0, 0), (3, 4)) == 7
    assert manhattan_distance((7, 2), (8, 2)) == 1


def test_astar_finds_path():
    path = astar_search(
        start=(0, 0),
        goal=(2, 2),
        rows=3,
        cols=3,
        obstacles=set(),
    )

    assert path[0] == (0, 0)
    assert path[-1] == (2, 2)
    assert len(path) - 1 == 4


def test_astar_avoids_obstacles():
    obstacles = {
        (0, 1),
        (1, 1),
    }

    path = astar_search(
        start=(0, 0),
        goal=(0, 2),
        rows=3,
        cols=3,
        obstacles=obstacles,
    )

    assert path[0] == (0, 0)
    assert path[-1] == (0, 2)
    assert not any(position in obstacles for position in path)


def test_astar_rejects_invalid_start():
    with pytest.raises(ValueError):
        astar_search(
            start=(0, 0),
            goal=(2, 2),
            rows=3,
            cols=3,
            obstacles={(0, 0)},
        )