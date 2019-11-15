from time import sleep
from glob import glob
from sys import argv
import os
from cv2 import imwrite
import inspect_modules
import inspect_bomb
from debug import log
import windows_util as win_util
import main
from features.util import convert_to_cv2
import model.module_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import config

INCLUDED_LABELS = (3, 5, 6, 10, 11, 15, 16, 18)
INSPECTIONS = -1
if len(argv) > 1:
    if argv[1] in ("-h", "-help"):
        print("Usage: python generate_data.py " +
              "[inspections] [type (bomb|modules|both)] [auto_label]")
        exit(0)
    INSPECTIONS = int(argv[1])
DATA_TYPE = argv[2] if len(argv) > 2 else "bomb"
AUTO_LABEL = int(argv[3]) if len(argv) > 3 else False
config.MAX_GPU_FRACTION = 0.2
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

def process_bomb_data(images):
    IMAGES_CAPTURED = 0
    predictions = []
    for img in images:
        cv2_img = convert_to_cv2(img)
        resized = dataset_util.reshape(cv2_img, config.INPUT_DIM[1:])
        pred = classifier.predict(MODEL, resized)
        label = classifier_util.get_best_prediction(pred)[0]
        predictions.append(label)
        if label in INCLUDED_LABELS:
            label_name = clean_file_path(classifier.LABELS[label])
            path = f"../resources/training_images/modules/{label_name}"
            num_images = len(glob(path + "*.png"))
            imwrite(f"{path}{num_images:03d}.png", cv2_img)
            IMAGES_CAPTURED += 1

    log(f"Captured {IMAGES_CAPTURED} bomb images.")
    return predictions

def clean_file_path(path):
    return path.replace("?", "").replace("'", "").replace(" ", "_").lower()

def process_module_data(images, predictions=None):
    IMAGES_CAPTURED = 0
    for i, img in enumerate(images):
        cv2_img = convert_to_cv2(img)
        path = None
        if predictions is not None:
            label = predictions[i]
            if label in INCLUDED_LABELS:
                label_name = clean_file_path(classifier.LABELS[label])
                path = f"../resources/training_images/modules/{label_name}/"
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
main.sleep_until_start()

if "skip" not in argv:
    main.start_level()
    main.await_level_start()

while INSPECTIONS:
    data = inspect_bomb.inspect()
    PREDICTIONS = process_bomb_data(data, DATA_TYPE == "modules")
    if DATA_TYPE in ("modules", "both"):
        data, FILTERED_PREDICTIONS = inspect_modules.inspect(PREDICTIONS, INCLUDED_LABELS)
        process_module_data(data, FILTERED_PREDICTIONS)
    if "skip" not in argv or INSPECTIONS > 1:
        restart_level()
    INSPECTIONS -= 1
