from time import sleep, time
from numpy import array
import cv2
import config
import features.util as feature_util
from debug import log, LOG_DEBUG

def is_solved(image):
    rgb = feature_util.split_channels(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    pixel = (18, 270)
    lit_low = (0, 200, 0)
    lit_high = (50, 255, 50)
    return feature_util.color_in_range(pixel, rgb, lit_low, lit_high)

def get_response_color(color, features):
    if features["contains_vowel"]:
        if color == 0: # Red.
            return 1 # Press blue.
        if color == 1: # Blue.
            return 0 # Press red.
        if color == 2: # Green.
            return 3 # Press yellow.
        if color == 3: # Yellow.
            return 2 # Press green.
    else:
        if color == 0: # Red.
            return 1 # Press blue.
        if color == 1: # Blue.
            return 3 # Press yellow.
        if color == 2: # Green.
            return 2 # Press green.
        if color == 3: # Yellow.
            return 0 # Press red.
    return -1

def get_next_color(sc_func, ranges, features, curr_match):
    coords = [(140, 95), (74, 155), (204, 156), (140, 216)]
    colors = ["Red", "Blue", "Green", "Yellow"]
    button_coords = []
    pause_between_blinks = 0.35
    colors_matched = 0
    timestamp = 0
    while True:
        sc, _, _ = sc_func()
        rgb = feature_util.split_channels(cv2.cvtColor(array(sc), cv2.COLOR_RGB2BGR))
        for i, (low, high) in enumerate(ranges):
            coord = coords[i]
            if feature_util.color_in_range(coord, rgb, low, high) and time() - timestamp > pause_between_blinks:
                colors_matched += 1
                press_color = get_response_color(i, features)
                button_coords.append(coords[press_color])
                timestamp = time()
                if colors_matched == curr_match:
                    log(f"Color: {colors[i]}. Press: {colors[press_color]}", LOG_DEBUG, "Simon Says")
                    return button_coords
        sleep(0.1) # Lamps are lit for 0.25 seconds.

def solve(screenshot_func, features, color_num=1):
    ranges = config.SIMON_COLOR_RANGE
    coords = get_next_color(screenshot_func, ranges, features, color_num)
    return coords
