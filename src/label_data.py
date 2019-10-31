import os
from glob import glob
import cv2
import numpy as np
import config
import model.dataset as dataset

def label_img(img, label):
    path = f"../resources/labeled_images/{label}/"
    if not os.path.exists(path):
        os.mkdir(path)
    img_index = len(glob(path + "*.png"))
    name = f"{path}{img_index:03d}.png"

    cv2.imwrite(name, dataset.resize_img(dataset.pad_image(img)))

FILES = glob("../resources/training_images/*.png")
if len(FILES) == 0:
    print("No data to label, exiting...")
    exit(0)
cv2.namedWindow("Data labeling")
for file in FILES:
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
    label_img(img, int(key_val))
    print(f"Labeled: {int(key_val)} ({config.LABELS[int(key_val)]})", flush=True)
