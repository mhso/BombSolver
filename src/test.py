from glob import glob
import os
import numpy as np
import cv2

exit(0)

for label in range(97, 123):
    letter = chr(label)
    files = glob(f"../resources/labeled_images/serial/{letter}/*.png")
    for file in files:
        print(file)
        img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
        if img.shape[1] < 32:
            os.unlink(file)
            img = cv2.resize(img, (32, 32), interpolation=cv2.INTER_AREA)
            cv2.imwrite(file, img)
