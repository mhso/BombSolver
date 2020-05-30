from glob import glob
from time import sleep
import numpy as np
import cv2
import config
import model.character_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import util.windows_util as win_util
import features.util as features_util
from debug import log

def indicator_bbox(img):
    a = np.where(img != 0)
    bbox = np.min(a[0]), np.max(a[0]), np.min(a[1]), np.max(a[1])
    return bbox

def get_threshold(img):
    copy = img.copy()
    gray = cv2.cvtColor(copy, cv2.COLOR_BGR2GRAY)
    inverted = 255 - gray
    thresh = cv2.Canny(gray, 140, 255)
    bbox = indicator_bbox(thresh)
    min_y, max_y, min_x, max_x = bbox
    inverted = inverted[min_y:max_y, min_x:max_x]
    thresh = cv2.threshold(inverted, 50, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh, bbox

def largest_bounding_rect(contours):
    min_x = 9999
    min_y = 9999
    max_x = 0
    max_y = 0
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if x < min_x:
            min_x = x
        if y < min_y:
            min_y = y
        if x+w > max_x:
            max_x = x+w
        if y+h > max_y:
            max_y = y+h
    return (min_x, min_y, max_x, max_y)

def get_segmented_image(image):
    thresh, bbox = get_threshold(image)
    contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]

    return thresh, contours, bbox

def get_masked_images(image, contours):
    mask = np.zeros(image.shape[:2], dtype="uint8")

    contours.sort(key=lambda c: cv2.boundingRect(c)[1])

    masks = []
    curr_contours = []
    sub_mask = mask.copy()
    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        mid_y = y + (h/2)
        next_y = -1
        if i < len(contours) - 1:
            x2, y2, w2, h2 = cv2.boundingRect(contours[i+1])
            next_y = y2 + (h2/2)
        curr_contours.append(c)
        if next_y == -1 or abs(mid_y - next_y) > 5:
            cv2.drawContours(sub_mask, curr_contours, -1, (255, 255, 255), -1)
            x1, y1, x2, y2 = largest_bounding_rect(curr_contours)
            curr_contours = []
            cropped = sub_mask[y1:y2, x1:x2]
            masks.append(cropped)
            sub_mask = mask.copy()

    filtered_masks = []
    for mask in masks:
        if mask.shape[0] > 2 and mask.shape[1] > 2:
            filtered_masks.append(mask)

    while len(filtered_masks) > 3:
        index = 0
        max_w = 0
        for i, mask in enumerate(filtered_masks):
            if mask.shape[0] > max_w:
                max_w = mask.shape[0]
                index = i
        filtered_masks.pop(index)

    return filtered_masks

def determine_alignment(image, bbox, lit):
    if lit:
        return lit
    mid_x = (bbox[2] + bbox[3]) // 2
    q = abs(bbox[3] - bbox[2]) // 4
    q1_x = (bbox[2] + q)
    q3_x = abs(bbox[2] - bbox[3]) - q + bbox[2]
    x_coords = [q1_x, mid_x, q3_x]
    y_coords = [bbox[1]-30, bbox[1]-60, bbox[0]+30, bbox[0]+60]
    for x in x_coords:
        for i, y in enumerate(y_coords):
            h, _ = image.shape[:2]
            if y >= h or y < 0:
                continue
            min_c, max_c = ((25, 25, 25), (45, 45, 45))
            rgb = features_util.split_channels(image)
            pixel = (y, x)
            if features_util.color_in_range(pixel, rgb, min_c, max_c):
                return 1 if i < 2 else -1
    return 0

def rotate_masks(masks, alignment):
    rotated = []
    for mask in masks:
        if alignment == -1:
            rotated.append(cv2.rotate(mask, cv2.ROTATE_90_COUNTERCLOCKWISE))
        else:
            rotated.append(cv2.rotate(mask, cv2.ROTATE_90_CLOCKWISE))
    return rotated

def indicator_is_lit(image):
    h, w = image.shape[:2]
    offsets = [30, 60]
    for offset in offsets:
        if image[h-offset, w//2] > 240:
            return 1
        if image[offset, w//2] > 240:
            return -1
    return 0

def get_characters(image):
    h, w = image.shape[:2]
    thresh, contours, bbox = get_segmented_image(image)
    gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    lit = indicator_is_lit(gray[bbox[0] : bbox[1], bbox[2] : bbox[3]])
    log(f"Indicator is {'lit' if lit else 'not lit'}", config.LOG_DEBUG, "Indicator")
    masks = get_masked_images(image, contours)
    if len(masks) != 3:
        log(f"WARNING: Length of indicator masks != 3 (len={len(masks)}).", config.LOG_WARNING)
    alignment = determine_alignment(image, bbox, lit)
    if not alignment:
        log("WARNING: Indicator alignment could not be determined!", config.LOG_WARNING)
    else:
        log(f"Indicator is {'left' if alignment == 1 else 'right'} aligned.", config.LOG_DEBUG, "Indicator")
    masks = rotate_masks(masks, alignment)
    if alignment == 1:
        masks.reverse()
    return masks, bool(lit)

def format_label(prediction):
    return prediction[0] + prediction[1] + prediction[2]

def get_indicator_features(image, model):
    masks, lit = get_characters(image)
    masks = [dataset_util.reshape(mask, config.CHAR_INPUT_DIM[1:]) for mask in masks]
    prediction = classifier.predict(model, np.array(masks))
    best_pred = classifier_util.get_best_prediction(prediction)
    return lit, format_label([classifier.LABELS[p] for p in best_pred])
