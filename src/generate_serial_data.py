from os import unlink
from glob import glob
import cv2
from features import serial_number
from features import indicator
from features import button
from debug import log
import config

config.VERBOSITY = 1

PATHS = ("/bomb/serial/", "/bomb/indicator/", "/modules/button/")
FEATURE_EXTRACTORS = (serial_number, indicator, button)

for i, base_path in enumerate(PATHS):
    path = "../resources/training_images" + base_path
    FILES = glob(path + "images/*.png")
    NUM_IMAGES = len(glob(path + "*.png"))
    INDEX = NUM_IMAGES
    for file in FILES:
        img = cv2.imread(file, cv2.IMREAD_COLOR)
        masks, _ = FEATURE_EXTRACTORS[i].get_characters(img)
        for mask in masks:
            if mask is None:
                print("MASK IS NONE :(")
                exit(0)
            cv2.imwrite(f"{path}{INDEX:03d}.png", mask)
            INDEX += 1
        unlink(file)

    log(f"Captured {INDEX-NUM_IMAGES} images. Total images: {INDEX}")
