import os
from sys import argv
from glob import glob
import cv2
import config
import model.dataset_util as dataset_util

def label_img(img, label, data_type):
    path = f"../resources/labeled_images/{data_type}/{label}/"
    if not os.path.exists(path):
        os.mkdir(path)
    img_index = len(glob(path + "*.png"))
    name = f"{path}{img_index:03d}.png"

    resized = None
    padded = dataset_util.pad_image(img)
    if data_type == "modules":
        resized = dataset_util.resize_img(padded, (config.INPUT_DIM[1], config.INPUT_DIM[2]))
    elif data_type == "serial":
        resized = dataset_util.resize_img(padded, (config.SERIAL_INPUT_DIM[1], config.SERIAL_INPUT_DIM[2]))
    cv2.imwrite(name, resized)

if len(argv) == 1:
    print("Need to specify data type!")
    exit(0)

DATA_TYPE = argv[1]

FILES = glob(f"../resources/training_images/{DATA_TYPE}/*.png")
if len(FILES) == 0:
    print("No data to label, exiting...")
    exit(0)
cv2.namedWindow("Data labeling")
for i, file in enumerate(FILES):
    img = cv2.imread(file, cv2.IMREAD_COLOR)
    cv2.imshow("Data labeling", img)
    key = cv2.waitKey(0)
    if key == ord('q'):
        break
    elif key == ord('s'):
        continue
    elif key == ord('d'):
        os.unlink(file)
        continue
    key_val = chr(key)
    while True:
        key = cv2.waitKey(0)
        if key == ord("c"):
            os.unlink(file)
            break
        key_val += chr(key)
    label_img(img, int(key_val), DATA_TYPE)
    print(f"Labeled: {int(key_val)} ({config.LABELS[int(key_val)]}) ({(i+1)}/{len(FILES)})",
          flush=True)
