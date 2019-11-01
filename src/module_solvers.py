from enum import Enum
from debug import log
import windows_util as win_util

def color_in_range(img, pixel, low, high):
    red = img[:, :, 0]
    green = img[:, :, 1]
    blue = img[:, :, 2]
    return (red[pixel] >= low[0] and green[pixel] >= low[1]
            and blue[pixel] >= low[2] and red[pixel] <= high[0]
            and green[pixel] <= high[1] and blue[pixel] <= high[2])

def get_nth_wire(wires, index, color=None):
    wires_seen = 0
    curr_index = 0
    last_wire = 0
    for wire in wires:
        if wire > 0 and (color is None or color == wire):
            wires_seen += 1
            last_wire = curr_index
            if index != -1 and wires_seen >= index:
                return curr_index
        curr_index += 1
    return last_wire

def solve_simple_wires(img, **kwargs):
    log("Solving Simple Wires...")

    h, w, c = img.shape

    # Coordinates of wire endpoints.
    coords = [
        (40, 70), (80, 74), (118, 74),
        (157, 74), (198, 70), (240, 72)
    ]
    # Colords of wires.
    colors = [
        ((0, 0, 0), (20, 20, 20)),
        ((220, 220, 0), (255, 255, 20)),
        ((30, 30, 180), (100, 100, 255)),
        ((210, 210, 210), (255, 255, 255)),
        (((139, 0, 0)), (255, 99, 71))
    ]
    Colors = Enum("Colors", {"Black":0, "Yellow":1, "Blue":2, "White":3, "Red":4})
    num_wires = 0
    color_hist = [0, 0, 0, 0, 0]
    wire_hist = [0, 0, 0, 0, 0, 0]
    for i, coord in enumerate(coords):
        #cv2.rectangle(cv2_img, coord, (coord[0]+2, coord[1]+2), (0, 220, 0), 3)
        for j, (low, high) in enumerate(colors):
            if color_in_range(img, coord, low, high):
                color_hist[j] += 1
                wire_hist[i] = j
                num_wires += 1
                print(f"Wire {i+1} is {Colors(j)}")
                break

    serial_odd = kwargs.get("last_serial_odd", None)
    if serial_odd is None:
        return (False, "Serial number information not provided")

    if num_wires == 3:
        last_wire = get_nth_wire(wire_hist, -1)
        if color_hist[4] == 0: # There are no red wires.
            return get_nth_wire(wire_hist, 2) # Cut second wire.
        if wire_hist[last_wire] == 3: # Last wire is white.
            return get_nth_wire(wire_hist, -1) # Cut last wire
        if color_hist[2] > 1: # More than one blue wire.
            return get_nth_wire(wire_hist, -1, 2) # Cut last blue wire.
        return get_nth_wire(wire_hist, -1) # Cut the last wire.
    elif num_wires == 4: #TODO: Need to be able to read serial number to solve higher num of wires.
        if color_hist[4] > 1 and serial_odd: # More than one red wire + serial number odd.
            return get_nth_wire(wire_hist, -1, 4) # Cut last red wire.
        last_wire = get_nth_wire(wire_hist, -1)
        if color_hist[last_wire] == 1 and color_hist[4] == 0: # Last wire is yellow + no red wires.
            return get_nth_wire(wire_hist, 0) # Cut the first wire.
        if color_hist[2] == 1: # Exactly one blue wire.
            return get_nth_wire(wire_hist, 0) # Cut the first wire.
        if color_hist[1] > 1: # More than one yellow wire.
            return get_nth_wire(wire_hist, -1, 4) # Cut last red wire.
        return get_nth_wire(wire_hist, 1) # Cut the second wire.
    elif num_wires == 5:
        last_wire = get_nth_wire(wire_hist, -1)
        if wire_hist[last_wire] == 0 and serial_odd: # Last wire is black + serial number odd.
            return get_nth_wire(wire_hist, 3) # Cut the fourth wire.
        if color_hist[4] == 1 and color_hist[1] > 1: # One red wire + more than one yellow.
            return get_nth_wire(wire_hist, 0) # Cut the first wire.
        if color_hist[0] == 0: # No black wires.
            return get_nth_wire(wire_hist, 1) # Cut the second wire.
        return get_nth_wire(wire_hist, 0) # Cut the first wire.
    elif num_wires == 6:
        if color_hist[1] == 0 and serial_odd: # No yellow wires + serial number odd.
            return get_nth_wire(wire_hist, 2) # Cut the third wire.
        if color_hist[1] == 1 and color_hist[3] > 1: # One yellow + more than one white.
            return get_nth_wire(wire_hist, 3) # Cut the fourth wire.
        if color_hist[4] == 0: # No red wires.
            return get_nth_wire(wire_hist, -1) # Cut last wire.
        return get_nth_wire(wire_hist, 3) # Cut the fourth wire.
    else:
        return (False, "Invalid number of wires")

    return (False, "Could not identify solution")

def solve_button(img):
    log("Solving Button...")

def solve_symbols(img):
    log("Solving Symbols...")

def solve_simon(img):
    log("Solving Simon Says...")

def solve_wire_sequence(img):
    log("Solving Wire Sequence...")

def solve_complicated_wires(img):
    log("Solving Complicated Wires...")

def solve_memory(img):
    log("Solving Memory Game...")

def solve_whos_first(img):
    log("Solving Who's On First?...")

def solve_maze(img):
    log("Solving Maze...")

def solve_password(img):
    log("Solving Password...")

def solve_morse(img):
    log("Solving Morse...")
