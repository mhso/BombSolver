from sys import argv
from time import sleep
from numpy import array
import windows_util as win_util
import solvers.simon_solver as solver
from model.grab_img import screenshot
import cv2

features = {"contains_vowel" : False}
if len(argv) == 2:
    features["contains_vowel"] = int(argv[1]) == 1

def screenshot_module():
    SW, SH = win_util.get_screen_size()
    x = int(SW * 0.43)
    y = int(SH*0.36)
    return screenshot(x, y, 300, 300), x, y

def sleep_until_start():
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

sleep_until_start()
print("Running...")

SC, mod_x, mod_y = screenshot_module()
image = cv2.cvtColor(array(SC), cv2.COLOR_RGB2BGR)
num = 1
while not solver.is_solved(image):
    btn_coords = solver.solve(image, screenshot_module, features, num)
    for coords in btn_coords:
        button_y, button_x = coords
        win_util.click(mod_x + button_x, mod_y + button_y)
        sleep(0.5)
    sleep(1)
    num += 1
    SC, _, _ = screenshot_module()
    image = cv2.cvtColor(array(SC), cv2.COLOR_RGB2BGR)
