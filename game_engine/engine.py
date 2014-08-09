from collections import defaultdict
from itertools import izip
import json
import os

from py2neo import node, rel
from py2neo import neo4j
from py2neo.packages.urimagic import URI
import requests


DB_URL = os.environ.get("GRAPHENEDB_URL")

service_root = neo4j.ServiceRoot(URI(DB_URL).resolve("/"))
GRAPH_DB = service_root.graph_db


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


def to_hackerrank_paths(paths):
    return " ".join(["{0},{1}".format(p["src"], p["dst"]) for p in paths])


def from_hackerrank_paths(line):
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


def persist_graph(ladders, snakes):
    board = set_extra_paths(ladders + snakes, create_pristine_board())
    new_board = GRAPH_DB.create(node(snakes=to_hackerrank_paths(snakes),
                                     ladders=to_hackerrank_paths(ladders)))[0]
    new_board.add_labels("board")
    board_id = new_board._id

    nodes_in_db = GRAPH_DB.create(*[node(value=n, board=board_id) for n in board.keys()])
    nodes = dict(izip(board.keys(), nodes_in_db))
    edges = []

    for src in board:
        if board[src]:
            for dst, cost in board[src].iteritems():
                edges.append(rel(nodes[src], "to", nodes[dst], cost=cost))

    GRAPH_DB.create(*edges)

    return board_id


def _get_node_id(board_id, node_value):
    query = "MATCH n WHERE n.value = {0} AND n.board={1} RETURN n".format(node_value, board_id)
    return neo4j.CypherQuery(GRAPH_DB, query).execute_one()._id


def win_game(board_id):
    start_id = _get_node_id(board_id, 1)
    finish_id = _get_node_id(board_id, 100)

    url = "{0}/db/data/node/{1}/path".format(DB_URL, start_id)

    query = {
        "to": "{0}/db/data/node/{1}".format(DB_URL, finish_id),
        "cost_property": "cost",
        "relationships": {
            "type": "to",
            "direction": "out"
        },
        "algorithm": "dijkstra"
    }

    r = requests.post(url, data=json.dumps(query))

    return [neo4j.Node(node)["value"] for node in r.json()['nodes']]


def get_all_boards():
    return [board for board in GRAPH_DB.find("board")]


def get_board(board_id):
    all_boards = [board for board in GRAPH_DB.find("board")]
    board = filter(lambda b: b._id == board_id, all_boards)[0]
    return {"ladders": from_hackerrank_paths(board["ladders"]),
            "snakes": from_hackerrank_paths(board["snakes"])}


def sample_board_1():
    ladders = from_hackerrank_paths("32,62 42,68 12,98")
    snakes = from_hackerrank_paths("95,13 97,25 93,37 79,27 75,19 49,47 67,17")
    return set_extra_paths(ladders + snakes, create_pristine_board())


# persist_graph(from_hackerrank_paths("32,62 42,68 12,98"),
# from_hackerrank_paths("95,13 97,25 93,37 79,27 75,19 49,47 67,17"))

# print get_board(908)

# print get_all_boards()
# persist_graph(board)
