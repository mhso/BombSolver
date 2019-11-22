import numpy as np
import cv2
import features.util as features_util
import config
from model import (classifier_util, dataset_util, character_classifier as classifier)

LABEL_W, LABEL_H = 70, 28

def get_threshold(gray):
    thresh = cv2.threshold(gray, 65, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def crop_to_screen(img):
    x_min, y_min, x_max, y_max = 64, 44, 172, 70
    return cv2.cvtColor(img[y_min:y_max, x_min:x_max, :], cv2.COLOR_BGR2GRAY)

def split_labels(img):
    coords = [
        (126, 84), (126, 168),
        (174, 84), (174, 168),
        (223, 84), (223, 168)
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
    _, contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Sort contours by x value.
    contours.sort(key=lambda c: features_util.mid_bbox(cv2.boundingRect(c))[0])

    # Filter out contours that have an area of less than 9 (apostrophes fx.).
    filtered_contours = []
    for c in contours:
        if cv2.contourArea(c) > 8:
            filtered_contours.append(c)

    # Combine contours that are '4' apart from each on the x-axis (or 30 on the y).
    contours = features_util.combine_contours(filtered_contours, 4, 30)
    masks = []
    for c in contours:
        mask = np.zeros(img.shape, "uint8")
        cv2.drawContours(mask, c, -1, (255, 255, 255), -1)
        min_y, max_y, min_x, max_x = features_util.crop_to_content(mask, padding=2)
        masks.append(mask[min_y:max_y, min_x:max_x])

    # Split masks into two, if they are over '24' pixels in width.
    # This is because some letters are too close to each other for the contours
    # to be seperated.
    filtered_masks = []
    for mask in masks:
        if mask.shape[1] > 24:
            mask1 = mask[:, 0:12]
            mask2 = mask[:, 12:]
            filtered_masks.append(mask1)
            filtered_masks.append(mask2)
        elif mask.shape[0] > 12 or mask.shape[1] > 12:
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

def get_word(prediction):
    characters = [classifier.LABELS[x] for x in classifier_util.get_best_prediction(prediction)]
    if characters[0] == "y" and characters[2] == "u":
        characters[1] = "o"
    elif characters[:4] == ["w", "h", "a", "t"] and len(characters) == 5:
        characters[4] = "?"
    elif characters[:3] == ["d", "i", "s"] and characters[4:] == ["l", "a", "y"]:
        characters[3] = "p"
    return "".join(characters)

def get_words(img, model):
    _, words, coords = get_characters(img)
    predictions = []
    for masks in words:
        result = " "
        if masks is not None:
            masks = np.array([dataset_util.reshape(mask, config.CHAR_INPUT_DIM[1:]) for mask in masks])
            prediction = classifier.predict(model, masks)
            result = get_word(prediction)
        predictions.append(result)
    return predictions, coords
