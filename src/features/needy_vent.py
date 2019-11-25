import numpy as np
import cv2
import features.util as features_util

def get_threshold(img):
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def segment_image(img):
    _, contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 1000:
            filtered_contours.append(c)

    contours = filtered_contours
    contours.sort(key=lambda c: features_util.mid_bbox(cv2.boundingRect(c))[0])

    contours = features_util.combine_contours(contours, 5, 30)
    masks = []
    for c in contours:
        mask = np.zeros(img.shape[:2], dtype="uint8")
        cv2.drawContours(mask, c, -1, (255, 255, 255), -1)
        masks.append(mask)
    return masks

def crop_image(img):
    min_y, min_x, max_y, max_x = 104, 78, 128, 230
    return img[min_y:max_y, min_x:max_x]

def get_characters(img):
    cropped = crop_image(img)
    thresh = get_threshold(cropped)
    return segment_image(thresh)
