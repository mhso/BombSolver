import features.maze as maze_features
from debug import log

def solve(img):
    details = maze_features.get_maze_details(img)
    log(f"Maze start point: {details[0]}, end point: {details[1]}, circles: {details[2:]}")

    return details
