import features.needy_knob as knob_features
from debug import log, LOG_DEBUG

F = False
T = True
UP_SOLUTION_1 = [
    F, F, T, F, T, T,
    T, T, T, T, F, T
]
UP_SOLUTION_2 = [
    T, F, T, F, T, F,
    F, T, T, F, T, T
]
DOWN_SOLUTION_1 = [
    F, T, T, F, F, T,
    T, T, T, T, F, T
]
DOWN_SOLUTION_2 = [
    T, F, T, F, T, F,
    F, T, F, F, F, T
]
LEFT_SOLUTION_1 = [
    F, F, F, F, T, F,
    T, F, F, T, T, T
]
LEFT_SOLUTION_2 = [
    F, F, F, F, T, F,
    F, F, F, T, T, F
]
RIGHT_SOLUTION_1 = [
    T, F, T, T, T, T,
    T, T, T, F, T, F
]
RIGHT_SOLUTION_2 = [
    T, F, T, T, F, F,
    T, T, T, F, T, F
]

def get_desired_orientation(leds):
    if leds in (UP_SOLUTION_1, UP_SOLUTION_2):
        return 0
    if leds in (DOWN_SOLUTION_1, DOWN_SOLUTION_2):
        return 2
    if leds in (LEFT_SOLUTION_1, LEFT_SOLUTION_2):
        return 3
    if leds in (RIGHT_SOLUTION_1, RIGHT_SOLUTION_2):
        return 1
    return -1

def solve(img):
    directions = knob_features.get_directions(img)
    dial_orientation = knob_features.get_dial_orientation(img)
    leds = knob_features.get_led_states(img)
    if leds == [False] * 12:
        log("Needy Knob is not active, nothing needs doing.", LOG_DEBUG, "Needy Knob")
        return 0

    up_index = directions.index(True) # The clockwise index of the "UP" label.
    down_index = (up_index + 2) % 4
    right_index = (up_index + 1) % 4
    left_index = (down_index + 1) % 4

    # Align the knob directions by the "new" rotated view of the knob.
    aligned_dirs = [0] * 4
    aligned_dirs[0] = up_index
    aligned_dirs[1] = right_index
    aligned_dirs[2] = down_index
    aligned_dirs[3] = left_index

    # Get the desired clockwise position of the dial.
    desired_pos = get_desired_orientation(leds)
    dirs = ["Up", "Right", "Down", "Left"]

    for i in range(4):
        log(f"{dirs[i]} is at index '{aligned_dirs.index(i)}' clock-wise.")

    log(f"Knob needs to be in the '{dirs[desired_pos]}' position.", LOG_DEBUG, "Needy Knob")
    log(f"Knob Dial is pointing at position {dial_orientation}")
    turns = desired_pos - dial_orientation + up_index
    if turns < 0:
        turns = 0
    log(f"Turn knob {turns} times.", LOG_DEBUG, "Needy Knob")
    return turns
