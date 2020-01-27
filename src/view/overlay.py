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
    def pad_bg_img(img, pad_x, pad_y):
        new_img = img
        new_img[pad_x:, :-pad_y] = 0
        return new_img

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

        mon_bbox = {"top": 0, "left": 0, "width": sw, "height": sh}
        sct = mss()

        queue = Queue(5)
        io_thread = Thread(target=save_video_frame, args=(record_path, queue))
        io_thread.start()

        Thread(target=listen, args=(conn,)).start()

        target_fps = 30
        secs_per_frame = 1 / target_fps

        try:
            while not GUIOverlay.is_active:
                sleep(0.1) # Wait for start.

            time_started = GUIOverlay.properties.get("speedrun_time", None)
            timestamp = int(time())
            while GUIOverlay.is_active:
                frame_time = time()
                img = np.array(sct.grab(mon_bbox))
                img = GUIOverlay.pad_bg_img(img, 300, 100)
                if time_started is not None:
                    new_time = int(time())
                    if new_time > timestamp:
                        timestamp = new_time
                        GUIOverlay.add_property("speedrun_time", timestamp - time_started)
                elif "speedrun_time" in GUIOverlay.properties:
                    time_started = GUIOverlay.properties["speedrun_time"]

                frame_time = time() - frame_time
                if frame_time < secs_per_frame:
                    sleep(secs_per_frame - frame_time)

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
