from glob import glob
import cv2
import serial_number
from debug import log

FILES = glob("../resources/training_images/serial/images/*.png")
NUM_IMAGES = len(glob("../resources/training_images/serial/*.png"))
INDEX = NUM_IMAGES
for file in FILES:
    img = cv2.imread(file, cv2.IMREAD_COLOR)
    masks = serial_number.get_characters(img)
    for mask in masks:
        cv2.imwrite(f"../resources/training_images/{INDEX:03d}.png", mask)
        INDEX += 1

log(f"Captured {INDEX-NUM_IMAGES} images. Total images: {INDEX}")
