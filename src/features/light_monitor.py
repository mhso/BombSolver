from time import sleep
from threading import Thread, Event
from _thread import interrupt_main
from features import util as features_util
from util.windows_util import get_screen_size
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
        self.is_active = False

    def start(self):
        self.is_active = True
        self.lights_on = True
        self.exploded = False
        Thread(target=self.monitor).start()

    def bomb_exploded(self, rgb):
        lo = (0, 0, 0)
        hi = (3, 3, 3)
        return features_util.color_in_range(self.pixel, rgb, lo, hi)

    def exit_after_explosion(self):
        log("Bomb Exploded... Whoops.")
        interrupt_main()

    def monitor(self):
        _, SH = get_screen_size()
        lo = (30, 30, 30)
        hi = (255, 255, 255)
        self.change_event.set()
        while self.is_active:
            sc = screenshot(0, SH-200, 200, 200)
            img = features_util.convert_to_cv2(sc)
            rgb = features_util.split_channels(img)
            if self.lights_on:
                if not features_util.color_in_range(self.pixel, rgb, lo, hi):
                    if self.bomb_exploded(rgb): # We died :(
                        self.is_active = False
                        self.exit_after_explosion()
                    else:
                        log("Lights in the room are turned off. Pausing execution temporarily...")
                        self.lights_on = False
                        self.change_event.clear()
                        sleep(1)
            else:
                if features_util.color_in_range(self.pixel, rgb, lo, hi):
                    log("Lights in the room are turned back on. Resuming...")
                    self.change_event.set()
                    self.lights_on = True
                    sleep(1)
            sleep(0.25)

    def wait_for_light(self):
        self.change_event.wait()

    def shut_down(self):
        self.is_active = False
