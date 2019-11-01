import cv2
import numpy as np

def get_serial_number(img):
    canny = cv2.Canny(img, threshold1=200, threshold2=255)
    return canny

def get_bbox(img):
    a = np.where(img != 0)
    bbox = np.min(a[0]), np.max(a[0]), np.min(a[1]), np.max(a[1])
    return bbox

img = cv2.imread("../resources/training_images/016.png", cv2.IMREAD_COLOR)
edges = get_serial_number(img)

min_y, max_y, min_x, max_x = get_bbox(edges)

edges = edges[min_y:max_y, min_x:max_x]


cv2.namedWindow("Wow")
cv2.imshow("Wow", edges)
cv2.waitKey(0)
