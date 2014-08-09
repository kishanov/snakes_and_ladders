from collections import defaultdict
from itertools import izip
import json
import os
from random import randint, shuffle
import operator

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
    """
    Utility function, which does the following conversion:
    [{'src': 32, 'dst': 62}, {'src': 42, 'dst': 68}, {'src': 12, 'dst': 98}] -> "32,62 42,68 12,98"

    :param paths:
    :return:
    """
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


def save_board_to_db(ladders, snakes):
    """
    Creates a single Node, representing a board in database.

    :param ladders:
    :param snakes:
    :return:
    """
    new_board = GRAPH_DB.create(node(snakes=to_hackerrank_paths(snakes),
                                     ladders=to_hackerrank_paths(ladders)))[0]
    new_board.add_labels("board")
    return new_board._id


def create_graph_in_db(board_id):
    board_from_db = get_board(board_id)
    board = set_extra_paths(board_from_db["ladders"] + board_from_db["snakes"], create_pristine_board())
    nodes_in_db = GRAPH_DB.create(*[node(value=n, board=board_id) for n in board.keys()])
    nodes = dict(izip(board.keys(), nodes_in_db))
    edges = []

    for src in board:
        if board[src]:
            for dst, cost in board[src].iteritems():
                edges.append(rel(nodes[src], "to", nodes[dst], cost=cost))

    GRAPH_DB.create(*edges)

    return {"start": nodes_in_db[0],
            "finish": nodes_in_db[-1],
            "board": board,
            "snakes": board_from_db["snakes"],
            "ladders": board_from_db["ladders"]}


def remove_temporary_nodes(board_id):
    """
    Cleans up all nodes and relations, created during board persistence in database.

    :param board_id:
    :return:
    """
    q1 = "MATCH (n)-[r]-() WHERE n.board = {0} DELETE n, r".format(board_id)
    q2 = "MATCH n WHERE n.board = {0} DELETE n".format(board_id)
    neo4j.CypherQuery(GRAPH_DB, q1).execute_one()
    neo4j.CypherQuery(GRAPH_DB, q2).execute_one()


def _get_node_id(board_id, node_value):
    query = "MATCH n WHERE n.value = {0} AND n.board={1} RETURN n".format(node_value, board_id)
    return neo4j.CypherQuery(GRAPH_DB, query).execute_one()._id


def get_src(jumps):
    return [jump["src"] for jump in jumps]


def _annotate_moves(moves, ladders, snakes):
    """
    Annotates simple path, calculated by Neo4J Dijkstra's algorithm call
    with meaningful, game-specific comments.

    :param moves: A list of all nodes in the path, starting from 1 and ending on 100
    :param ladders: ladders in [{"src":..., "dst":...}] representation
    :param snakes: snakes in [{"src":..., "dst":...}] representation
    :return: for each moves return a dict {"src":int, "dst":int, "action":string, "step":int}
    """
    solution = [{"src": moves[i], "dst": moves[i + 1]} for i in xrange(len(moves) - 1)]

    for move in solution:
        move["step"] = move["dst"] - move["src"]
        if move["src"] in get_src(ladders):
            move["action"] = "Climbs ladder"
        elif move["src"] in get_src(snakes):
            move["action"] = "Is digested by snake"
        else:
            move["action"] = "Rolls dice"

    return solution


def solve_board(board_id):
    """
    Finds a shortest path (sequence of dice rolls, snakes and ladders) to reach from 1 to 100.
    During it's execution temporarily create a graph which represents game board in Neo4J.
    The shortest path is found using Neo4J's implementation of Dijktra's algorithm.

    :param board_id:
    :return: Annotated sequence of moves to reach from 1 to 100.
    """
    temp_graph = create_graph_in_db(board_id)

    url = "{0}/db/data/node/{1}/path".format(DB_URL, temp_graph["start"]._id)

    query = {
        "to": "{0}/db/data/node/{1}".format(DB_URL, temp_graph["finish"]._id),
        "cost_property": "cost",
        "relationships": {
            "type": "to",
            "direction": "out"
        },
        "algorithm": "dijkstra"
    }

    r = requests.post(url, data=json.dumps(query))
    nodes = [neo4j.Node(n)["value"] for n in r.json()['nodes']]
    remove_temporary_nodes(board_id)
    return _annotate_moves(nodes, temp_graph["ladders"], temp_graph["snakes"])


def get_all_boards():
    """
    Finds all boards in database.

    :return: list of Py2Neo Node elements (each Node has a metadata about a board)
    """
    return [board for board in GRAPH_DB.find("board")]


def get_board(board_id):
    """
    Finds single board in database.

    :param board_id:
    :return: a dict of {"snakes": [...], "ladders": [...]}, each in {"src":int, "dst":int} format.
    """
    all_boards = [board for board in GRAPH_DB.find("board")]
    board = filter(lambda b: b._id == board_id, all_boards)[0]
    return {"ladders": from_hackerrank_paths(board["ladders"]),
            "snakes": from_hackerrank_paths(board["snakes"])}


def sample_board_1():
    ladders = from_hackerrank_paths("32,62 42,68 12,98")
    snakes = from_hackerrank_paths("95,13 97,25 93,37 79,27 75,19 49,47 67,17")
    return set_extra_paths(ladders + snakes, create_pristine_board())


def _gen_valid_destinations(sources, valid_destinations, comp_func):
    shortcuts = []

    for i in sources:
        valid_dst_for_i = [x for x in valid_destinations if comp_func(x, i)]
        j = randint(0, len(valid_dst_for_i) - 1)
        shortcuts.append({"src": i, "dst": valid_dst_for_i[j]})

    return shortcuts


def generate_board(ladders_count, snakes_count, board_size=100):
    valid_src_range = [i for i in xrange(2, board_size)]
    shuffle(valid_src_range)
    valid_destination_range = valid_src_range[(ladders_count + snakes_count):]

    return {"ladders": _gen_valid_destinations(valid_src_range[:ladders_count], valid_destination_range, operator.gt),
            "snakes": _gen_valid_destinations(valid_src_range[:ladders_count], valid_destination_range, operator.lt)}


# save_board_to_db(from_hackerrank_paths("32,62 42,68 12,98"),
# from_hackerrank_paths("95,13 97,25 93,37 79,27 75,19 49,47 67,17"))

# save_board_to_db(from_hackerrank_paths("32,62 44,66 22,58 34,60 2,90"),
# from_hackerrank_paths("85,7 63,31 87,13 75,11 89,33 57,5 71,15 55,25"))

# save_board_to_db(from_hackerrank_paths("8,52 6,80 26,42 2,72"),
# from_hackerrank_paths("51,19 39,11 37,29 81,3 59,5 79,23 53,7 43,33 77,21"))

# print win_game(2318)

