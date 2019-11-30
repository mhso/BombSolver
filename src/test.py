import cv2
import features.whos_first
import features.needy_knob
import features.maze

img = cv2.imread("../resources/misc/error_imgs/4.png", cv2.IMREAD_COLOR)
details = features.whos_first.get_characters(img)
masks = details[0]
for mask in masks:
    cv2.imshow("Test", mask)
    key = cv2.waitKey(0)
    if key == ord('q'):
        exit(0)
    cv2.destroyWindow("Test")
