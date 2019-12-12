from numpy import array
import cv2
import features.util as features_util
import config
from model import (classifier_util, dataset_util, character_classifier as classifier)

def get_threshold(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def crop_img(img):
    min_y, min_x, max_y, max_x = 94, 40, 192, 257
    return img[min_y:max_y, min_x:max_x]

def segment_image(img):
    contours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
    filtered_contours = []
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        if area < 1000:
            filtered_contours.append(c)

    filtered_contours.sort(key=lambda c: features_util.mid_bbox(cv2.boundingRect(c))[0])

    masks = []
    start_x = 6
    start_y = 10
    width = 41
    height = 70
    contour_index = -1
    for i in range(5):
        x = start_x + (i * width)
        sub_mask = img[start_y:start_y+height, x:x+width]
        curr_contours = []
        for j, c in enumerate(filtered_contours[contour_index:]):
            mid_x, _ = features_util.mid_bbox(cv2.boundingRect(c))
            if mid_x > x < x + width:
                if contour_index != -1:
                    contour_index = j
                curr_contours.append(c)
        contour_index = -1
        cv2.drawContours(sub_mask, curr_contours, -1, (255, 255, 255), -1)
        masks.append(sub_mask)

    return masks

def get_characters(img):
    cropped = crop_img(img)
    thresh = get_threshold(cropped)
    return segment_image(thresh)

def get_password(img, model):
    masks = get_characters(img)
    masks = array([dataset_util.reshape(mask, config.CHAR_INPUT_DIM[1:]) for mask in masks])
    prediction = classifier.predict(model, masks)
    best_pred = classifier_util.get_best_prediction(prediction)
    characters = [classifier.LABELS[x] for x in best_pred]
    return "".join(characters)
