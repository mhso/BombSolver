from time import sleep, time
from sys import argv
from math import floor
from numpy import array
#from view.overlay import initialize as overlay_init
from debug import log, handle_module_exception
import util.windows_util as win_util
import util.inspect_bomb as inspect_bomb
from model import (
    module_classifier, character_classifier, symbol_classifier,
    classifier_util, dataset_util
)
from model.grab_img import screenshot
from solvers import (
    wire_solver, button_solver, symbols_solver, simon_solver,
    wire_seq_solver, compl_wires_solver, memory_solver, whos_first_solver,
    maze_solver, password_solver, morse_solver, needy_vent_solver, needy_knob_solver
)
from features.serial_number import get_serial_number
from features.bomb_details import get_bomb_details
from features.util import convert_to_cv2
from features.indicator import get_indicator_features
from features.light_monitor import LightMonitor
import features.needy_util as needy_features
import config

LIGHT_MONITOR = None # Monitors (from a seperate thread) whether the light has turned off.
OVERLAY_CONN = None

def sleep_until_start():
    """
    Sleep until 's' has been pressed.
    """
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

def start_level():
    """
    Click the 'Start Level' button, after a level has been selected.
    """
    SW, SH = win_util.get_screen_size()
    win_util.click(int(SW - SW/2.6), int(SH - SH/3.3))

def await_level_start():
    """
    Sleep until the given level has started (when the light is turned on).
    """
    LIGHT_MONITOR.wait_for_light()

def identify_side_features(sides, model):
    flattened = []
    for side in sides:
        for img in side:
            converted = dataset_util.reshape(convert_to_cv2(img), config.MODULE_INPUT_DIM[1:])
            flattened.append(converted)
    preds = module_classifier.predict(model, array(flattened))
    predictions = classifier_util.get_best_prediction(preds)
    return predictions

def print_features(features):
    for feature, amount in enumerate(features):
        print(f"{module_classifier.LABELS[feature]} - {amount}")

def get_time_spent(time_started):
    return time() - time_started

def get_time_remaining(time_started, minutes, seconds):
    time_spent = get_time_spent(time_started)
    return floor((minutes * 60 + seconds) - (time_spent))

# /========================= BOMB FEATURES =========================\

def serial_contains_vowel(serial_num):
    vowels = ["A", "E", "I", "U", "Y"]
    for char in serial_num:
        if char in vowels:
            return True
    return False

def extract_serial_number_features(serial_num):
    """
    Get relevanmt features about the serial number.
    This includes wether the last digit is odd and whether it contains a vowel.
    """
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
            mod_name = module_classifier.LABELS[labels[index]]
            try:
                if labels[index] == 1: # Single battery (large or small).
                    features["batteries"] += 1
                elif labels[index] == 2: # Double batteries.
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
            except KeyboardInterrupt:
                handle_module_exception(mod_name, cv2_img)
                raise KeyboardInterrupt
            except Exception:
                handle_module_exception(mod_name, cv2_img)
            index += 1
    return features

# /================= MODULE SELECTION / SCREENSHOTTING =================\

