import features.memory as memory_features
from debug import log, LOG_DEBUG

# Solutions are ordered corresponding to rounds of the game.
# An entry corresponds to: Round -> Label on screen -> (number, literal, history)
SOLUTIONS = [
    [(2, False, False), (2, False, False), (3, False, False), (4, False, False)],
    [(4, True, False), (1, False, True), (1, False, False), (1, False, True)],
    [(2, True, True), (1, True, True), (3, False, False), (4, True, False)],
    [(1, False, True), (1, False, False), (2, False, True), (2, False, True)],
    [(1, True, True), (2, True, True), (4, True, True), (3, True, True)]
]

def solve(img, model, history):
    """
    Solves the 'memory' module on the bomb.
    Returns coords of the button to press + the label and index of that button.
    """
    numbers, coords = memory_features.get_labels(img, model)

    log(f"Number on screen: {numbers[0]}, Buttons: {numbers[1:]}", LOG_DEBUG, "Memory Game")
    num_on_screen = numbers[0]
    numbers = numbers[1:]
    (solution, literal, from_history) = SOLUTIONS[len(history)][num_on_screen-1]

    if from_history: # Grab either the label or position from a previous round.
        index = 0 if literal else 1
        hist_value = history[solution-1][index]

        if literal:
            # Button labeled 'hist_value'.
            index = numbers.index(hist_value)
            return coords[index], hist_value, index

        # Button at position 'hist_value'.
        return coords[hist_value], numbers[hist_value], hist_value

    if literal:
        # Button labeled 'solution'.
        index = numbers.index(solution)
        return coords[index], solution, index

    # Button at position 'solution'.
    return coords[solution-1], numbers[solution-1], solution-1
