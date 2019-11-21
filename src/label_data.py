import os
from sys import argv
from glob import glob
import cv2
import config
import model.dataset_util as dataset_util
from model.module_classifier import LABELS as MODULE_LABELS
from model.symbol_classifier import LABELS as SYMBOL_LABELS

def label_img(img, label, data_type):
    path = f"../resources/labeled_images/{data_type}/{label}/"
    if not os.path.exists(path):
        os.mkdir(path)
    img_index = len(glob(path + "*.png"))
    name = f"{path}{img_index:03d}.png"

    reshaped = dataset_util.pad_image(img)
    if data_type == "modules":
        if label == 3:
            serial_path = "../resources/training_images/serial_number/"
            index = len(glob(serial_path + "*.png"))
            cv2.imwrite(f"{serial_path}{index:03d}.png", img)
        elif label == 6:
            indicator_path = "../resources/training_images/indicator/"
            index = len(glob(indicator_path + "*.png"))
            cv2.imwrite(f"{indicator_path}{index:03d}.png", img)
        reshaped = dataset_util.resize_img(reshaped, config.MODULE_INPUT_DIM[1:])
    elif data_type == "characters":
        reshaped = dataset_util.resize_img(reshaped, config.CHAR_INPUT_DIM[1:])
    elif data_type == "symbols":
        reshaped = dataset_util.resize_img(reshaped, config.SYMBOLS_INPUT_DIM[1:])
    cv2.imwrite(name, reshaped)
    new_len = len(glob(path + "*.png"))
    if new_len == img_index:
        return False
    return True

VALID_TYPES = ("characters", "modules", "symbols")
if len(argv) == 1:
    print(f"Need to specify data type! Valid types: {VALID_TYPES}.")
    exit(0)

DATA_TYPE = argv[1]
if DATA_TYPE not in VALID_TYPES:
    print("Invalid data type! Valid types: {POSSIBLE_TYPES}.")
    exit(0)

if DATA_TYPE == "characters":
    FOLDERS = ("button", "indicator", "serial_number", "timer",
               "password", "memory_game", "whos_on_first")
    FILES = []
    for folder in FOLDERS:
        FILES = FILES + glob(f"../resources/training_images/{folder}/generated_data/*.png")
elif DATA_TYPE == "symbols":
    FILES = glob(f"../resources/training_images/symbols/generated_data/*.png")
else:
    FILES = glob(f"../resources/training_images/*.png")
if FILES == []:
    print("No data to label, exiting...")
    exit(0)

cv2.namedWindow("Data labeling")

for i, file in enumerate(FILES):
    img = cv2.imread(file, cv2.IMREAD_COLOR)
    cv2.destroyWindow("Data labeling")
    cv2.imshow("Data labeling", img)
    key = cv2.waitKey(0)
    if key == 27: # Escape
        break
    elif key == 32: # Space
        os.unlink(file)
        continue
    key_val = chr(key)
    label = key_val
    label_desc = label
    if DATA_TYPE in ("modules", "symbols"):
        while True:
            key = cv2.waitKey(0)
            if key == ord("c"):
                break
            key_val += chr(key)
        label = int(key_val)
        label_desc = MODULE_LABELS[label] if DATA_TYPE == "modules" else SYMBOL_LABELS[label]
    success = label_img(img, label, DATA_TYPE)
    if not success:
        print("ERROR: Image overwritten!")
        break
    os.unlink(file)
    print(f"Labeled: {label} ({label_desc}) ({(i+1)}/{len(FILES)})",
          flush=True)
