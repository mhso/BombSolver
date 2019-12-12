import numpy as np
from model import (dataset_util,
                   symbol_classifier as classifier,
                   classifier_util)
import features.util as features_util
import cv2
import config
from debug import log, LOG_DEBUG

def get_threshold(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def crop_and_split_img(img):
    coords = [
        (123, 84), (123, 179),
        (213, 84), (213, 179)
    ]
    w = 84
    h = 82
    images = []
    for i in range(4):
        y, x = coords[i]
        y -= h // 2 # Coords are midpoint of the symbols.
        x -= w // 2
        images.append(img[y:y+h, x:x+w, :])
    return images, coords

def crop_to_symbol(img):
    a = np.where(img != 0)
    min_y, max_y, min_x, max_x = np.min(a[0]), np.max(a[0]), np.min(a[1]), np.max(a[1])
    return img[min_y:max_y, min_x:max_x]

def segment_image(img):
    contours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
    min_y = 10000
    min_cont = -1
    for i, cont in enumerate(contours):
        _, mid_y = features_util.mid_bbox(cv2.boundingRect(cont))
        if mid_y < min_y:
            min_y = mid_y
            min_cont = i
    contours.pop(min_cont)

    mask = np.zeros(img.shape, dtype="uint8")
    cv2.drawContours(mask, contours, -1, (255, 255, 255), 1)
    cv2.drawContours(mask, contours, -1, (255, 255, 255), -1)
    mask = crop_to_symbol(mask)

    return mask

def get_characters(img):
    symbols, coords = crop_and_split_img(img)
    masks = []
    for symbol in symbols:
        thresh = get_threshold(symbol)
        mask = segment_image(thresh)
        masks.append(mask)
    return masks, coords

def get_symbols(img, model):
    masks, coords = get_characters(img)
    masks = np.array([dataset_util.reshape(mask, config.SYMBOLS_INPUT_DIM[1:]) for mask in masks])
    prediction = classifier.predict(model, masks)
    best_pred = classifier_util.get_best_prediction(prediction)
    log(f"Symbols: {[classifier.LABELS[x] for x in best_pred]}", LOG_DEBUG, "Symbols")
    return best_pred, coords
