from sys import argv
from os import unlink
from glob import glob
import cv2
from features import (serial_number, indicator, button, symbols)
from debug import log
import config

config.VERBOSITY = 1

if len(argv) == 1:
    print("Please provide a data type to generate.")
    exit(0)

DATA_TYPE = argv[1]
DEL_IMAGES = True
if len(argv) > 2:
    DEL_IMAGES = int(argv[2]) == 1

FEATURE_EXTRACTORS = {
    "serial_number" : serial_number,
    "indicator" : indicator,
    "button" : button,
    "symbols" : symbols
}

INPUT_PATH = "../resources/training_images/modules/" + DATA_TYPE
OUTPUT_PATH = f"{INPUT_PATH}/generated_data/"

NUM_IMAGES = len(glob(OUTPUT_PATH + "*.png"))
INDEX = NUM_IMAGES

FILES = glob(INPUT_PATH + "/*.png")
for file in FILES:
    img = cv2.imread(file, cv2.IMREAD_COLOR)
    masks, _ = FEATURE_EXTRACTORS[DATA_TYPE].get_characters(img)
    for mask in masks:
        if mask is None:
            print("MASK IS NONE :(")
            exit(0)
        cv2.imwrite(f"{OUTPUT_PATH}{INDEX:03d}.png", mask)
        INDEX += 1
    if DEL_IMAGES:
        unlink(file)

log(f"Captured {INDEX-NUM_IMAGES} images. Total images: {INDEX}")
