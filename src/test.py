from glob import glob
import cv2
import features.memory as mem_feat

FILES = glob("../resources/training_images/memory_game/*.png")
for file in FILES:
    img = cv2.imread(file, cv2.IMREAD_COLOR)
    masks, coords = mem_feat.get_characters(img)
    for mask in masks:
        cv2.imshow("Test", mask)
        key = cv2.waitKey(0)
        if key == ord('q'):
            exit(0)
        cv2.destroyWindow("Test")
