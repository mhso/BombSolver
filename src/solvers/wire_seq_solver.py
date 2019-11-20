from enum import Enum
import features.util as features_util
from debug import log, LOG_DEBUG

WIRE_TABLE = [
    [
        (2,), (1,), (0, 2), (1,), (0, 2), (0, 1, 2), (0, 1), (1,)
    ],
    [
        (1,), (0, 2), (1,), (0,), (1,), (1, 2), (2,), (0, 2), (0,)
    ],
    [
        (0, 1, 2), (0, 2), (1,), (0, 2), (1,), (1, 2), (0, 1), (2,), (2,)
    ]
]

def get_wire_colors(img):
    Colors = Enum("Colors", {"Red":0, "Blue":1, "Black":2})
    coords = [
        (91, 86), (102, 100), (102, 80),
        (127, 106), (138, 90), (146, 90),
        (174, 91), (173, 111), (184, 106)
    ]
    colors = [ # Red, Blue & Black.
        ((139, 0, 0), (255, 99, 71)),
        ((30, 30, 120), (100, 100, 255)),
        ((0, 0, 0), (10, 10, 10))
    ]
    rgb = features_util.split_channels(img)
    wires = [-1] * 3
    destinations = [-1] * 3
    coords_to_cut = [-1] * 3
    for i, pixel in enumerate(coords):
        for color, (lo, hi) in enumerate(colors):
            if features_util.color_in_range(pixel, rgb, lo, hi):
                letters = ["A", "B", "C"]
                log(f"{Colors(color)} wire from {i//3+1} to {letters[i%3]}")
                coords_to_cut[i // 3] = coords[i]
                wires[i // 3] = color
                destinations[i // 3] = i % 3
    return wires, destinations, coords_to_cut

def determine_cuts(wires, destinations, color_hist):
    Colors = Enum("Colors", {"Red":0, "Blue":1, "Black":2})
    wires_to_cut = [False] * 3
    for i, (wire, dest) in enumerate(zip(wires, destinations)):
        if wire == -1:
            continue
        time_seen = color_hist[wire]
        wires_to_cut[i] = dest in WIRE_TABLE[wire][time_seen]
        color_hist[wire] += 1
    return wires_to_cut, color_hist

def solve(img, wires_seen):
    wires, destinations, coords = get_wire_colors(img)
    assert len(wires) == 3
    assert len(destinations) == 3
    assert len(coords) == 3
    log(f"Wires: {wires}", LOG_DEBUG, module="Wire Sequence")
    log(f"Destinations: {destinations}", LOG_DEBUG, module="Wire Sequence")
    log(f"Coords: {coords}", LOG_DEBUG, module="Wire Sequence")
    cuts, color_hist = determine_cuts(wires, destinations, wires_seen)
    log(f"Wire hist: {wires_seen}", LOG_DEBUG, module="Wire Sequence")
    return (cuts, color_hist, coords)
