import cv2
import numpy as np
import math

def get_threshold(img):
    inverted = 255 - cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(inverted, 50, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def get_bbox(img):
    a = np.where(img != 0)
    bbox = np.min(a[0]), np.max(a[0]), np.min(a[1]), np.max(a[1])
    return bbox

def get_serial_number(img):
    thresh = get_threshold(img)

    min_y, max_y, min_x, max_x = get_bbox(thresh)
    copy = cv2.cvtColor(img[min_y:max_y, min_x:max_x].copy(), cv2.COLOR_BGR2GRAY)

    thresh = cv2.threshold(copy, 70, 255, cv2.THRESH_BINARY_INV)[1]

    _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

    return copy, contours

def determine_orientation(img):
    pass

#img = cv2.imread("../resources/training_images/050.png", cv2.IMREAD_COLOR)
img = cv2.imread("../resources/training_images/026.png", cv2.IMREAD_COLOR)
image, contours = get_serial_number(img)
mask = np.zeros(image.shape[:2])

filtered_contours = []
for c in contours:
    circle = cv2.minEnclosingCircle(c)
    ps = math.pow(cv2.arcLength(c, True), 2)
    circularity = 0
    if ps > 0:
        circularity = (4*math.pi*cv2.contourArea(c))/ps
    print(circularity)
    if circularity > 0.08:
        filtered_contours.append(c)

cv2.drawContours(mask, filtered_contours, -1, (255, 255, 255), 1)

cv2.namedWindow("Wow")
#cv2.imshow("Wow", edges)
cv2.imshow("Wow", mask)
cv2.waitKey(0)
