from time import time
import cv2
from view.overlay import GUIOverlay

test_img = cv2.imread("../resources/misc/test_full2.png", cv2.IMREAD_COLOR)
test_img = test_img[:-100, 300:, :]

GUIOverlay.add_status("speedrun_time", time())
GUIOverlay.start()

GUIOverlay.add_status("speedrun_splits", [("first_bomb", 30)])
GUIOverlay.add_status("speedrun_splits", [("first_bomb", 30), ("one_step_up", 45)])
GUIOverlay.add_status("speedrun_splits",
                      [("first_bomb", 30), ("one_step_up", 45), ("new_old", 100)])
GUIOverlay.add_status("module_selected", (825, 388, 4))
GUIOverlay.add_status("module_info", (17, "MAZE_2"))
GUIOverlay.add_status("log", ["Some data", "Some more data", "EVEN more data"])
