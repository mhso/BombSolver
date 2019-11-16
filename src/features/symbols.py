import numpy as np
from model import (dataset_util,
                   symbol_classifier as classifier,
                   classifier_util)
import cv2
import config

def get_threshold(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)[1]
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

def mid_bbox(bbox):
    return (bbox[0] + (bbox[2]/2), bbox[1] + (bbox[3]/2))

def segment_image(img):
    _, contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    min_y = 10000
    min_cont = -1
    for i, cont in enumerate(contours):
        _, mid_y = mid_bbox(cv2.boundingRect(cont))
        if mid_y < min_y:
            min_y = mid_y
            min_cont = i
    contours.pop(min_cont)
    mask = np.zeros(img.shape, dtype="uint8")
    cv2.drawContours(mask, contours, -1, (255, 255, 255), -1)
    return mask

def get_characters(img):
    symbols, coords = crop_and_split_img(img)
    masks = []
    for symbol in symbols:
        thresh = get_threshold(symbol)
        mask = segment_image(thresh)
        masks.append(mask)
    return masks, coords

def reshape_masks(masks):
    resized_masks = []
    for mask in masks:
        reshaped = mask.reshape(mask.shape + (1,))
        padded = dataset_util.pad_image(reshaped)
        resized = dataset_util.resize_img(padded, config.CHAR_INPUT_DIM[1:])
        repeated = np.repeat(resized.reshape(((1,) + config.CHAR_INPUT_DIM[1:])), 3, axis=0)
        resized_masks.append(repeated)
    return np.array(resized_masks)

def get_symbols(img, model):
    masks, coords = get_characters(img)
    masks = reshape_masks(masks)
    prediction = classifier.predict(model, masks)
    best_pred = classifier_util.get_best_prediction(prediction)
    print(f"Symbols: {[classifier.LABELS[x] for x in best_pred]}")
    return best_pred, coords
