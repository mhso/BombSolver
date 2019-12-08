from glob import glob
from time import sleep
from features import bomb_duration
import util.windows_util as win_util
import cv2

def sleep_until_start():
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

sleep_until_start()
masks = bomb_duration.get_characters()
PATH = "../resources/training_images/timer/"
INDEX = len(glob(PATH+"*.png"))
for mask in masks:
    cv2.imwrite(f"{PATH}{INDEX:03d}.png", mask)
    print("Saved timer image.")
    INDEX += 1
