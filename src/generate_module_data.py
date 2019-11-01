from glob import glob
import inspect_bomb
from debug import log

def save_data(sides):
    NUM_IMAGES = len(glob("../resources/training_images/*.png"))
    INDEX = NUM_IMAGES
    for side in sides:
        for img in side:
            img.save(f"../resources/training_images/{INDEX:03d}.png")
            INDEX += 1

    log(f"Captured {INDEX-NUM_IMAGES} images. Total images: {INDEX}")

inspect_bomb.inspect_and_reset(save_data)
