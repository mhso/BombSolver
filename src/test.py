from glob import glob
from features import button
import cv2

FILES = glob("../resources/training_images/button/images/*.png")
cv2.namedWindow("Test")
for file in FILES:
    image = cv2.imread(file, cv2.IMREAD_COLOR)
    masks, color = button.get_characters(image)
    for mask in masks:
        cv2.destroyWindow("Test")
        cv2.imshow("Test", mask)
        key = cv2.waitKey(0)
        if key == ord('q'):
            break
