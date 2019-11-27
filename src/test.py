import cv2
import features.whos_first

img = cv2.imread("../resources/training_images/whos_on_first/082.png", cv2.IMREAD_COLOR)
masks = features.whos_first.get_characters(img)[0]
for mask in masks:
    cv2.imshow("Test", mask)
    key = cv2.waitKey(0)
    if key == ord('q'):
        exit(0)
    cv2.destroyWindow("Test")
