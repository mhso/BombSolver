from enum import Enum
from debug import log, LOG_DEBUG, LOG_WARNING
import features.util as features_util
import config

def get_nth_wire(wires, index, color=None):
    wires_seen = 0
    curr_index = 0
    last_wire = 0
    for wire in wires:
        if wire >= 0 and (color is None or color == wire):
            last_wire = curr_index
            if index != -1 and wires_seen >= index:
                return curr_index
            wires_seen += 1
        curr_index += 1
    return last_wire

def solve(img, features):
    h, w, c = img.shape

    # Coordinates of wire endpoints.
    coords = [
        (40, 70), (80, 74), (118, 74),
        (157, 74), (198, 70), (240, 72)
    ]
    # Colords of wires.
    color_ranges = config.WIRE_COLOR_RANGE
    Colors = Enum("Colors", {"Black":0, "Yellow":1, "Blue":2, "White":3, "Red":4})
    num_wires = 0
    color_hist = [0, 0, 0, 0, 0]
    wire_hist = [-1, -1, -1, -1, -1, -1]
    rgb = features_util.split_channels(img)
    for i, coord in enumerate(coords):
        for j, (low, high) in enumerate(color_ranges):
            if features_util.color_in_range(coord, rgb, low, high):
                color_hist[j] += 1
                wire_hist[i] = j
                num_wires += 1
                log(f"Wire {i+1} is {Colors(j)}", LOG_DEBUG, "Wires")
                break

    serial_odd = features.get("last_serial_odd", None)
    if serial_odd is None:
        log("WARNING: Serial number information not provided", LOG_WARNING, "Wires")
        raise ValueError # Something went wrong.

    if num_wires == 3:
        if color_hist[Colors.Red.value] == 0: # There are no red wires.
            return get_nth_wire(wire_hist, 1), coords # Cut second wire.
        last_wire = get_nth_wire(wire_hist, -1)
        if wire_hist[last_wire] == Colors.White.value: # Last wire is white.
            return get_nth_wire(wire_hist, -1), coords # Cut last wire
        if color_hist[Colors.Blue.value] > 1: # More than one blue wire.
            return get_nth_wire(wire_hist, -1, Colors.Blue.value), coords # Cut last blue wire.
        return get_nth_wire(wire_hist, -1), coords # Cut the last wire.
    if num_wires == 4:
        if color_hist[Colors.Red.value] > 1 and serial_odd: # More than one red wire + serial number odd.
            return get_nth_wire(wire_hist, -1, Colors.Red.value), coords # Cut last red wire.
        last_wire = get_nth_wire(wire_hist, -1)
        # Last wire is yellow + no red wires.
        if wire_hist[last_wire] == Colors.Yellow.value and color_hist[Colors.Red.value] == 0:
            return get_nth_wire(wire_hist, 0), coords # Cut the first wire.
        if color_hist[Colors.Blue.value] == 1: # Exactly one blue wire.
            return get_nth_wire(wire_hist, 0), coords # Cut the first wire.
        if color_hist[Colors.Yellow.value] > 1: # More than one yellow wire.
            return get_nth_wire(wire_hist, -1, Colors.Red.value), coords # Cut last red wire.
        return get_nth_wire(wire_hist, 1), coords # Cut the second wire.
    if num_wires == 5:
        last_wire = get_nth_wire(wire_hist, -1)
        # Last wire is black + serial number odd.
        if wire_hist[last_wire] == Colors.Black.value and serial_odd:
            return get_nth_wire(wire_hist, 3), coords # Cut the fourth wire.
        # One red wire + more than one yellow.
        if color_hist[Colors.Red.value] == 1 and color_hist[Colors.Yellow.value] > 1:
            return get_nth_wire(wire_hist, 0), coords # Cut the first wire.
        if color_hist[Colors.Black.value] == 0: # No black wires.
            return get_nth_wire(wire_hist, 1), coords # Cut the second wire.
        return get_nth_wire(wire_hist, 0), coords # Cut the first wire.
    if num_wires == 6:
        if color_hist[Colors.Yellow.value] == 0 and serial_odd: # No yellow wires + serial number odd.
            return get_nth_wire(wire_hist, 2), coords # Cut the third wire.
        # One yellow + more than one white.
        if color_hist[Colors.Yellow.value] == 1 and color_hist[Colors.White.value] > 1:
            return get_nth_wire(wire_hist, 3), coords # Cut the fourth wire.
        if color_hist[Colors.Red.value] == 0: # No red wires.
            return get_nth_wire(wire_hist, -1), coords # Cut last wire.
        return get_nth_wire(wire_hist, 3), coords # Cut the fourth wire.
    log("WARNING: Invalid number of wires.", LOG_WARNING, "Wires")
    raise ValueError # Something went wrong.
