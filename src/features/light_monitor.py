from time import sleep
from threading import Thread, Event
from features import util as features_util
from windows_util import get_screen_size
from model.grab_img import screenshot
from debug import log

class LightMonitor:
    """
    The LightMonitor runs in a separate thread
    and monitors the random event in which the
    light turns off during the defusal of the bomb.
    """
    def __init__(self):
        self.pixel = (160, 10)
        self.change_event = Event()
        Thread(target=self.monitor).start()

    def monitor(self):
        _, SH = get_screen_size()
        lo = (30, 30, 30)
        hi = (255, 255, 255)
        lights_on = True
        self.change_event.set()
        while True:
            sc = screenshot(0, SH-200, 200, 200)
            img = features_util.convert_to_cv2(sc)
            rgb = features_util.split_channels(img)
            if lights_on:
                if not features_util.color_in_range(self.pixel, rgb, lo, hi):
                    log("Lights in the room are turned off. Pausing execution temporarily...")
                    lights_on = False
                    self.change_event.clear()
                    sleep(3)
            else:
                if features_util.color_in_range(self.pixel, rgb, lo, hi):
                    log("Lights in the room are turned back on. Resuming...")
                    self.change_event.set()
                    lights_on = True
                    sleep(3)
            sleep(0.25)

    def wait_for_light(self):
        self.change_event.wait()
