from numpy import array
import cv2
import features.util as features_util
import config
from model import (classifier_util, dataset_util, character_classifier as classifier)

LABEL_W, LABEL_H = 30, 60

def get_threshold(gray):
    thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def crop_to_screen(img):
    x_min, y_min, x_max, y_max = 84, 60, 164, 120
    return cv2.cvtColor(img[y_min:y_max, x_min:x_max, :], cv2.COLOR_BGR2GRAY)

def split_labels(img):
    coords = [
        (210, 60), (210, 105),
        (210, 148), (210, 192)
    ]
    w = LABEL_W
    h = LABEL_H
    images = []
    for y, x in coords:
        y -= h // 2 # Coords are midpoint of the labels.
        x -= w // 2
        images.append(cv2.cvtColor(img[y:y+h, x:x+w, :], cv2.COLOR_BGR2GRAY))
    return images, coords

def get_characters(img):
    screen = crop_to_screen(img)
    screen = 255 - screen
    labels, coords = split_labels(img)
    masks = []
    for image in [screen] + labels:
        thresh = get_threshold(image)
        min_y, max_y, min_x, max_x = features_util.crop_to_content(thresh)
        mask = thresh[min_y:max_y, min_x:max_x]
        masks.append(mask)
    masks[0] = dataset_util.resize_img(masks[0], (LABEL_W, LABEL_H))
    return masks, coords

def get_labels(img, model):
    masks, coords = get_characters(img)
    masks = array([dataset_util.reshape(mask, config.CHAR_INPUT_DIM[1:]) for mask in masks])
    prediction = classifier.predict(model, masks)
    return [x for x in classifier_util.get_best_prediction(prediction)], coords
