from time import sleep, time
from sys import argv
from math import floor
from debug import log
import windows_util as win_util
from model import (module_classifier, character_classifier, symbol_classifier,
                   classifier_util, dataset_util)
from model.grab_img import screenshot
from solvers import (wire_solver, button_solver, symbols_solver, simon_solver,
                     wire_seq_solver, compl_wires_solver, memory_solver, whos_first_solver,
                     maze_solver, password_solver, morse_solver)
from features.serial_number import get_serial_number
from features.bomb_duration import get_bomb_duration
from features.util import convert_to_cv2
from features.indicator import get_indicator_features
from features.light_monitor import LightMonitor
import config

LIGHT_MONITOR = None

def sleep_until_start():
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

def start_level():
    SW, SH = win_util.get_screen_size()
    win_util.click(int(SW - SW/2.6), int(SH - SH/3.3))

def await_level_start():
    sleep(16.4)

def inspect_side(mx, my, sx, sy, sw, sh):
    win_util.mouse_move(mx, my)
    sleep(0.5)
    SC = screenshot(sx, sy, sw, sh)
    sleep(0.2)
    return SC

def flip_bomb(SW, SH):
    mid_x = SW // 2
    mid_y = SH // 2
    win_util.click(SW - 100, 100, btn="right")
    sleep(0.5)
    win_util.click(mid_x, mid_y + (mid_y // 8))
    sleep(0.2)
    win_util.mouse_down(mid_x, mid_y, btn="right")
    sleep(0.5)
    win_util.mouse_move(SW - int(SW / 4.4), mid_y + (mid_y // 9))
    sleep(0.5)

def inspect_bomb():
    SW, SH = win_util.get_screen_size()
    mid_x = SW // 2
    mid_y = SH // 2
    win_util.click(mid_x, mid_y + (mid_y // 8))
    sleep(0.5)
    # Inspect front of bomb.
    front_img = screenshot(460, 220, 1000, 640)
    sleep(0.2)
    # Rotate bomb.
    win_util.mouse_down(mid_x, mid_y, btn="right")
    sleep(0.2)
    # Inspect right side.
    right_img = inspect_side(SW - int(SW / 2.74), mid_y + int(mid_y / 8), 755, 60, 480, 900)
    # Inspect left side.
    left_img = inspect_side(int(SW / 2.76), mid_y + int(mid_y / 8), 755, 60, 480, 900)
    # Inspect top side.
    top_img = inspect_side(int(SW / 2.75), SH, 720, 0, 480, SH)
    # Inspect bottom side.
    bottom_img = inspect_side(int(SW / 2.75), 0, 720, 0, 480, SH)
    # Inspect back of bomb.
    win_util.mouse_up(mid_x, mid_y, btn="right")
    sleep(0.5)
    flip_bomb(SW, SH)
    back_img = screenshot(460, 220, 1000, 640)
    sleep(0.4)
    win_util.mouse_up(mid_x, mid_y, btn="right")
    return (back_img, front_img, left_img, right_img, top_img, bottom_img)

def partition_main_sides(images):
    side_partitions = []
    for img in images:
        sides = []
        sides.append(img.crop((105, 60, 361, 316)))
        sides.append(img.crop((384, 62, 640, 318)))
        sides.append(img.crop((658, 62, 914, 318)))
        sides.append(img.crop((86, 344, 342, 600)))
        sides.append(img.crop((373, 344, 629, 600)))
        sides.append(img.crop((648, 344, 904, 600)))
        side_partitions.extend(sides)
    return side_partitions

def partition_short_sides(images):
    side_partitions = []
    for img in images:
        sides = []
        sides.append(img.crop((30, 168, 202, 410)))
        sides.append(img.crop((238, 165, 400, 415)))
        sides.append(img.crop((30, 450, 200, 712)))
        sides.append(img.crop((238, 450, 400, 712)))
        side_partitions.extend(sides)
    return side_partitions

def partition_long_sides(images):
    side_partitions = []
    # Left side.
    side_partitions.append(images[0].crop((98, 144, 242, 356)))
    side_partitions.append(images[0].crop((282, 144, 425, 354)))
    side_partitions.append(images[0].crop((90, 388, 240, 714)))
    side_partitions.append(images[0].crop((282, 388, 430, 714)))
    side_partitions.append(images[0].crop((90, 748, 240, 956)))
    side_partitions.append(images[0].crop((282, 748, 430, 956)))
    # Right side.
    side_partitions.append(images[1].crop((100, 136, 240, 300)))
    side_partitions.append(images[1].crop((270, 134, 420, 300)))
    side_partitions.append(images[1].crop((90, 344, 240, 650)))
    side_partitions.append(images[1].crop((276, 344, 434, 650)))
    side_partitions.append(images[1].crop((80, 694, 240, 926)))
    side_partitions.append(images[1].crop((274, 690, 440, 926)))
    return side_partitions

def partition_sides(images):
    main_sides = partition_main_sides(images[0:2])
    short_sides = partition_short_sides(images[2:4])
    long_sides = partition_long_sides(images[4:6])
    return (main_sides, short_sides, long_sides)

def identify_side_features(sides, model):
    predictions = [0] * 32
    i = 0
    for side in sides:
        for img in side:
            converted = dataset_util.reshape(convert_to_cv2(img), config.MODULE_INPUT_DIM[1:])
            pred = module_classifier.predict(model, converted)
            predict_label = classifier_util.get_best_prediction(pred)[0]
            predictions[i] = predict_label
            i += 1
    return predictions

def print_features(features):
    for feature, amount in enumerate(features):
        print(f"{module_classifier.LABELS[feature]} - {amount}")

def get_time_remaining(time_started, minutes, seconds):
    return floor((minutes * 60 + seconds) - (time() - time_started))

def serial_contains_vowel(serial_num):
    vowels = ["A", "E", "I", "U", "Y"]
    for c in serial_num:
        if c in vowels:
            return True
    return False

def extract_serial_number_features(serial_num):
    features = {}
    try:
        features["last_serial_odd"] = (int(serial_num[-1])) % 2 == 1
    except ValueError:
        log(f"WARNING: Misread last character of serial number.", config.LOG_WARNING)
        features["last_serial_odd"] = False
    features["contains_vowel"] = serial_contains_vowel(serial_num)
    return features

def extract_side_features(sides, labels, character_model):
    index = 0
    features = {
        "indicators" : [],
        "parallel_port" : False,
        "batteries" : 0
    }
    for side in sides:
        for img in side:
            cv2_img = convert_to_cv2(img)
            if labels[index] == 1:
                features["batteries"] += 1
            elif labels[index] == 2:
                features["batteries"] += 2
            elif labels[index] == 3: # Serial number.
                serial_num = get_serial_number(cv2_img, character_model)
                if serial_num is None:
                    log(f"Serial number could not be determined.", config.LOG_WARNING)
                    index += 1
                    continue
                log(f"Serial number: {serial_num}", verbose=config.LOG_DEBUG)
                features["serial_number"] = serial_num
                serial_features = extract_serial_number_features(serial_num)
                features.update(serial_features)
            elif labels[index] == 5: # Parallel port.
                features["parallel_port"] = True
            elif labels[index] == 6: # Indicator of some kind.
                lit, text = get_indicator_features(cv2_img, character_model)
                desc = "lit_" + text if lit else "unlit_" + text
                features["indicators"].append(desc)
            index += 1
    return features

def select_module(module):
    SW, SH = win_util.get_screen_size()
    start_x = SW * 0.35
    start_y = SH * 0.35
    offset_x = 300
    offset_y = 300
    x = int(start_x + ((module % 3) * offset_x))
    y = int(start_y + ((module // 3) * offset_y))
    win_util.click(x, y)
    sleep(1)

def deselect_module(module):
    SW, SH = win_util.get_screen_size()
    start_x = SW * 0.35
    start_y = SH * 0.35
    offset_x = 300
    offset_y = 300
    win_util.click(300, 300, btn="right")
    sleep(1)

def screenshot_module():
    SW, SH = win_util.get_screen_size()
    x = int(SW * 0.43)
    y = int(SH*0.36)
    return screenshot(x, y, 300, 300), x, y

def release_mouse_at(digit, duration, x, y):
    time_started, minutes, seconds = duration
    while True:
        remaining = get_time_remaining(time_started, minutes, seconds)
        sec_str = str(remaining % 60)
        if len(sec_str) == 1:
            sec_str = "0" + sec_str
        digits = (remaining // 60, int(sec_str[0]), int(sec_str[1]))
        if digit in digits:
            win_util.mouse_up(x, y)
            break
        sleep(0.5)

def solve_wires(image, mod_pos, side_features):
    log("Solving Simple Wires...", config.LOG_DEBUG)
    mod_x, mod_y = mod_pos
    result, coords = wire_solver.solve(image, side_features)
    if result == -1:
        log(coords, config.LOG_WARNING)
        return
    log(f"Cut wire at {result}", config.LOG_DEBUG)
    wire_y, wire_x = coords[result]
    sleep(0.5)
    win_util.click(mod_x + wire_x, mod_y + wire_y)

def solve_button(image, mod_pos, side_features, character_model, duration):
    log("Solving Button...", config.LOG_DEBUG)
    mod_x, mod_y = mod_pos
    hold = button_solver.solve(image, side_features, character_model)
    log(f"Hold button: {hold}", config.LOG_DEBUG)
    button_x, button_y = mod_x + 125, mod_y + 175
    if not hold:
        win_util.click(button_x, button_y)
        sleep(1)
    else:
        win_util.mouse_move(button_x, button_y)
        win_util.mouse_down(button_x, button_y)
        sleep(0.9) # 48 frames until strip lights up.
        SC, _, _ = screenshot_module()
        image = convert_to_cv2(SC)
        pixel = (184, 255)
        release_time = button_solver.get_release_time(image, pixel)
        log(f"Release button at {release_time}", config.LOG_DEBUG)
        release_mouse_at(release_time, duration, button_x, button_y)

def solve_simon(image, mod_pos, side_features):
    log("Solving Simon Says...", config.LOG_DEBUG)
    mod_x, mod_y = mod_pos
    num = 1
    while not simon_solver.is_solved(image):
        btn_coords = simon_solver.solve(image, screenshot_module, side_features, num)
        for coords in btn_coords:
            button_y, button_x = coords
            win_util.click(mod_x + button_x, mod_y + button_y)
            sleep(0.5)
        sleep(1)
        num += 1
        SC, _, _ = screenshot_module()
        image = convert_to_cv2(SC)

def solve_wire_sequence(image, mod_pos):
    log("Solving Wire Sequence...", config.LOG_DEBUG)
    mod_x, mod_y = mod_pos
    button_x, button_y = 128 + mod_x, 248 + mod_y
    color_hist = [0, 0, 0]
    for _ in range(4):
        wires_to_cut, color_hist, coords = wire_seq_solver.solve(image, color_hist)
        for i, cut in enumerate(wires_to_cut):
            if cut:
                y, x = coords[i]
                win_util.click(mod_x + x, mod_y + y)
                sleep(0.5)
        win_util.click(button_x, button_y)
        sleep(2)
        image = convert_to_cv2(screenshot_module()[0])

def solve_complicated_wires(image, mod_pos, side_features):
    log("Solving Complicated Wires...", config.LOG_DEBUG)
    mod_x, mod_y = mod_pos
    wires_to_cut, coords = compl_wires_solver.solve(image, side_features)
    for i, cut in enumerate(wires_to_cut):
        if cut:
            y, x = coords[i]
            win_util.click(mod_x + x, mod_y + y)
            sleep(0.5)

def solve_morse(image, mod_pos):
    log("Solving Morse Code...", config.LOG_DEBUG)
    mod_x, mod_y = mod_pos
    presses, frequency = morse_solver.solve(image, screenshot_module)
    log(f"Morse frequency: {frequency}.", config.LOG_DEBUG)
    button_x, button_y = mod_x + 154, mod_y + 236
    inc_btn_x, inc_btn_y = mod_x + 240, mod_y + 170
    for _ in range(presses):
        win_util.click(inc_btn_x, inc_btn_y)
        sleep(0.3)
    win_util.click(button_x, button_y)

def solve_symbols(image, mod_pos, symbol_model):
    log("Solving Symbols...", config.LOG_DEBUG)
    mod_x, mod_y = mod_pos
    coords = symbols_solver.solve(image, symbol_model)
    if coords is None:
        log("WARNING: Could not solve symbols.", config.LOG_WARNING)
        return
    for y, x in coords:
        win_util.click(mod_x + x, mod_y + y)
        sleep(0.5)

def solve_maze(image, mod_pos):
    log("Solving Maze...", config.LOG_DEBUG)
    mod_x, mod_y = mod_pos
    up_x, up_y = (mod_x + 143, mod_y + 36)
    down_x, down_y = (mod_x + 143, mod_y + 263)
    left_x, left_y = (mod_x + 27, mod_y + 144)
    right_x, right_y = (mod_x + 253, mod_y + 144)
    N = maze_solver.DIRECTIONS.North
    S = maze_solver.DIRECTIONS.South
    E = maze_solver.DIRECTIONS.East
    W = maze_solver.DIRECTIONS.West
    path = maze_solver.solve(image)
    for direction in path:
        if direction == N:
            win_util.click(up_x, up_y)
        elif direction == S:
            win_util.click(down_x, down_y)
        elif direction == W:
            win_util.click(left_x, left_y)
        elif direction == E:
            win_util.click(right_x, right_y)
        sleep(0.5)

def solve_password(image, char_model, mod_pos):
    mod_x, mod_y = mod_pos
    submit_x, submit_y = mod_x + 154, mod_y + 254
    # Use lambda function to translate 'image-local' clicks
    # from the password solver into 'screen-local' coordinates.
    click_func = lambda x, y: win_util.click(mod_x + x, mod_y + y)
    success = password_solver.solve(image, char_model, screenshot_module, click_func)
    if success:
        win_util.click(submit_x, submit_y)
    else:
        log(f"WARNING: Could not solve 'Password'.", config.LOG_WARNING)

def solve_memory(image, char_model, mod_pos):
    mod_x, mod_y = mod_pos
    history = []
    for i in range(5):
        if i > 0:
            sleep(3.5)
        coords, label, position = memory_solver.solve(image, char_model, history)
        history.append((label, position))
        y, x = coords
        win_util.click(x + mod_x, y + mod_y)
        image = convert_to_cv2(screenshot_module()[0])

def solve_whos_on_first(image, char_model, mod_pos):
    mod_x, mod_y = mod_pos
    coords = whos_first_solver.solve(image, char_model)
    if coords is None:
        log(f"WARNING: Could not solve 'Who's On First?'.", config.LOG_WARNING)

def solve_modules(modules, side_features, character_model, symbol_model, duration):
    dont_solve = [9, 10, 11, 12, 13, 14, 17, 18, 19]
    for module, label in enumerate(modules[:12]):
        mod_index = module if module < 6 else module - 6
        if label > 8:
            LIGHT_MONITOR.wait_for_light() # If the room is dark, wait for light.
            select_module(mod_index)
            SC, x, y = screenshot_module()
            mod_pos = (x, y)
            cv2_img = convert_to_cv2(SC)
            if label == 9 and label not in dont_solve: # Wires.
                solve_wires(cv2_img, mod_pos, side_features)
            elif label == 10 and label not in dont_solve: # Button.
                solve_button(cv2_img, mod_pos, side_features, character_model, duration)
            elif label == 11 and label not in dont_solve: # Symbols.
                solve_symbols(cv2_img, mod_pos, symbol_model)
            elif label == 12 and label not in dont_solve: # Simon Says.
                solve_simon(cv2_img, mod_pos, side_features)
            elif label == 13 and label not in dont_solve: # Wire Sequence.
                solve_wire_sequence(cv2_img, mod_pos)
            elif label == 14 and label not in dont_solve: # Complicated Wires.
                solve_complicated_wires(cv2_img, mod_pos, side_features)
            elif label == 15 and label not in dont_solve: # Memory Game.
                solve_memory(cv2_img, character_model, mod_pos)
            elif label == 17 and label not in dont_solve: # Maze.
                solve_maze(cv2_img, mod_pos)
            elif label == 18 and label not in dont_solve: # Password.
                solve_password(cv2_img, character_model, mod_pos)
            elif label == 19 and label not in dont_solve: # Morse.
                solve_morse(cv2_img, mod_pos)
            sleep(0.5)
            deselect_module(mod_index)
        if module == 5: # We have gone through 6 modules, flip the bomb over and proceeed.
            SW, SH = win_util.get_screen_size()
            flip_bomb(SW, SH)
            sleep(0.75)
            win_util.mouse_up(SW // 2, SH // 2, btn="right")
            sleep(0.5)

if __name__ == "__main__":
    config.MAX_GPU_FRACTION = 0.2 # Limit Neural Network classifier GPU usage.
    log("Loading classifier model...")
    # Load model for classifying modules.
    MODEL = module_classifier.load_from_file("../resources/trained_models/module_model")

    # Load model for classifying letters (serial number, indicators, etc.).
    CHAR_MODEL = character_classifier.load_from_file("../resources/trained_models/character_model")

    # Load model for classifying symbols (used only in the symbol module).
    SYMBOL_MODEL = symbol_classifier.load_from_file("../resources/trained_models/symbol_model")

    log("Waiting for level selection...")
    log("Press S when a level has been selected.")
    sleep_until_start() # Wait for level selection.

    MINUTES = 8
    SECONDS = 0

    if "skip" not in argv:
        # Extract bomb duration from description of bomb in main menu.
        MINUTES, SECONDS = get_bomb_duration(CHAR_MODEL)
        log(f"Bomb duration: {MINUTES} minute(s) & {SECONDS} seconds.")

        start_level()

        log("Waiting for level to start...")
        await_level_start() # Wait for level to load and bomb timer to start.

    TIME_STARTED = time() # Time started is used for solving the button module.

    log("Inspecting bomb...")

    IMAGES = inspect_bomb() # Capture images of all sides of the bomb.
    SIDE_PARTITIONS = partition_sides(IMAGES) # Split images into modules/side of bomb.
    # Identify features from the side of the bomb (indicators, batteries, serial number, etc.).
    PREDICTIONS = identify_side_features(SIDE_PARTITIONS, MODEL)

    # Extract aforementioned features (read serial number, count num. of batteries, etc.).
    SIDE_FEATURES = extract_side_features(SIDE_PARTITIONS[1:], PREDICTIONS[12:], CHAR_MODEL)

    log(f"Side features: {SIDE_FEATURES}", verbose=config.LOG_DEBUG)
    log(f"Modules: {[module_classifier.LABELS[x] for x in PREDICTIONS[:12]]}", config.LOG_DEBUG)

    LIGHT_MONITOR = LightMonitor() # Monitor whether the light in the room has turned off.

    # Solve all modules. Back of the bomb first, then from the top, left to right.
    solve_modules(PREDICTIONS[:12], SIDE_FEATURES, CHAR_MODEL,
                  SYMBOL_MODEL, (TIME_STARTED, MINUTES, SECONDS))

    LIGHT_MONITOR.shut_down()
