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

def repair_gaps(img):
    """
    Fills out gaps in letters, specifically the letter K,
    when they appear on screen.
    """
    y = int(img.shape[0] / 2) - 2
    last_white = 0
    for x in range(img.shape[1]):
        white = img[y, x] == 255
        if white and img[y, x-1] == 0 and x - last_white < 4:
            img[y-1:y+1, x-2:x] = 255
        if white:
            last_white = x
    return img

def get_masked_images(img, x_dist):
    contours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
    # Sort contours by x value.
    contours.sort(key=lambda c: features_util.mid_bbox(cv2.boundingRect(c))[0])

    # Combine contours that are less than 'x_dist' apart from each on the x-axis (or 30 on the y).
    contours = features_util.combine_contours(contours, x_dist, 40)
    #contours = features_util.combine_contours_better(filtered_contours, x_dist, 30)
    masks = []
    for c in contours:
        mask = np.zeros(img.shape, "uint8")
        cv2.drawContours(mask, c, -1, (255, 255, 255), -1)
        min_y, max_y, min_x, max_x = features_util.crop_to_content(mask, padding=2)
        mask = mask[min_y:max_y, min_x:max_x]
        masks.append(mask)

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
    thresh = repair_gaps(thresh)
    screen_masks = get_masked_images(thresh, 5)

    words = [screen_masks]
    masks = []
    if screen_masks == []: # Word on the screen is blank (empty).
        words = [None]
    else:
        masks = [m for m in screen_masks]
    label_images, coords = split_labels(img)
    for image in label_images:
        thresh = get_threshold(image)
        word = get_masked_images(thresh, 4)
        words.append(word)
        masks.extend(word)
    return masks, words, coords

def get_word(prediction):
    characters = [classifier.LABELS[x] for x in classifier_util.get_best_prediction(prediction)]
    if characters[:4] == ["w", "h", "a", "t"] and len(characters) == 5:
        characters[4] = "?" # Handle special case with question-mark after 'what'.
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
