from enum import Enum
import numpy as np
import cv2
import features.util as features_util
import config
from debug import log, LOG_DEBUG

COLOR = Enum("Colors", {"Blue": 0, "White": 1, "Red": 2, "Both": 3})

def get_stars(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    coords = [
        (244, 51), (244, 88), (243, 123),
        (243, 165), (241, 205), (243, 240)
    ]
    radius = 8
    stars = [False] * 6
    for i, (y, x) in enumerate(coords):
        label = gray[y-radius:y+radius, x-radius:x+radius]
        if len(np.where(label < 70)[0]) > 50:
            stars[i] = True
    return stars

def get_lights(rgb):
    coords = (52, 80, 110, 142, 172, 200)
    y = 43
    lit_lo = (200, 200, 150)
    lit_hi = (255, 255, 220)
    lights = [False] * 6
    for i, x in enumerate(coords):
        pixel = (y, x)
        if features_util.color_in_range(pixel, rgb, lit_lo, lit_hi):
            lights[i] = True
    return lights

def get_wire_colors(img, coords):
    wires = [-1] * 6
    radius = 9
    colors = config.WIRE_COLOR_RANGE[2:]
    rgb = features_util.split_channels(img)
    color_threshold = 6
    for i, (y, x) in enumerate(coords):
        valid_colors = [0] * len(colors)
        for k, (lo, hi) in enumerate(colors):
            for m in range(y-radius, y+radius):
                for n in range(x-radius, x+radius):
                    if features_util.color_in_range((m, n), rgb, lo, hi):
                        if valid_colors[k] < color_threshold:
                            valid_colors[k] += 1
        if valid_colors[COLOR.Blue.value] == color_threshold:
            if valid_colors[COLOR.Red.value] == color_threshold:
                wires[i] = COLOR.Both.value # Both colors.
            else:
                wires[i] = COLOR.Blue.value
        elif valid_colors[COLOR.Red.value] == color_threshold:
            wires[i] = COLOR.Red.value
        elif valid_colors[COLOR.White.value] == color_threshold:
            wires[i] = COLOR.White.value
    return wires

def get_wire_label(has_star, is_lit, color):
    if color > COLOR.White.value: # Color is either Blue + Red or just Red.
        if color == COLOR.Both.value: # Wire is Blue and Red.
            if has_star:
                if not is_lit:
                    return "P"
            return "S"
        if has_star: # Wire is just Red.
            if is_lit:
                return "B"
            return "C"
        if is_lit:
            return "B"
        return "S"
    if color == COLOR.Blue.value: # Wire is just Blue.
        if has_star:
            if is_lit:
                return "P"
            return "D"
        if is_lit:
            return "P"
        return "S"
    if has_star:
        if is_lit:
            return "B"
        return "C"
    if is_lit:
        return "D"
    return "C"

def parse_label(label, features):
    if label == "C": # Cut always.
        return True
    if label == "S": # Cut if last digit of serial is odd.
        return not features["last_serial_odd"]
    if label == "P": # Cut if bomb has a parallel port.
        return features["parallel_port"]
    if label == "B": # Cut if bomb has 2 or more batteries.
        return features["batteries"] >= 2
    return False

def desc_wires(wires, stars, lights):
    descriptions = []
    colors = ["Blue", "White", "Red", "Both"]
    for wire, star, light in zip(wires, stars, lights):
        if wire == -1:
            descriptions.append("None")
        else:
            desc = colors[wire]
            if light:
                desc += " with LED "
            if star:
                if light:
                    desc += "& star"
                else:
                    desc += " with star"
            desc += "."
            descriptions.append(desc)
    return descriptions

def solve(img, features):
    wire_coords = [
        (140, 49), (140, 74), (140, 126),
        (140, 168), (140, 190), (140, 226)
    ]
    wires = get_wire_colors(img, wire_coords)
    stars = get_stars(img)
    lights = get_lights(features_util.split_channels(img))
    log(desc_wires(wires, stars, lights), LOG_DEBUG, "Complicated Wires")
    wires_to_cut = []
    for (star, light, wire) in zip(stars, lights, wires):
        if wire == -1:
            wires_to_cut.append(False)
            continue
        solve_label = get_wire_label(star, light, wire)
        wires_to_cut.append(parse_label(solve_label, features))
    log(f"Wires to cut: {wires_to_cut}", LOG_DEBUG, "Complicated Wires")
    return wires_to_cut, wire_coords
