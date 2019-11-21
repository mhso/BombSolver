from glob import glob
import cv2
import features.whos_first as whos_first_feat

FILE = "../resources/misc/3.png"
img = cv2.imread(FILE, cv2.IMREAD_COLOR)
masks, _, _ = whos_first_feat.get_characters(img)
for mask in masks:
    cv2.imshow("Test", mask)
    key = cv2.waitKey(0)
    if key == ord('q'):
        exit(0)
    cv2.destroyWindow("Test")
