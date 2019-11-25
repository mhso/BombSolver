import cv2
import features.needy_vent as feat

img = cv2.imread("../resources/misc/Vent.png", cv2.IMREAD_COLOR)
masks = feat.get_characters(img)
for mask in masks:
    cv2.imshow("Test", mask)
    key = cv2.waitKey(0)
    if key == ord('q'):
        break
    cv2.destroyWindow("Test")
