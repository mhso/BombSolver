from glob import glob
from time import time, sleep
from os import mkdir
from pickle import dump
from threading import Thread
from multiprocessing import Process, Pipe
from queue import Queue
from mss import mss
import numpy as np
import util.windows_util as win_util

def save_video_frame(filename, queue):
    frames = 0
    while True:
        data = queue.get(True)
        if data is None:
            break
        with open(f"{filename}{frames}.bin", "wb") as f:
            dump(data, f)
        frames += 1

def initialize():
    receiver, sender = Pipe(False)
    Process(target=GUIOverlay.create_window, args=(receiver,)).start()
    return sender

def listen(conn):
    while GUIOverlay.is_active:
        prop, value = conn.recv()
        if prop == "active":
            GUIOverlay.is_active = value
        else:
            GUIOverlay.add_property(prop, value)

class GUIOverlay:
    bg_img = None
    properties = {}
    is_active = True
    window_name = "BombSolver"

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
        for source, targets in conflicts:
            if prop == source:
                for target in targets:
                    if target in GUIOverlay.properties:
                        del GUIOverlay.properties[target]

    @staticmethod
    def add_property(prop, value):
        GUIOverlay.properties[prop] = value

    @staticmethod
    def set_status(status_dict):
        GUIOverlay.properties = status_dict

    @staticmethod
    def erase_properties():
        GUIOverlay.create_bg_image()

    @staticmethod
    def create_bg_image():
        sw, sh = win_util.get_screen_size()
        padding = 20
        if "debug_bg_img" in GUIOverlay.properties:
            GUIOverlay.bg_img = np.copy(GUIOverlay.properties["debug_bg_img"])
        else:
            GUIOverlay.bg_img = np.zeros((sh-padding, sw-padding, 3), dtype="uint8")

    @staticmethod
    def create_window(conn):
        sw, sh = win_util.get_screen_size()

        path = "../resources/misc/recorded_runs/"
        num_files = len(glob(path+"*"))
        record_path = f"{path}{num_files+1}/"
        mkdir(record_path)

        mon_bbox = {"top": 0, "left": 300, "width": sw-300, "height": sh-100}
        sct = mss()

        queue = Queue(5)
        io_thread = Thread(target=save_video_frame, args=(record_path, queue))
        io_thread.start()

        Thread(target=listen, args=(conn,)).start()

        try:
            while not GUIOverlay.is_active:
                sleep(0.1) # Wait for start.

            time_started = GUIOverlay.properties.get("speedrun_time", None)
            timestamp = int(time())
            while GUIOverlay.is_active:
                img = np.array(sct.grab(mon_bbox))
                img = GUIOverlay.pad_bg_img(img)
                if time_started is not None:
                    new_time = int(time())
                    if new_time > timestamp:
                        timestamp = new_time
                        GUIOverlay.add_property("speedrun_time", timestamp - time_started)
                elif "speedrun_time" in GUIOverlay.properties:
                    time_started = GUIOverlay.properties["speedrun_time"]

                if time_started is not None:
                    data = (img, GUIOverlay.properties, time() - time_started)
                    queue.put(data, True)
        except KeyboardInterrupt:
            return
        finally:
            queue.put(None)

    @staticmethod
    def shut_down():
        GUIOverlay.is_active = False
