from collections import defaultdict

__author__ = 'kishanov'

import os


db_url = os.environ.get("GRAPHENEDB_URL")

# service_root = neo4j.ServiceRoot(URI(db_url).resolve("/"))
# graph_db = service_root.graph_db


def create_pristine_board(size=100):
    """
    Creates an empty game board (without snakes or ladders), represented as a graph.
    Graph is stored as adjacency list, where:
    - nodes: board cells
    - edges: connects cells, which you can reach from current cell with a throw of a dice
    - weights: dice's face value

    :param size: count of cells on a board.
    :return: {1: {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6}, 2: {3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6}, ...}
    """
    board = defaultdict(dict)

    for i in xrange(1, size + 1):
        board[i] = {j: (j - i) for j in xrange(min(i + 1, size + 1), min(i + 7, size + 1))}

    return board


def distance(src, dst):
    """
    :param src: Number on a board, between 1 and 100
    :param dst: Number on a board, between 1 and 100
    :return: 0 if processing a ladder, src - dst if processing a snake
    """
    return max(0, src - dst)


def set_extra_paths(paths, board):
    """
    Updates board graph with snakes or ladders coordinates info.

    :param paths: paths.true
    :param board: game board, represented
    :return: new board, with paths applied (doesn't modify given board, creates new)
    """
    new_board = board.copy()

    for path in paths:
        new_board[path["src"]][path["dst"]] = distance(path["src"], path["dst"])

    return new_board


def _parse_hackerrank_path(line):
    """
    Utility function, which does the following conversion:
    "32,62 42,68 12,98" -> [{'src': 32, 'dst': 62}, {'src': 42, 'dst': 68}, {'src': 12, 'dst': 98}]

    :param line: either snakes or ladders
    :return: a list of path source and destination pairs
    """
    tokens = line.split()
    paths = []

    for token in tokens:
        src, dst = map(int, token.split(","))
        paths.append({"src": src, "dst": dst})

    return paths


# ladders = _parse_hackerrank_path("32,62 42,68 12,98")
# snakes = _parse_hackerrank_path("95,13 97,25 93,37 79,27 75,19 49,47 67,17")
#
# print ladders
# print snakes
# print ladders + snakes
#
# print set_extra_paths(ladders + snakes, create_pristine_board())
