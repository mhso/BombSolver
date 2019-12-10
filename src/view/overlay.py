from glob import glob
from threading import Thread, Lock
import numpy as np
import cv2
import util.windows_util as win_util

class GUIOverlay:
    def __init__(self):
        self.record = False
        self.bg_img = None
        self.properties = {}
        self.changed_properties = []
        self.lock = Lock()
        self.is_active = True
        self.window_name = "BombSolver"
        Thread(target=self.create_window).start()

    def draw_speedrun_splits(self, splits):
        pass

    def draw_speedrun_time(self, time):
        pass

    def draw_modules(self, positions, names):
        offset = 150
        self.erase_properties(["module_selected", "module_names"])
        for ((x, y), name) in zip(positions, names):
            cv2.rectangle(self.bg_img, (x-offset, y-offset),
                          (x+offset, y+offset+10), (0, 0, 255), 5)
            if name is not None:
                text_x = x-(len(name) * 8)
                cv2.putText(self.bg_img, name, (text_x, y-offset+30),
                            cv2.FONT_HERSHEY_PLAIN, 1.8, (120, 30, 30))

    def draw_module_selected(self, module):
        size = 300
        x, y, index = module
        self.erase_properties(["module_positions", "module_names"])
        for i in range(6):
            offset_x = (i % 3) - (index % 3)
            offset_y = 0
            offset_x = offset_x * size
            if (i > 2) ^ (index > 2):
                offset_y = 300 if i > index else -300
            if index != i:
                cv2.rectangle(self.bg_img, (x+offset_x, y+offset_y),
                              (x+offset_x+size, y+offset_y+size), (0, 0, 255), 5)
        cv2.rectangle(self.bg_img, (x, y), (x+size, y+size), (35, 255, 35), 5)

    def add_status(self, status, value):
        self.lock.acquire(True)
        self.properties[status] = value
        self.changed_properties.append(status)
        self.lock.release()

    def set_status(self, status_dict):
        self.properties = status_dict
        self.changed_properties = list(status_dict.keys())

    def draw_properties(self, props):
        for prop in props:
            value = self.properties[prop]
            if prop == "speedrun_splits":
                self.draw_speedrun_splits(value)
            elif prop == "speedrun_time":
                self.draw_speedrun_time(value)
            elif prop == "module_positions":
                names = self.properties.get("module_names", [None for _ in value])
                self.draw_modules(value, names)
            elif prop == "module_selected":
                self.draw_module_selected(value)
            elif prop == "debug_bg_img":
                self.bg_img = value

    def erase_properties(self, erased_props):
        self.create_blank_bg_image()
        self.changed_properties = set(self.properties.keys()) - set(erased_props)
        print(self.changed_properties)

    def draw_changed_properties(self):
        self.lock.acquire(True)
        self.draw_properties(self.changed_properties)
        self.changed_properties = []
        self.lock.release()

    def create_blank_bg_image(self):
        sw, sh = win_util.get_screen_size()
        padding = 20
        self.bg_img = np.zeros((sh-padding, sw-padding, 3), dtype="uint8")

    def create_window(self):
        sw, sh = win_util.get_screen_size()
        fps = 10

        self.create_blank_bg_image()

        path = "../../resources/misc/recorded_runs/"
        num_files = len(glob(path+".mov"))
        #capture = cv2.VideoCapture(f"{path}{num_files}.mov")

        cv2.namedWindow(self.window_name)
        cv2.moveWindow(self.window_name, sw-15, 0)

        while self.is_active:
            # if self.record:
            #     retval, frame = capture.read()
            #     if not retval:
            #         break

            self.draw_changed_properties()

            cv2.imshow(self.window_name, self.bg_img)
            key = cv2.waitKey(1000 // fps)
            if key == ord('q'):
                break

    def shut_down(self):
        self.is_active = False
