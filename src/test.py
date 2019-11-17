import features.symbols as symbols_features
import cv2

img = cv2.imread("../resources/training_images/symbols/013.png", cv2.IMREAD_COLOR)

symbols, _ = symbols_features.get_characters(img)

cv2.namedWindow("Test")
for s in symbols:
    cv2.imshow("Test", s)
    key = cv2.waitKey(0)
    if key == ord('q'):
        exit(0)
