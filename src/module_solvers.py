from debug import log
import windows_util as win_util

def color_in_range(img, pixel, low, high):
    red = img[:, :, 0]
    green = img[:, :, 1]
    blue = img[:, :, 2]
    print(f"Color at area: {(red[pixel], green[pixel], blue[pixel])}")
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

def solve_simple_wires(img):
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
    color_names = ["black", "yellow", "blue", "white", "red"]
    num_wires = 0
    color_hist = [0, 0, 0, 0, 0]
    wire_hist = [0, 0, 0, 0, 0]
    for i, coord in enumerate(coords):
        #cv2.rectangle(cv2_img, coord, (coord[0]+2, coord[1]+2), (0, 220, 0), 3)
        for j, (low, high) in enumerate(colors):
            if color_in_range(img, coord, low, high):
                color_hist[j] += 1
                wire_hist[i] = j
                num_wires += 1
                print(f"Wire {i+1} is {color_names[j]}")
                break

    if num_wires == 3:
        last_wire = get_nth_wire(wire_hist, -1)
        if color_hist[4] == 0: # There are no red wires.
            return get_nth_wire(wire_hist, 2) # Cut second wire.
        elif wire_hist[last_wire] == 3: # Last wire is white.
            return get_nth_wire(wire_hist, -1) # Cut last wire
        elif color_hist[2] > 1: # More than one blue wire.
            return get_nth_wire(wire_hist, -1, 2) # Cut last blue wire.
        return get_nth_wire(wire_hist, -1) # Cut the last wire.
    # TODO: Need to be able to read serial number to solve higher num of wires.

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
