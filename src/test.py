import cv2
import features.whos_first
import features.needy_knob
import features.maze

img = cv2.imread("../resources/misc/error_imgs/3.png", cv2.IMREAD_COLOR)
masks = features.whos_first.get_characters(img)[0]
mask = features.needy_knob.get_threshold(img)
for mask in masks:
    cv2.imshow("Test", mask)
    key = cv2.waitKey(0)
    if key == ord('q'):
        exit(0)
    cv2.destroyWindow("Test")
