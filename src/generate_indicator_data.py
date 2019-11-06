from os import unlink
from glob import glob
import cv2
from features import indicator
from debug import log
import config

config.VERBOSITY = 1

FILES = glob("../resources/training_images/indicators/images/*.png")
NUM_IMAGES = len(glob("../resources/training_images/serial/*.png"))
INDEX = NUM_IMAGES
for file in FILES:
    img = cv2.imread(file, cv2.IMREAD_COLOR)
    masks, _ = indicator.get_characters(img)
    for mask in masks:
        if mask is None:
            print("MASK IS NONE :(")
            exit(0)
        cv2.imwrite(f"../resources/training_images/serial/{INDEX:03d}.png", mask)
        INDEX += 1
    unlink(file)

log(f"Captured {INDEX-NUM_IMAGES} images. Total images: {INDEX}")
