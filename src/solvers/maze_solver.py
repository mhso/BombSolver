from enum import Enum
import features.maze as maze_features
from debug import log, LOG_DEBUG

DIRECTIONS = Enum("Directions", {"North":0, "South":1, "West":2, "East":3})
N = DIRECTIONS.North
S = DIRECTIONS.South
E = DIRECTIONS.East
W = DIRECTIONS.West

# Mazes. For each square in the maze,
# a tuple indicates the legal directions to go from there.
MAZES = {
    "MAZE_1" : [
        [(S, E), (W, E), (W, S), (S, E), (E, W), (W,)],
        [(N, S), (S, E), (N, W), (N, E), (E, W), (S, W)],
        [(N, S), (N, E), (S, W), (S, E), (W, E), (N, S, W)],
        [(N, S), (E,), (N, W, E), (N, W), (E,), (N, S, W)],
        [(N, S, E), (W, E), (S, W), (S, E), (W,), (N, S)],
        [(N, E), (W,), (N, E), (N, W), (E,), (N, W)]
    ],
    "MAZE_2" : [
        [(E,), (S, W, E), (W,), (S, E), (S, E, W), (W,)],
        [(S, E), (N, W), (S, E), (N, W), (N, E), (S, W)],
        [(N, S), (S, E), (N, W), (S, E), (W, E), (N, S, W)],
        [(N, S, E), (N, W), (S, E), (N, W), (S,), (N, S)],
        [(N, S), (S,), (N, S), (S, E), (N, W), (N, S)],
        [(N,), (N, E), (N, W), (N, E), (W, E), (N, W)]
    ],
    "MAZE_3" : [
        [(S, E), (W, E), (S, W), (S,), (S, E), (S, W)],
        [(N,), (S,), (N, S), (N, E), (N, W), (N, S)],
        [(S, E), (S, N, W), (N, S), (S, E), (S, W), (N, S)],
        [(N, S), (N, S), (N, S), (N, S), (N, S), (N, S)],
        [(N, S), (N, E), (N, W), (N, S), (N, S), (N, S)],
        [(N, E), (W, E), (W, E), (N, W), (N, E), (N, W)]
    ],
    "MAZE_4" : [
        [(S, E), (S, W), (E,), (W, E), (W, E), (S, W)],
        [(N, S), (N, S), (S, E), (W, E), (W, E), (N, S, W)],
        [(N, S), (N, E), (N, W), (S, E), (W,), (N, S)],
        [(N, S), (E,), (W, E), (N, W, E), (W, E), (N, S, W)],
        [(N, S, E), (W, E), (W, E), (W, E), (S, W), (N, S)],
        [(N, E), (W, E), (W,), (E,), (N, W), (N,)]
    ],
    "MAZE_5" : [
        [(E,), (W, E), (W, E), (W, E), (S, W, E), (S, W)],
        [(S, E), (W, E), (W, E), (S, W, E), (N, W), (N,)],
        [(N, S, E), (S, W), (E,), (N, W), (S, E), (S, W)],
        [(N, S), (N, E), (W, E), (S, W), (N,), (N, S)],
        [(N, S), (S, E), (W, E), (N, W, E), (W,), (N, S)],
        [(N,), (N, E), (W, E), (W, E), (W, E), (N, W)]
    ],
    "MAZE_6" : [
        [(S,), (S, E), (S, W), (E,), (S, W, E), (S, W)],
        [(N, S), (N, S), (N, S), (S, E), (N, W), (N, S)],
        [(N, S, E), (N, W), (N,), (N, S), (S, E), (N, W)],
        [(N, E), (S, W), (S, E), (N, S, W), (N, S), (S,)],
        [(S, E), (N, W), (N,), (N, S), (N, E), (N, S, W)],
        [(N, E), (W, E), (W, E), (N, W), (E,), (N, W)]
    ],
    "MAZE_7" : [
        [(S, E), (W, E), (W, E), (S, W), (S, E), (S, W)],
        [(N, S), (S, E), (W,), (N, E), (N, W), (N, S)],
        [(N, E), (N, W), (S, E), (W,), (S, E), (N, W)],
        [(S, E), (S, W), (N, S, E), (W, E), (N, W), (S,)],
        [(N, S), (N,), (N, E), (W, E), (S, W), (N, S)],
        [(N, E), (W, E), (W, E), (W, E), (N, W, E), (N, W)]
    ],
    "MAZE_8" : [
        [(S,), (S, E), (W, E), (S, W), (S, E), (S, W)],
        [(N, S, E), (N, W, E), (W,), (N, E), (N, W), (N, S)],
        [(N, S), (S, E), (W, E), (W, E), (S, W), (N, S)],
        [(N, S), (N, E), (S, W), (E,), (N, W, E), (N, W)],
        [(N, S), (S,), (N, E), (W, E), (W, E), (W,)],
        [(N, E), (N, W, E), (W, E), (W, E), (W, E), (W,)]
    ],
    "MAZE_9" : [
        [(S,), (S, E), (W, E), (W, E), (S, W, E), (S, W)],
        [(N, S), (N, S), (S, E), (W,), (N, S), (N, S)],
        [(N, S, E), (N, W, E), (N, W), (S, E), (N, W), (N, S)],
        [(N, S), (S,), (S, E), (N, W), (E,), (N, S, W)],
        [(N, S), (N, S), (N, S), (S, E), (S, W), (N,)],
        [(N, E), (N, W), (N, E), (N, W), (N, E), (W,)]
    ]
}

