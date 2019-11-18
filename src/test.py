from glob import glob
import features.password as pw_features
import cv2

img = cv2.imread("../resources/training_images/password/002.png", cv2.IMREAD_COLOR)
masks = pw_features.get_characters(img)
for mask in masks:
    cv2.imshow("Test", mask)
    key = cv2.waitKey(0)
    cv2.destroyWindow("Test")
    if key == ord('q'):
        break
