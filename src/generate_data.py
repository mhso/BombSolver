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

#INCLUDED_LABELS = (3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
INCLUDED_LABELS = (11, 15, 16, 18)
INSPECTIONS = -1
if len(argv) > 1:
    if argv[1] in ("-h", "-help"):
        print("Usage: python generate_data.py " +
              "[type (modules|bomb|both)] [inspections] [auto_label]")
        exit(0)
    DATA_TYPE = argv[1]
INSPECTIONS = int(argv[2]) if len(argv) > 2 else -1
AUTO_LABEL = int(argv[3]) if len(argv) > 3 else True
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
        resized = dataset_util.reshape(cv2_img, config.MODULE_INPUT_DIM[1:])
        pred = classifier.predict(MODEL, resized)
        label = classifier_util.get_best_prediction(pred)[0]
        predictions.append(label)
        if label in INCLUDED_LABELS and DATA_TYPE != "modules":
            path = f"../resources/training_images/"
            if label < 7:
                label_name = clean_file_path(classifier.LABELS[label])
                path = f"{path}{label_name}/"
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
                path = f"../resources/training_images/{label_name}/"
                if not os.path.exists(path):
                    os.mkdir(path)
        else:
            path = f"../resources/training_images/"
        if path is not None:
            num_images = len(glob(path + "*.png"))
            imwrite(f"{path}{num_images:03d}.png", cv2_img)
            IMAGES_CAPTURED += 1

    log(f"Captured {IMAGES_CAPTURED} module images.")

inspect_str = "infinitely many" if INSPECTIONS == -1 else str(INSPECTIONS)
suffix = "times" if INSPECTIONS != 1 else "time"
log(f"Running {inspect_str} {suffix}.")
log(f"Auto labeling {'enabled' if AUTO_LABEL else 'disabled'}.")

log("Waiting for user to press S")
main.sleep_until_start()

while INSPECTIONS:
    if "skip" not in argv:
        main.start_level()
    main.await_level_start()

    data = inspect_bomb.inspect()
    PREDICTIONS = process_bomb_data(data)
    if DATA_TYPE in ("modules", "both"):
        PREDICTIONS = PREDICTIONS[:12]
        data, FILTERED_PREDICTIONS = inspect_modules.inspect(PREDICTIONS, INCLUDED_LABELS)
        process_module_data(data, FILTERED_PREDICTIONS)
    if "skip" not in argv or INSPECTIONS > 1:
        restart_level()
    INSPECTIONS -= 1