MAZE_NAMES = {
    (0, 1, 5, 2) : "MAZE_1",
    (4, 1, 1, 3) : "MAZE_2",
    (3, 3, 5, 3) : "MAZE_3",
    (0, 0, 0, 3) : "MAZE_4",
    (4, 2, 3, 5) : "MAZE_5",
    (4, 0, 2, 4) : "MAZE_6",
    (1, 0, 1, 5) : "MAZE_7",
    (3, 0, 2, 3) : "MAZE_8",
    (2, 1, 0, 4) : "MAZE_9",
}

def get_circles(details):
    """
    Return maze square coordinate of the two highlighted
    circles that identify the specific maze.
    """
    c_1, c_2 = details
    width = 25

    return (
        (int(c_1[0] // width), int(c_1[1] // width)),
        (int(c_2[0] // width), int(c_2[1] // width))
    )

def vertex(tupl):
    """
    Return the 'flattened' value of a coordinate.
    """
    x, y = tupl

    return y * 6 + x

def sort_circles(c_1, c_2):
    l = [c_1, c_2]
    l.sort(key=lambda t: vertex(t))

    return l[0] + l[1]

def solve_maze(maze, start, end):
    """
    Performs BFS search from 'start' to 'end'.
    """
    queue = [start]
    marked = [False] * 36
    marked[vertex(start)] = True
    edge_to = [None] * 36

    while queue != []:
        c_v = queue.pop(0)
        if c_v == end:
            break

        c_x, c_y = c_v
        directions = maze[c_y][c_x]
        up = (c_x, c_y-1)
        up_v = vertex(up)

        if N in directions and not marked[up_v]:
            marked[up_v] = True
            edge_to[up_v] = N
            queue.append(up)

        down = (c_x, c_y+1)
        down_v = vertex(down)

        if S in directions and not marked[down_v]:
            marked[down_v] = True
            edge_to[down_v] = S
            queue.append(down)

        left = (c_x-1, c_y)
        left_v = vertex(left)

        if W in directions and not marked[left_v]:
            marked[left_v] = True
            edge_to[left_v] = W
            queue.append(left)

        right = (c_x+1, c_y)
        right_v = vertex(right)

        if E in directions and not marked[right_v]:
            marked[right_v] = True
            edge_to[right_v] = E
            queue.append(right)

    return edge_to

def solve(img):
    """
    Solve the 'maze' module on the bomb.
    First identifies the start and end points,
    then identifies which of the 9 mazes it is.
    Finally, solves the maze using BFS.
    """
    start, end, contours = maze_features.get_maze_details(img)

    # Get the coordinates of the two circles that uniquely identify the maze.
    c_1, c_2 = get_circles(contours)
    log(f"Start square: {start}, end: {end}", LOG_DEBUG, "Maze")
    log(f"Circles: {c_1} & {c_2}", LOG_DEBUG, "Maze")

    circles = sort_circles(c_1, c_2)
    maze_name = MAZE_NAMES[circles]
    log(f"Maze: {maze_name}", LOG_DEBUG, "Maze")

    maze = MAZES[maze_name]

    directions = solve_maze(maze, start, end)
    pos = end
    direction = directions[vertex(pos)]
    path = []

    # Traverse the maze and save each direction taken to a list.
    while direction is not None:
        x, y = pos
        path.append(direction)

        if direction == N:
            pos = (x, y+1)

        elif direction == S:
            pos = (x, y-1)

        elif direction == W:
            pos = (x+1, y)

        else:
            pos = (x-1, y)

        direction = directions[vertex(pos)]

    return list(reversed(path))
