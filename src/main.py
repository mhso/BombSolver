from time import sleep, time
from sys import argv
from math import ceil
from numpy import array
import cv2
from debug import log
from model.grab_img import screenshot
import windows_util as win_util
from model import module_classifier, serial_classifier, classifier_util, dataset_util
import solvers
from features.serial_number import get_serial_number
from features.bomb_duration import get_bomb_duration
from features.indicator import get_indicator_features
import config

def sleep_until_start():
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

def start_level():
    SW, SH = win_util.get_screen_size()
    win_util.click(int(SW - SW/2.6), int(SH - SH/3.3))

def wait_for_light():
    sleep(15.3)

def inspect_side(mx, my, sx, sy, sw, sh):
    win_util.mouse_move(mx, my)
    sleep(0.5)
    SC = screenshot(sx, sy, sw, sh)
    sleep(0.2)
    return SC

def inspect_bomb():
    SW, SH = win_util.get_screen_size()
    mid_x = SW // 2
    mid_y = SH // 2
    win_util.click(mid_x, mid_y + (mid_y // 8))
    sleep(0.5)
    # Inspect front of bomb.
    front_img = screenshot(460, 220, 1000, 640)
    front_img.save("../front.png")
    sleep(0.2)
    # Rotate bomb.
    win_util.mouse_down(mid_x, mid_y, btn="right")
    sleep(0.2)
    # Inspect right side.
    right_img = inspect_side(SW - int(SW / 2.74), mid_y + int(mid_y / 8), 755, 60, 480, 900)
    right_img.save("../left.png")
    # Inspect left side.
    left_img = inspect_side(int(SW / 2.76), mid_y + int(mid_y / 8), 755, 60, 480, 900)
    left_img.save("../right.png")
    # Inspect top side.
    top_img = inspect_side(int(SW / 2.75), SH, 720, 0, 480, SH)
    top_img.save("../top.png")
    # Inspect bottom side.
    bottom_img = inspect_side(int(SW / 2.75), 0, 720, 0, 480, SH)
    bottom_img.save("../bot.png")
    # Inspect back of bomb.
    win_util.mouse_up(mid_x, mid_y, btn="right")
    sleep(0.5)
    win_util.click(SW - 100, 100, btn="right")
    sleep(0.5)
    win_util.click(mid_x, mid_y + (mid_y // 8))
    sleep(0.2)
    win_util.mouse_down(mid_x, mid_y, btn="right")
    sleep(0.5)
    back_img = inspect_side(SW - int(SW / 4.4), mid_y + (mid_y // 9), 460, 220, 1000, 640)
    back_img.save("../back.png")
    sleep(0.2)
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
    features = [0] * config.OUTPUT_DIM
    predictions = [0] * 32
    i = 0
    for side in sides:
        for img in side:
            padded = dataset_util.pad_image(array(img))
            reshaped = dataset_util.resize_img(padded, config.INPUT_DIM[1:])
            converted = cv2.cvtColor(reshaped, cv2.COLOR_RGB2BGR) / 255
            pred = module_classifier.predict(model, converted)
            predict_label = classifier_util.get_best_prediction(pred)[0]
            predictions[i] = predict_label
            features[predict_label] += 1
            i += 1
    return (features, predictions)

def print_features(features):
    for feature, amount in enumerate(features):
        print(f"{module_classifier.LABELS[feature]} - {amount}")

def get_time_remaining(time_started, minutes, seconds):
    return ceil((minutes * 60 + seconds) - (time() - time_started))

def serial_contains_vowel(serial_num):
    vowels = ["A", "E", "I", "U", "Y"]
    for c in serial_num:
        if c in vowels:
            return True
    return False

def extract_serial_number_features(serial_num):
    features = {}
    features["last_serial_odd"] = (int(serial_num[-1])) % 2 == 1
    features["contains_vowel"] = serial_contains_vowel(serial_num)
    return features

def extract_side_features(sides, labels, serial_model):
    index = 0
    features = {
        "indicators" : [],
        "parallel_port" : False,
        "batteries" : 0
    }
    for side in sides:
        for img in side:
            cv2_img = cv2.cvtColor(array(img), cv2.COLOR_RGB2BGR)
            if labels[index] == 1:
                features["batteries"] += 1
            elif labels[index] == 2:
                features["batteries"] += 2
            elif labels[index] == 3: # Serial number.
                serial_num = get_serial_number(cv2_img, serial_model)
                if serial_num is None:
                    log(f"Serial number could not be determined.")
                    index += 1
                    continue
                log(f"Serial number: {serial_num}", verbosity_level=1)
                features["serial_number"] = serial_num
                serial_features = extract_serial_number_features(serial_num)
                log(f"Serial number features: {serial_features}", verbosity_level=1)
                features.update(serial_features)
            elif labels[index] == 5: # Parallel port.
                features["parallel_port"] = True
            elif labels[index] == 6: # Indicator of some kind.
                lit, text = get_indicator_features(cv2_img, serial_model)
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
    sleep(1.5)

def deselect_module(module):
    SW, SH = win_util.get_screen_size()
    start_x = SW * 0.35
    start_y = SH * 0.35
    offset_x = 300
    offset_y = 300
    x = int(start_x + ((module % 3) * offset_x))
    y = int(start_y + ((module // 3) * offset_y))
    win_util.click(300, 300, btn="right")
    sleep(1)

def screenshot_module():
    SW, SH = win_util.get_screen_size()
    x = int(SW * 0.43)
    y = int(SH*0.36)
    return screenshot(x, y, 300, 300), x, y

def solve_modules(modules, solver_funcs, side_features):
    for module, label in enumerate(modules[:6]):
        if label > 8:
            select_module(module)
            SC, mod_x, mod_y = screenshot_module()
            SC = array(SC)
        if label == 9 and False:
            result, coords = solver_funcs[label-8].solve(SC, side_features)
            if result == -1:
                log(coords)
                continue
            log(f"Cut wire at {result}")
            wire_y, wire_x = coords[result]
            sleep(0.5)
            win_util.click(mod_x + wire_x, mod_y + wire_y)
            sleep(1)
            deselect_module(module)
        elif label == 10:
            hold = solver_funcs[label-8].solve(SC, side_features)
            log(f"Button, hold: {hold}")

if __name__ == "__main__":
    config.MAX_GPU_FRACTION = 0.2
    log("Loading classifier model...")
    MODEL = module_classifier.load_from_file("../resources/trained_models/module_model")

    SERIAL_MODEL = serial_classifier.load_from_file("../resources/trained_models/serial_model")

    log("Waiting for level selection...")
    log("Press S when a level has been selected.")
    sleep_until_start()

    MINUTES = 8
    SECONDS = 0

    if "skip" not in argv:
        MINUTES, SECONDS = get_bomb_duration(SERIAL_MODEL)
        log(f"Bomb duration: {MINUTES} minute(s) & {SECONDS} seconds.")

        start_level()

        log("Waiting for level to start...")
        wait_for_light()

    TIME_STARTED = time()

    log("Inspecting bomb...")
    IMAGES = inspect_bomb()
    SIDE_PARTITIONS = partition_sides(IMAGES)
    FEATURES, PREDICTIONS = identify_side_features(SIDE_PARTITIONS, MODEL)

    SOLVERS = [
        solvers.wire_solver, solvers.button_solver,
        solvers.symbols_solver, solvers.simon_solver,
        solvers.wire_seQ_solver, solvers.compl_wires_solver,
        solvers.memory_solver, solvers.whos_first_solver, solvers.maze_solver,
        solvers.password_solver, solvers.morse_solver
    ]

    SIDE_FEATURES = extract_side_features(SIDE_PARTITIONS[1:], PREDICTIONS[12:], SERIAL_MODEL)
    log(f"Side features: {SIDE_FEATURES}", verbosity_level=1)
    log(f"Modules: {[module_classifier.LABELS[x] for x in PREDICTIONS[:12]]}", verbosity_level=1)
    #solve_modules(PREDICTIONS[:12], SOLVERS, SIDE_FEATURES)
    """
    cv2.namedWindow("Predictions")

    label = 0
    for side in SIDE_PARTITIONS:
        for img in side:
            pred_label = PREDICTIONS[label]
            print(f"Predicted: {pred_label} ({config.LABELS[pred_label]})")
            img = cv2.cvtColor(array(img, dtype="uint8"), cv2.COLOR_RGB2BGR)
            cv2.imshow("Predictions", img)
            label += 1
            key = cv2.waitKey(0)
            if key == ord('q'):
                exit(0)

    print_features(FEATURES)
    """
