from enum import Enum
import numpy as np
import cv2
import features.util as features_util
import config

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
    radius = 5
    Color = Enum("Colors", {"Blue":0, "White":1, "Red":2, "Both":3})
    colors = config.WIRE_COLOR_RANGE[2:]
    rgb = features_util.split_channels(img)
    color_threshold = 5
    for i, (y, x) in enumerate(coords):
        valid_colors = [0] * len(colors)
        for k, (lo, hi) in enumerate(colors):
            for m in range(y-radius, y+radius):
                for n in range(x-radius, x+radius):
                    if features_util.color_in_range((m, n), rgb, lo, hi):
                        if valid_colors[k] < color_threshold:
                            valid_colors[k] += 1
        if valid_colors[Color.Blue.value] == color_threshold:
            if valid_colors[Color.Red.value] == color_threshold:
                wires[i] = Color.Both.value # Both colors.
            else:
                wires[i] = Color.Blue.value
        elif valid_colors[Color.Red.value] == color_threshold:
            wires[i] = Color.Red.value
        elif valid_colors[Color.White.value] == color_threshold:
            wires[i] = Color.White.value
    return wires

def get_wire_label(has_star, is_lit, color):
    Color = Enum("Colors", {"Blue":0, "White":1, "Red":2, "Both":3})
    if color > Color.White.value:
        if color == Color.Both.value:
            if has_star:
                if not is_lit:
                    return "P"
            return "S"
        if has_star:
            if is_lit:
                return "B"
            return "C"
        return "S"
    elif color == Color.Blue.value:
        if has_star:
            if is_lit:
                return "P"
            return "D"
        if is_lit:
            return "P"
        return "S"
    elif has_star:
        if is_lit:
            return "B"
        return "C"
    elif is_lit:
        return "D"
    return "C"

def parse_label(label, features):
    if label == "C":
        return True
    if label == "S":
        return not features["last_serial_odd"]
    if label == "P":
        return features["parallel_port"]
    if label == "B":
        return features["batteries"] >= 2
    return False

def solve(img, features):
    wire_coords = [
        (140, 49), (140, 74), (140, 126),
        (140, 168), (140, 190), (140, 226)
    ]
    stars = get_stars(img)
    lights = get_lights(features_util.split_channels(img))
    wires = get_wire_colors(img, wire_coords)
    wires_to_cut = []
    for (star, light, wire) in zip(stars, lights, wires):
        if wire == -1:
            wires_to_cut.append(False)
            continue
        solve_label = get_wire_label(star, light, wire)
        wires_to_cut.append(parse_label(solve_label, features))
    return wires_to_cut, wire_coords
