from glob import glob
from sys import argv
from time import time
from threading import Thread, Lock
from mss import mss
from PIL import Image
from solvers.maze_solver import MAZES, DIRECTIONS
import numpy as np
import cv2
import util.windows_util as win_util

def format_time(s_time, sig_digs=1):
    mins = int(s_time // 60)
    secs = s_time % 60
    secs_str = f"{secs:0.{sig_digs}f}"
    if secs < 10:
        secs_str = "0" + secs_str
    return f"{mins:02d}:{secs_str}"

def format_level(level):
    upper_y = 15
    mid_y = 25
    lower_y = 30
    if len(level) > 9:
        split = level.split("_")
        if len(split) == 1:
            return [(level[:10], upper_y), (level[10:], lower_y)]
        return [("_".join(split[:-1]), upper_y), (split[-1], lower_y)]
    return [(level, mid_y)]

def draw_text(img, text, pt_1, scale, color, thickness=2, font=cv2.FONT_HERSHEY_PLAIN):
    pt_1 = pt_1[0] - GUIOverlay.padding_x, pt_1[1] + GUIOverlay.padding_y
    cv2.putText(img, text, pt_1, font, scale, color, thickness)

def draw_rect(img, pt_1, pt_2, color, thickness):
    pt_1 = pt_1[0] - GUIOverlay.padding_x, pt_1[1] + GUIOverlay.padding_y
    pt_2 = pt_2[0] - GUIOverlay.padding_x, pt_2[1] + GUIOverlay.padding_y
    cv2.rectangle(img, pt_1, pt_2, color, thickness)

def draw_line(img, pt_1, pt_2, color, thickness):
    pt_1 = pt_1[0] - GUIOverlay.padding_x, pt_1[1] + GUIOverlay.padding_y
    pt_2 = pt_2[0] - GUIOverlay.padding_x, pt_2[1] + GUIOverlay.padding_y
    cv2.line(img, pt_1, pt_2, color, thickness)

class GUIOverlay:
    record = False
    bg_img = None
    properties = {}
    drawing_order = []
    lock = Lock()
    is_active = True
    selected_module = (0, 0)
    padding_x = 300
    padding_y = 100
    window_name = "BombSolver"

    @staticmethod
    def start():
        Thread(target=GUIOverlay.create_window).start()

    @staticmethod
    def draw_speedrun_splits(splits):
        sw, _ = win_util.get_screen_size()
        bar_height = 100
        cv2.rectangle(GUIOverlay.bg_img, (0, 0), (sw, bar_height), (0, 0, 0), -1)
        start_x = 5
        step_x = 125
        for i, (level, split) in enumerate(splits):
            segment = split if i < 1 else split - splits[i-1][1]
            total_time_str = format_time(split)
            segment_time_str = format_time(segment)
            level_strs = format_level(level)
            x = start_x + (step_x * i)
            cv2.rectangle(GUIOverlay.bg_img, (step_x*i, 0), (step_x*(i+1), bar_height), (80, 80, 80), -1)
            cv2.rectangle(GUIOverlay.bg_img, (step_x*i, 0), (step_x*(i+1), bar_height), (0, 0, 0), 1)
            for lvl_s, lvl_y in level_strs:
                cv2.putText(GUIOverlay.bg_img, lvl_s, (x, lvl_y),
                            cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 1)
            cv2.putText(GUIOverlay.bg_img, total_time_str, (x, 60),
                        cv2.FONT_HERSHEY_PLAIN, 1.6, (60, 230, 30), 2)
            cv2.putText(GUIOverlay.bg_img, "("+segment_time_str+")", (x, 90),
                        cv2.FONT_HERSHEY_PLAIN, 1.6, (40, 160, 40), 2)

    @staticmethod
    def draw_speedrun_time(s_time):
        sw, _ = win_util.get_screen_size()
        time_str = format_time(s_time, 0)
        draw_text(GUIOverlay.bg_img, time_str, (sw+120, -50), 2.8, (255, 255, 255), 2)

    @staticmethod
    def draw_modules(positions, names):
        offset = 150
        for ((x, y), name) in zip(positions, names):
            draw_rect(GUIOverlay.bg_img, (x-offset, y-offset),
                      (x+offset, y+offset+10), (0, 0, 255), 5)
            if name is not None:
                text_x = x-(len(name) * 8)
                draw_text(GUIOverlay.bg_img, name, (text_x, y-offset+30), 1.8, (120, 30, 30), 2)

    @staticmethod
    def draw_module_selected(module):
        size = 300
        x, y, index = module
        GUIOverlay.selected_module = (x, y)
        for i in range(6):
            offset_x = (i % 3) - (index % 3)
            offset_y = 0
            offset_x = offset_x * size
            if (i > 2) ^ (index > 2):
                offset_y = 300 if i > index else -300
            if index != i:
                draw_rect(GUIOverlay.bg_img, (x+offset_x, y+offset_y),
                          (x+offset_x+size, y+offset_y+size), (0, 0, 255), 5)
        draw_rect(GUIOverlay.bg_img, (x, y), (x+size, y+size), (35, 255, 35), 5)

    @staticmethod
    def log_info(info):
        sw, sh = win_util.get_screen_size()
        width = 350
        x = sw - width
        y_step = 20
        start_y = 0
        draw_rect(GUIOverlay.bg_img, (x-10, start_y), (sw, sh), (0, 0, 0), -1)
        max_lines = int(sh // 23) # 47 for 1080.
        for i, s in enumerate(info[-max_lines:]):
            draw_text(GUIOverlay.bg_img, s, (x, start_y+10+(y_step*i)), 1.2, (255, 255, 255), 1)

    @staticmethod
    def draw_maze(maze_name):
        maze = MAZES[maze_name]
        N = DIRECTIONS.North
        S = DIRECTIONS.South
        W = DIRECTIONS.West
        E = DIRECTIONS.East
        mod_x, mod_y = GUIOverlay.selected_module
        draw_text(GUIOverlay.bg_img, maze_name, (mod_x+100, mod_y+30), 1.5, (0, 0, 255), 2)
        mod_x += 60
        mod_y += 72
        step = 25
        start = 3
        color = (255, 130, 0)
        for y, row in enumerate(maze):
            for x, dirs in enumerate(row):
                x_real = mod_x + start + (x * step)
                y_real = mod_y + start + (y * step)
                if N not in dirs:
                    draw_line(GUIOverlay.bg_img, (x_real, y_real),
                              (x_real+step, y_real), color, 2)
                if S not in dirs:
                    draw_line(GUIOverlay.bg_img, (x_real, y_real+step),
                              (x_real+step, y_real+step), color, 2)
                if W not in dirs:
                    draw_line(GUIOverlay.bg_img, (x_real, y_real),
                              (x_real, y_real+step), color, 2)
                if E not in dirs:
                    draw_line(GUIOverlay.bg_img, (x_real+step, y_real),
                              (x_real+step, y_real+step), color, 2)

    @staticmethod
    def draw_module_info(module, info):
        if module == 17: # Maze.
            GUIOverlay.draw_maze(info)

    @staticmethod
    def draw_order_cmp(prop):
        if prop == "debug_bg_img":
            return 0
        if prop == "speedrun_splits":
            return 1
        if prop in ("module_positions", "module_selected"):
            return 2
        return 3

    @staticmethod
    def pad_bg_img(img):
        sw, sh = win_util.get_screen_size()
        h, w = img.shape[:2]
        GUIOverlay.padding_x = sw-w
        GUIOverlay.padding_y = sh-h
        return np.pad(img, ((sh-h, 0), (0, sw-w), (0, 0)), "constant", constant_values=0)

    @staticmethod
    def remove_conflicting_prop(prop):
        conflicts = [
            ("module_selected", ["module_positions"]),
            ("module_positions", ["module_selected"]),
            ("speedrun_splits", ["module_positions", "module_selected"])
        ]
        for source, targets in conflicts: # :^)
            if (prop == source):
                for target in targets:
                    if target in GUIOverlay.properties:
                        del GUIOverlay.properties[target]
                        GUIOverlay.drawing_order.remove(target)

    @staticmethod
    def add_status(prop, value):
        GUIOverlay.lock.acquire(True)
        GUIOverlay.properties[prop] = value
        if not prop in GUIOverlay.drawing_order:
            GUIOverlay.remove_conflicting_prop(prop)
            GUIOverlay.drawing_order.append(prop)
            GUIOverlay.drawing_order.sort(key=GUIOverlay.draw_order_cmp)
        GUIOverlay.lock.release()

    @staticmethod
    def set_status(status_dict):
        GUIOverlay.properties = status_dict

    @staticmethod
    def draw_properties(props):
        for prop in props:
            value = GUIOverlay.properties[prop]
            if prop == "speedrun_splits":
                GUIOverlay.draw_speedrun_splits(value)
            elif prop == "speedrun_time":
                GUIOverlay.draw_speedrun_time(value)
            elif prop == "module_positions":
                names = GUIOverlay.properties.get("module_names", [None for _ in value])
                GUIOverlay.draw_modules(value, names)
            elif prop == "module_selected":
                GUIOverlay.draw_module_selected(value)
            elif prop == "module_info":
                GUIOverlay.draw_module_info(value[0], value[1])
            elif prop == "log":
                GUIOverlay.log_info(value)

    @staticmethod
    def erase_properties():
        GUIOverlay.create_bg_image()

    @staticmethod
    def draw_changed_properties():
        GUIOverlay.lock.acquire(True)
        GUIOverlay.draw_properties(GUIOverlay.drawing_order)
        GUIOverlay.lock.release()

    @staticmethod
    def create_bg_image():
        sw, sh = win_util.get_screen_size()
        padding = 20
        if "debug_bg_img" in GUIOverlay.properties:
            GUIOverlay.bg_img = np.copy(GUIOverlay.properties["debug_bg_img"])
        else:
            GUIOverlay.bg_img = np.zeros((sh-padding, sw-padding, 3), dtype="uint8")

    @staticmethod
    def create_window():
        sw, sh = win_util.get_screen_size()
        fps = 20

        path = "../resources/misc/recorded_runs/"
        num_files = len(glob(path+"*.avi"))
        record = "record" in argv
        record_path = f"{path}{num_files}.avi"
        mon_bbox = {"top": 0, "left": 300, "width": sw-300, "height": sh-100}
        sct = mss()
        if record:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            capture = cv2.VideoWriter(record_path, fourcc, float(fps), (sw, sh), True)

        cv2.namedWindow(GUIOverlay.window_name)
        cv2.moveWindow(GUIOverlay.window_name, sw-15, 0)
        time_started = GUIOverlay.properties.get("speedrun_time", None)
        timestamp = int(time())

        try:
            while GUIOverlay.is_active:
                img = sct.grab(mon_bbox)
                img = np.array(img)
                GUIOverlay.bg_img = GUIOverlay.pad_bg_img(img)
                if time_started is not None:
                    new_time = int(time())
                    if new_time > timestamp:
                        timestamp = new_time
                        GUIOverlay.add_status("speedrun_time", timestamp - time_started)
                elif "speedrun_time" in GUIOverlay.properties:
                    time_started = GUIOverlay.properties["speedrun_time"]
                GUIOverlay.draw_changed_properties()

                if record and time_started is not None:
                    img = cv2.cvtColor(GUIOverlay.bg_img, cv2.COLOR_BGRA2BGR)
                    capture.write(img)
                cv2.imshow(GUIOverlay.window_name, GUIOverlay.bg_img)
                key = cv2.waitKey(1000 // fps)
                if key == ord('q'):
                    break
        finally:
            if record:
                capture.release()

    @staticmethod
    def shut_down():
        GUIOverlay.is_active = False
