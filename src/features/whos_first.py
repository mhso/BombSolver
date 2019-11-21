import numpy as np
import cv2
import features.util as features_util
import config
from model import (classifier_util, dataset_util, character_classifier as classifier)

LABEL_W, LABEL_H = 60, 26

def get_threshold(gray):
    thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def crop_to_screen(img):
    x_min, y_min, x_max, y_max = 64, 44, 172, 70
    return cv2.cvtColor(img[y_min:y_max, x_min:x_max, :], cv2.COLOR_BGR2GRAY)

def split_labels(img):
    coords = [
        (126, 84), (126, 167),
        (174, 84), (174, 167),
        (223, 84), (223, 167)
    ]
    w = LABEL_W
    h = LABEL_H
    images = []
    for y, x in coords:
        y -= h // 2 # Coords are midpoint of the labels.
        x -= w // 2
        images.append(cv2.cvtColor(img[y:y+h, x:x+w, :], cv2.COLOR_BGR2GRAY))
    return images, coords

def get_masked_images(img):
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours.sort(key=lambda c: features_util.mid_bbox(cv2.boundingRect(c))[0])

    contours = features_util.combine_contours(contours, 5)
    masks = []
    for c in contours:
        mask = np.zeros(img.shape, "uint8")
        cv2.drawContours(mask, c, -1, (255, 255, 255), -1)
        min_y, max_y, min_x, max_x = features_util.crop_to_content(mask)
        masks.append(mask[min_y:max_y, min_x:max_x])

    filtered_masks = []
    for mask in masks:
        h, w = mask.shape
        if h > 5 or w > 5:
            filtered_masks.append(mask)
    return filtered_masks

def get_characters(img):
    screen = crop_to_screen(img)
    screen = 255 - screen
    thresh = get_threshold(screen)
    screen_masks = get_masked_images(thresh)
    words = [screen_masks]
    masks = []
    if screen_masks == []: # Word on the screen is blank (empty).
        screen_masks = None
        words = [screen_masks]
    else:
        masks = [m for m in screen_masks]
    labels, coords = split_labels(img)
    for image in labels:
        thresh = get_threshold(image)
        word = get_masked_images(thresh)
        words.append(word)
        masks.extend(word)
    return masks, words, coords

def get_words(img, model):
    _, words, coords = get_characters(img)
    predictions = []
    for masks in words:
        result = " "
        if masks is not None:
            masks = np.array([dataset_util.reshape(mask, config.CHAR_INPUT_DIM[1:]) for mask in masks])
            prediction = classifier.predict(model, masks)
            best_preds = [classifier.LABELS[x] for x in classifier_util.get_best_prediction(prediction)]
            result = "".join(best_preds)
        predictions.append(result)
    return predictions, coords
