from time import sleep
from glob import glob
from sys import argv
import os
from cv2 import imwrite
import inspect_modules
import inspect_bomb
from debug import log
import windows_util as win_util
from main import sleep_until_start
from features.util import convert_to_cv2
import model.module_classifier as classifier
import model.dataset_util as dataset_util
import config

INCLUDED_BOMB_LABELS = [3, 5, 6]
INCLUDED_MODULE_LABELS = [10, 11, 15, 16, 18]
INSPECTIONS = -1
if len(argv) > 1:
    INSPECTIONS = int(argv[1])
DATA_TYPE = argv[2] if len(argv) > 2 else "bomb"
AUTO_LABEL = int(argv[3]) if len(argv) > 3 else False
MODEL = (None if not AUTO_LABEL else
         classifier.load_from_file("../resources/trained_models/module_model"))

def restart_level():
    SW, SH = win_util.get_screen_size()
    win_util.click(int(SW * 0.9), int(SH * 0.8), btn="right")
    sleep(1)
    win_util.click(int(SW * 0.73), int(SH * 0.65))
    sleep(1)
    win_util.click(int(SW * 0.73), int(SH * 0.45))
    sleep(2)
    win_util.click(int(SW * 0.52), int(SH * 0.53))
    sleep(0.8)
    win_util.click(int(SW * 0.55), int(SH * 0.53))
    sleep(0.5)

def process_bomb_data(images, just_predict):
    IMAGES_CAPTURED = 0
    predictions = []
    for img in images:
        cv2_img = convert_to_cv2(img)
        path = None
        if AUTO_LABEL:
            resized = dataset_util.resize_img(dataset_util.pad_image(cv2_img), config.INPUT_DIM[1:])
            label = classifier.predict(MODEL, resized)[0]
            if label in INCLUDED_BOMB_LABELS or label in INCLUDED_MODULE_LABELS:
                predictions.append(label)
                path = f"../resources/labeled_images/{label}/"
        else:
            path = f"../resources/training_images/modules/"
        if path is not None and not just_predict:
            num_images = len(glob(path + "*.png"))
            imwrite(f"{path}{num_images:03d}.png", cv2_img)
            IMAGES_CAPTURED += 1

    log(f"Captured {IMAGES_CAPTURED} bomb images.")
    return predictions

def process_module_data(images, predictions=None):
    IMAGES_CAPTURED = 0
    for i, img in enumerate(images):
        cv2_img = convert_to_cv2(img)
        path = None
        if predictions is not None:
            label = predictions[i]
            if label in INCLUDED_MODULE_LABELS:
                path = f"../resources/training_images/modules/{label}/"
                if not os.path.exists(path):
                    os.mkdir(path)
        else:
            path = f"../resources/training_images/modules/"
        if path is not None:
            num_images = len(glob(path + "*.png"))
            imwrite(f"{path}{num_images:03d}.png", cv2_img)
            IMAGES_CAPTURED += 1

    log(f"Captured {IMAGES_CAPTURED} module images.")

inspect_str = "infinitely many" if INSPECTIONS == -1 else str(INSPECTIONS)
log(f"Running {inspect_str} times.")

log("Waiting for user to press S")
sleep_until_start()

while INSPECTIONS:
    predictions = None
    if DATA_TYPE in ("bomb", "both") or AUTO_LABEL:
        data = inspect_bomb.inspect()
        predictions = process_bomb_data(data, DATA_TYPE == "modules")
    if DATA_TYPE in ("modules", "both"):
        data = inspect_modules.inspect()
        process_module_data(data, predictions)
    restart_level()
    INSPECTIONS -= 1