def get_module_coords(module_index):
    """
    Get screen coordinates of a module based on module index.
    """
    SW, SH = win_util.get_screen_size()
    start_x = SW * 0.35
    start_y = SH * 0.35
    offset_x = 300
    offset_y = 300
    x = int(start_x + ((module_index % 3) * offset_x))
    y = int(start_y + ((module_index // 3) * offset_y))
    return x, y

def select_module(module_index):
    x, y = get_module_coords(module_index)
    win_util.click(x, y)
    sleep(1)

def deselect_module():
    x = 300
    y = 300
    win_util.click(x, y, btn="right")
    sleep(0.5)

def screenshot_module():
    SW, SH = win_util.get_screen_size()
    x = int(SW * 0.43)
    y = int(SH*0.36)
    return screenshot(x, y, 300, 300), x, y

# /========================= MODULE SOLVING =========================\

def release_mouse_at(digit, duration, x, y):
    time_started, mins, secs = duration
    while True:
        remaining = get_time_remaining(time_started, mins, secs)
        sec_str = str(remaining % 60)
        if len(sec_str) == 1:
            sec_str = "0" + sec_str
        digits = (remaining // 60, int(sec_str[0]), int(sec_str[1]))
        if digit in digits:
            win_util.mouse_up(x, y)
            break
        sleep(0.5)

def solve_wires(image, mod_pos, side_features):
    mod_x, mod_y = mod_pos
    result, coords = wire_solver.solve(image, side_features)
    log(f"Cut wire at {result}", config.LOG_DEBUG)
    wire_y, wire_x = coords[result]
    win_util.click(mod_x + wire_x, mod_y + wire_y)

def solve_button(image, mod_pos, side_features, character_model, duration):
    mod_x, mod_y = mod_pos
    hold = button_solver.solve(image, side_features, character_model)
    button_x, button_y = mod_x + 125, mod_y + 175
    if not hold:
        log(f"Tapping button.", config.LOG_DEBUG, "Button")
        win_util.click(button_x, button_y)
        sleep(0.5)
    else:
        log(f"Holding button...", config.LOG_DEBUG, "Button")
        win_util.mouse_move(button_x, button_y)
        win_util.mouse_down(button_x, button_y)
        sleep(0.9) # 48 frames until strip lights up.
        SC, _, _ = screenshot_module()
        image = convert_to_cv2(SC)
        pixel = (184, 255)
        release_time = button_solver.get_release_time(image, pixel)
        log(f"Release button at {release_time}", config.LOG_DEBUG, "Button")
        release_mouse_at(release_time, duration, button_x, button_y)

def solve_simon(image, mod_pos, side_features):
    mod_x, mod_y = mod_pos
    num = 1
    while not simon_solver.is_solved(image):
        btn_coords = simon_solver.solve(screenshot_module, side_features, num)
        for coords in btn_coords:
            button_y, button_x = coords
            win_util.click(mod_x + button_x, mod_y + button_y)
            sleep(0.5)
        num += 1
        sleep(0.5)
        SC, _, _ = screenshot_module()
        image = convert_to_cv2(SC)

def solve_wire_sequence(image, mod_pos):
    mod_x, mod_y = mod_pos
    button_x, button_y = 128 + mod_x, 248 + mod_y
    color_hist = [0, 0, 0]
    for i in range(4):
        wires_to_cut, color_hist, coords = wire_seq_solver.solve(image, color_hist)
        for j, cut in enumerate(wires_to_cut):
            if cut:
                y, x = coords[j]
                win_util.click(mod_x + x, mod_y + y)
                sleep(0.5)
        win_util.click(button_x, button_y)
        if i < 3:
            sleep(1.8)
        image = convert_to_cv2(screenshot_module()[0])

def solve_complicated_wires(image, mod_pos, side_features):
    mod_x, mod_y = mod_pos
    wires_to_cut, coords = compl_wires_solver.solve(image, side_features)
    for i, cut in enumerate(wires_to_cut):
        if cut:
            y, x = coords[i]
            win_util.click(mod_x + x, mod_y + y)
            sleep(0.3)

def solve_morse(image, mod_pos):
    mod_x, mod_y = mod_pos
    presses, frequency = morse_solver.solve(image, screenshot_module)
    log(f"Morse frequency: {frequency}.", config.LOG_DEBUG, "Morse")
    button_x, button_y = mod_x + 154, mod_y + 236
    inc_btn_x, inc_btn_y = mod_x + 240, mod_y + 170
    for _ in range(presses):
        win_util.click(inc_btn_x, inc_btn_y)
        sleep(0.3)
    win_util.click(button_x, button_y)

def solve_symbols(image, mod_pos, symbol_model):
    mod_x, mod_y = mod_pos
    coords = symbols_solver.solve(image, symbol_model)
    if coords is None:
        log("WARNING: Could not solve symbols.", config.LOG_WARNING)
        return
    for y, x in coords:
        win_util.click(mod_x + x, mod_y + y)
        sleep(0.3)

def solve_maze(image, mod_pos):
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
        sleep(0.3)

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
        coords, label, position = memory_solver.solve(image, char_model, history)
        history.append((label, position))
        y, x = coords
        win_util.click(x + mod_x, y + mod_y)
        if i < 4:
            sleep(3.5)
        new_sc = screenshot_module()[0]
        image = convert_to_cv2(new_sc)

def solve_whos_on_first(image, char_model, mod_pos):
    mod_x, mod_y = mod_pos
    for i in range(3):
        coords = whos_first_solver.solve(image, char_model)
        y, x = coords
        win_util.click(x + mod_x, y + mod_y)
        if i < 2:
            sleep(3.5)
        sc = screenshot_module()[0]
        image = convert_to_cv2(sc)

# /========================= NEEDY MODULES =========================\

def solve_needy_vent(image, mod_pos):
    if not needy_features.is_active(image):
        log("Needy Vent is not active.", config.LOG_DEBUG, "Needy Vent")
        return
    mod_x, mod_y = mod_pos
    button_y, button_x = needy_vent_solver.solve(image)
    win_util.click(button_x + mod_x, button_y + mod_y)

def solve_needy_discharge(image, mod_pos, time_started):
    if not needy_features.is_active(image):
        log("Needy Discharge is not active.", config.LOG_DEBUG, "Needy Discharge")
        return
    mod_x, mod_y = mod_pos
    time_spent = get_time_spent(time_started)
    x_top, y_top = mod_x + 230, mod_y + 92

    win_util.mouse_move(x_top, y_top)
    win_util.mouse_down(x_top, y_top)
    sleep_time = 1 + (time_spent / 5)
    sleep(sleep_time)
    win_util.mouse_up(x_top, y_top)

def solve_needy_knob(image, mod_pos):
    mod_x, mod_y = mod_pos
    dial_x, dial_y = mod_x + 150, mod_y + 161
    num_turns = needy_knob_solver.solve(image)
    for _ in range(num_turns):
        win_util.click(dial_x, dial_y)
        sleep(0.3)

def needy_modules_critical(needy_modules, time_started, mod_duration):
    """
    Simplified function for figuring out whether we should solve
    needy modules, or if we can wait a bit. This method is not
    particularly accurate, but plays it safe, so we don't blow up.
    """
    if needy_modules == 0:
        return False
    time_spent = get_time_spent(time_started) + mod_duration
    needy_duration = 40 # Duration before a needy module explodes.
    time_to_solve = 4 # Approx. time required to solve a needy module.
    threshold = needy_modules * time_to_solve
    timeleft = needy_duration - time_spent
    flavor_str = f"in: {(timeleft - threshold):.1f}s" if timeleft >= threshold else "now!"
    log(f"Need to solve needy modules {flavor_str}", config.LOG_DEBUG)
    return timeleft < threshold

def solve_needy_modules(modules, needy_indices, curr_module, duration):
    SW, SH = win_util.get_screen_size()
    prev_index = curr_module
    timestamp = None
    for index in needy_indices:
        if (index > 5) ^ (prev_index > 5): # Flip the bomb, if needed.
            inspect_bomb.flip_bomb(SW, SH)
            sleep(0.75)
            win_util.mouse_up(SW // 2, SH // 2, btn="right")
            sleep(0.5)
        mod_index = index if index < 6 else index - 6
        label = modules[index]
        select_module(mod_index)
        add_overlay_properties("module_info", (label))
        SC, x, y = screenshot_module()
        mod_pos = (x, y)
        cv2_img = convert_to_cv2(SC)
        mod_name = module_classifier.LABELS[label]
        log(f"Solving {mod_name}...")
        try:
            if label == 20: # Needy Vent Gas.
                solve_needy_vent(cv2_img, mod_pos)
            elif label == 21: # Needy Discharge Capacitor.
                solve_needy_discharge(cv2_img, mod_pos, duration)
            elif label == 22: # Solve Knob.
                solve_needy_knob(cv2_img, mod_pos)
        except KeyboardInterrupt:
            handle_module_exception(mod_name, cv2_img)
            raise KeyboardInterrupt
        except Exception:
            handle_module_exception(mod_name, cv2_img)
        if timestamp is None:
            cooldown_time = 5
            timestamp = time() + cooldown_time
        sleep(0.5)
        deselect_module()
        prev_index = index
    # Flip the bomb back to it's original state, if needed.
    if (curr_module > 5) ^ (prev_index > 5):
        inspect_bomb.flip_bomb(SW, SH)
        sleep(0.75)
        win_util.mouse_up(SW // 2, SH // 2, btn="right")
        sleep(0.5)
    return timestamp

# /======================= SOLVE ALL MODULES =======================\

def solve_modules(modules, side_features, character_model, symbol_model, duration):
    # Get list of indexes of needy modules (all modules an index over 19).
    needy_indices = list(filter(lambda i: modules[i] > 19, [x for x in range(len(modules))]))
    needy_timestamp = duration[0]
    module_durations = [2, 5, 2, 12, 10, 2, 14, 8, 8, 8, 20]
    log(f"Needy modules: {len(needy_indices)}", config.LOG_DEBUG)

    solved_modules = 0
    num_modules = len(list(filter(lambda x: 8 < x < 20, modules)))
    module = 0
    while module < len(modules):
        label = modules[module]
        LIGHT_MONITOR.wait_for_light() # If the room is dark, wait for light.
        mod_index = module if module < 6 else module - 6
        bomb_solved = solved_modules == num_modules
        mod_duration = 2 if label > 19 else module_durations[label-9]
        critical = needy_modules_critical(len(needy_indices), needy_timestamp, mod_duration)
        if not bomb_solved and critical:
            # Needy modules need attention! Solve them, and continue where we left off.
            needy_timestamp = solve_needy_modules(modules, needy_indices, module, needy_timestamp)

        if 8 < label < 20:
            select_module(mod_index)
            SC, x, y = screenshot_module()
            #add_overlay_properties("module_selected", (x, y, mod_index))
            mod_pos = (x, y)
            cv2_img = convert_to_cv2(SC)
            mod_name = module_classifier.LABELS[label]
            log(f"Solving {mod_name}...")
            try:
                if label == 9: # Wires.
                    solve_wires(cv2_img, mod_pos, side_features)
                elif label == 10: # Button.
                    solve_button(cv2_img, mod_pos, side_features, character_model, duration)
                elif label == 11: # Symbols.
                    solve_symbols(cv2_img, mod_pos, symbol_model)
                elif label == 12: # Simon Says.
                    solve_simon(cv2_img, mod_pos, side_features)
                elif label == 13: # Wire Sequence.
                    solve_wire_sequence(cv2_img, mod_pos)
                elif label == 14: # Complicated Wires.
                    solve_complicated_wires(cv2_img, mod_pos, side_features)
                elif label == 15: # Memory Game.
                    solve_memory(cv2_img, character_model, mod_pos)
                elif label == 16: # Who's on First?
                    solve_whos_on_first(cv2_img, character_model, mod_pos)
                elif label == 17: # Maze.
                    solve_maze(cv2_img, mod_pos)
                elif label == 18: # Password.
                    solve_password(cv2_img, character_model, mod_pos)
                elif label == 19: # Morse.
                    solve_morse(cv2_img, mod_pos)
                solved_modules += 1
            except KeyboardInterrupt: # Bomb 'sploded.
                handle_module_exception(mod_name, cv2_img)
                raise KeyboardInterrupt
            except Exception:
                # If an exception happened while lights were off, we try again.
                if not LIGHT_MONITOR.lights_on:
                    log("Exception while light was off. We try again in a bit!")
                    deselect_module()
                    continue
                handle_module_exception(mod_name, cv2_img)

            sleep(0.1)
            deselect_module()

        if module == 5 and solved_modules != num_modules:
            # We have gone through all modules on one side of the bomb, flip it over and continue.
            SW, SH = win_util.get_screen_size()
            inspect_bomb.flip_bomb(SW, SH)
            sleep(0.75)
            win_util.mouse_up(SW // 2, SH // 2, btn="right")
            sleep(0.5)

        module += 1
    if solved_modules == num_modules:
        log("We did it! We live to defuse another bomb!")
    else:
        log("Some modules could not be disarmed, it seems we are doomed...")
        raise KeyboardInterrupt # We failed.

def add_overlay_properties(key, value):
    if "record" in argv:
        OVERLAY_CONN.send((key, value))

def run_level(module_model, char_model, symbol_model, minutes, seconds, num_modules):
    time_started = time() + 2 # Time started is used for solving the button module.

    log("Inspecting bomb...")

    inspect_both_sides = True#num_modules > 5 or num_modules == 3

    images = inspect_bomb.inspect_bomb(inspect_both_sides) # Capture images of all sides of the bomb.
    side_partitions = inspect_bomb.partition_sides(images) # Split images into modules/side of bomb.

    # Identify features from the side of the bomb (indicators, batteries, serial number, etc.).
    predictions = identify_side_features(side_partitions, module_model)

    modules = 12 if inspect_both_sides else 6

    #add_overlay_properties("module_positions", [get_module_coords(x) for x in range(6)])
    add_overlay_properties(
        "module_names", [module_classifier.LABELS[x] for x in predictions[:modules]]
    )

    # Extract aforementioned features (read serial number, count num. of batteries, etc.).
    side_features = extract_side_features(side_partitions[1:], predictions[modules:], char_model)

    log(f"Side features: {side_features}", verbose=config.LOG_DEBUG)
    log(f"Modules: {[module_classifier.LABELS[x] for x in predictions[:modules]]}", config.LOG_DEBUG)

    try:
        # Solve all modules. Back of the bomb first, from left to right, top to bottom.
        solve_modules(
            predictions[:modules], side_features, char_model,
            symbol_model, (time_started, minutes, seconds)
        )
    except KeyboardInterrupt: # Catch SIGINT from LightMonitor (meaning the bomb exploded).
        log("Exiting...")
    finally:
        LIGHT_MONITOR.shut_down()

if __name__ == "__main__":
    config.MAX_GPU_FRACTION = 0.2 # Limit Neural Network classifier GPU usage.

    #if "record" in argv: # Create GUI overlay.
    #    OVERLAY_CONN = overlay_init()

    log("Loading classifier models...")
    # Load model for classifying modules.
    MODEL = module_classifier.load_from_file("../resources/trained_models/module_model")

    # Load model for classifying letters (serial number, indicators, etc.).
    CHAR_MODEL = character_classifier.load_from_file("../resources/trained_models/character_model")

    # Load model for classifying symbols (used only in the symbol module).
    SYMBOL_MODEL = symbol_classifier.load_from_file("../resources/trained_models/symbol_model")

    log("Waiting for level selection...")
    log("Press S when a level has been selected.")
    sleep_until_start() # Wait for level selection.

    LIGHT_MONITOR = LightMonitor() # Track when the light in the room turns off.

    LEVELS = [None]
    SPLITS = []
    if "speedrun" in argv:
        log("Running in 'speedrun' mode, TAS engaged!")
        LEVELS_PER_PAGE = [5, 13, 20, 26, 32]
        LEVELS = inspect_bomb.LEVEL_COORDS

    if "record" in argv:
        config.VERBOSITY = config.LOG_OVERLAY

    for i, level in enumerate(LEVELS):
        speedrunning = level is not None
        if speedrunning:
            if i in LEVELS_PER_PAGE:
                inspect_bomb.next_level_page()
            log(f"Starting level '{level}'.")
            inspect_bomb.select_level(level)
            sleep(0.5)

        SECONDS = 0
        MINUTES = 5

        LIGHT_MONITOR.start()

        if "skip" not in argv:
            # Extract bomb duration from description of bomb in main menu.
            holder = []
            get_bomb_details(CHAR_MODEL, holder) # This method is run in parallel.

            start_level()
            if "speedrun" in argv and i == 0:
                SPEEDRUN_TIMESTAMP = time()
                add_overlay_properties("speedrun_time", SPEEDRUN_TIMESTAMP)

            log("Waiting for level to start...")
            await_level_start() # Wait for level to load and bomb timer to start.
            MINUTES, SECONDS = holder[0]
            NUM_MODULES = holder[1]
            log(f"Bomb timer: _:{SECONDS}.")
            log(f"Number of modules: {NUM_MODULES}.")

        run_level(MODEL, CHAR_MODEL, SYMBOL_MODEL, MINUTES, SECONDS, NUM_MODULES)

        if speedrunning: # Select next level.
            SPLITS.append((level, time() - SPEEDRUN_TIMESTAMP))
            add_overlay_properties("speedrun_splits", SPLITS)
            log(f"Split: {SPLITS[-1][1]:.3f} seconds.", module="Speedrun")
            log(f"Completed: {i+1}/{len(LEVELS)} levels.", module="Speedrun")
            sleep(11)
            inspect_bomb.continue_button()
            sleep(1.75)
            inspect_bomb.select_bombs_menu()
            sleep(1)

    if "record" in argv:
        OVERLAY_CONN.send(("active", False))
