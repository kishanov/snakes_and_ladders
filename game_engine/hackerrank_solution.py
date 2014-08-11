from engine import from_hackerrank_paths, set_extra_paths, create_pristine_board

INFINITY = 100000


def shortest_path(graph, start, end, visited=[], distances={}, predecessors={}):
    if start == end:
        path = []
        while end is not None:
            path.append(end)
            end = predecessors.get(end, None)
        return distances[start], path[::-1]

    if not visited:
        distances[start] = 0

    for neighbor in graph[start]:
        if neighbor not in visited:
            neighbor_distance = distances.get(neighbor, INFINITY)
            tentative_distance = distances[start] + graph[start][neighbor]
            if tentative_distance < neighbor_distance:
                distances[neighbor] = tentative_distance
                predecessors[neighbor] = start

    visited.append(start)
    unvisited = dict((k, distances.get(k, INFINITY)) for k in graph if k not in visited)
    closest_node = min(unvisited, key=unvisited.get)

    return shortest_path(graph, closest_node, end, visited, distances, predecessors)


INPUT = ["3",
         "3,7",
         "22,54",
         "79,17 67,7 89,25 69,23",
         "5,8",
         "28,64 24,98 14,76 4,56 54,92 18,90 20,68 46,84 8,80 48,88 44,60 26,96 52,66 34,72",
         "61,43 87,3 95,33 69,27 71,19 57,47 81,39 73,5 89,45 97,13 99,37",
         "4,9",
         "42,96 44,84 8,74 12,70 18,78",
         "61,11 99,15 91,43 75,45 93,33 67,9 59,51"]

if __name__ == "__main__":
    count = int(INPUT[0])

    for i in range(count):
        crap, ls, ss = INPUT[i * count + 1], INPUT[i * count + 2], INPUT[i * count + 3]
        ladders = from_hackerrank_paths(ls)
        snakes = from_hackerrank_paths(ss)
        shortcuts = snakes + ladders
        shortcuts_sources = [s["src"] for s in ladders]
        board = create_pristine_board()
        set_extra_paths(shortcuts, board)

        print shortest_path(board, 1, 100, [], {}, {})

