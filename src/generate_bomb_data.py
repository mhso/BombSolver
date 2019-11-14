from glob import glob
import inspect_bomb
from debug import log

INCLUDED_MODULES = [10, 11, 15, 16, 18]
AUTO_LABEL = int(argv[2]) if len(argv) > 2 else False
MODEL = (None if not AUTO_LABEL else
         classifier.load_from_file("../resources/trained_models/module_model"))



def save_data(sides):
    NUM_IMAGES = len(glob("../resources/training_images/modules/*.png"))
    INDEX = NUM_IMAGES
    for side in sides:
        for img in side:
            img.save(f"../resources/training_images/modules/{INDEX:03d}.png")
            INDEX += 1

    log(f"Captured {INDEX-NUM_IMAGES} images. Total images: {INDEX}")

inspect_bomb.inspect_and_reset(save_data)
