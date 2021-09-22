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
    # Coordinates of wire endpoints.
    coords = [
        (40, 70), (80, 74), (118, 74),
        (157, 74), (198, 70), (240, 72)
    ]
    # Colors of wires.
    color_ranges = config.WIRE_COLOR_RANGE
    Colors = Enum("Colors", {"Black":0, "Yellow":1, "Blue":2, "White":3, "Red":4})
    num_wires = 0
    color_hist = [0, 0, 0, 0, 0] # Histogram of color occurences.
    wire_colors = [-1, -1, -1, -1, -1, -1] # Color of each wire. -1 means wire is missing.
    rgb = features_util.split_channels(img)
    radius = 5

    # Look through coordinates for each wire and check if a color matches that pixel.
    for i, coord in enumerate(coords):
        valid_colors = [0] * len(color_ranges)
        max_color_index = 0
        max_color_count = 0

        for j, (low, high) in enumerate(color_ranges): # Run through each possible color range.
            for m in range(coord[0]-radius, coord[0]+radius): # Look in a 5px radius around pixel.
                for n in range(coord[1]-radius, coord[1]+radius):
                    if features_util.color_in_range((m, n), rgb, low, high): # Color detected.
                        valid_colors[j] += 1 # Record occurence of current color.
                        if valid_colors[j] > max_color_count: # Track most seen color.
                            max_color_count = valid_colors[j]
                            max_color_index = j

        if max_color_count > 10: # Assume no wire is present if too few pixels matched a color.
            color_hist[max_color_index] += 1 # Record occurence of wire color.
            wire_colors[i] = max_color_index # Record what color the ith wire is.
            num_wires += 1
            log(f"Wire {i+1} is {Colors(max_color_index)}", LOG_DEBUG, "Wires")

    serial_odd = features.get("last_serial_odd", None)
    if num_wires > 3 and serial_odd is None:
        # Serial number was not previous detected correctly.
        # If we depend on this info to solve wires, raise an error.
        log("WARNING: Serial number information not provided", LOG_WARNING, "Wires")
        raise ValueError

    if num_wires == 3:
        if color_hist[Colors.Red.value] == 0: # There are no red wires.
            return get_nth_wire(wire_colors, 1), coords # Cut second wire.
        last_wire = get_nth_wire(wire_colors, -1)
        if wire_colors[last_wire] == Colors.White.value: # Last wire is white.
            return get_nth_wire(wire_colors, -1), coords # Cut last wire
        if color_hist[Colors.Blue.value] > 1: # More than one blue wire.
            return get_nth_wire(wire_colors, -1, Colors.Blue.value), coords # Cut last blue wire.
        return get_nth_wire(wire_colors, -1), coords # Cut the last wire.
    if num_wires == 4:
        if color_hist[Colors.Red.value] > 1 and serial_odd: # More than one red wire + serial number odd.
            return get_nth_wire(wire_colors, -1, Colors.Red.value), coords # Cut last red wire.
        last_wire = get_nth_wire(wire_colors, -1)
        # Last wire is yellow + no red wires.
        if wire_colors[last_wire] == Colors.Yellow.value and color_hist[Colors.Red.value] == 0:
            return get_nth_wire(wire_colors, 0), coords # Cut the first wire.
        if color_hist[Colors.Blue.value] == 1: # Exactly one blue wire.
            return get_nth_wire(wire_colors, 0), coords # Cut the first wire.
        if color_hist[Colors.Yellow.value] > 1: # More than one yellow wire.
            return get_nth_wire(wire_colors, -1, Colors.Red.value), coords # Cut last red wire.
        return get_nth_wire(wire_colors, 1), coords # Cut the second wire.
    if num_wires == 5:
        last_wire = get_nth_wire(wire_colors, -1)
        # Last wire is black + serial number odd.
        if wire_colors[last_wire] == Colors.Black.value and serial_odd:
            return get_nth_wire(wire_colors, 3), coords # Cut the fourth wire.
        # One red wire + more than one yellow.
        if color_hist[Colors.Red.value] == 1 and color_hist[Colors.Yellow.value] > 1:
            return get_nth_wire(wire_colors, 0), coords # Cut the first wire.
        if color_hist[Colors.Black.value] == 0: # No black wires.
            return get_nth_wire(wire_colors, 1), coords # Cut the second wire.
        return get_nth_wire(wire_colors, 0), coords # Cut the first wire.
    if num_wires == 6:
        if color_hist[Colors.Yellow.value] == 0 and serial_odd: # No yellow wires + serial number odd.
            return get_nth_wire(wire_colors, 2), coords # Cut the third wire.
        # One yellow + more than one white.
        if color_hist[Colors.Yellow.value] == 1 and color_hist[Colors.White.value] > 1:
            return get_nth_wire(wire_colors, 3), coords # Cut the fourth wire.
        if color_hist[Colors.Red.value] == 0: # No red wires.
            return get_nth_wire(wire_colors, -1), coords # Cut last wire.
        return get_nth_wire(wire_colors, 3), coords # Cut the fourth wire.
    log("WARNING: Invalid number of wires.", LOG_WARNING, "Wires")
    raise ValueError # Something went wrong.
