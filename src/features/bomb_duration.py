import math
import numpy as np
import cv2
import config
import model.character_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import windows_util as win_util
from debug import log
from model.grab_img import screenshot

def get_threshold(img):
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)[1]
    opening = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((2, 2), dtype="uint8"), iterations=1)
    #canny = cv2.Canny(thresh, cv2.MORPH_CLOSE, )
    return opening

def eucl_dist(p1, p2):
    return math.sqrt(2 ** (p2[0] - p1[0]) + 2 ** (p2[1] - p1[1]))

def mid_bbox(bbox):
    return (bbox[0] + (bbox[2]/2), bbox[1] + (bbox[3]/2))

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

def get_characters():
    SW, SH = win_util.get_screen_size()
    sc = screenshot(int(SW * 0.47), int(SH * 0.54), 80, 38)
    img = cv2.cvtColor(np.array(sc), cv2.COLOR_RGB2BGR)
    thresh = get_threshold(img)
    _, contours, _ = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
    contours.sort(key=lambda c: mid_bbox(cv2.boundingRect(c)))
    mask = np.zeros(thresh.shape[:2])
    masks = []
    curr_contours = []
    sub_mask = mask.copy()
    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        mid_x = x + (w/2)
        next_x = -1
        if i < len(contours) - 1:
            x2, y2, w2, h2 = cv2.boundingRect(contours[i+1])
            next_x = x2 + (w2/2)
        curr_contours.append(c)
        if next_x == -1 or abs(mid_x - next_x) > 6:
            cv2.drawContours(sub_mask, curr_contours, -1, (255, 255, 255), -1)
            x1, y1, x2, y2 = largest_bounding_rect(curr_contours)
            curr_contours = []
            cropped = sub_mask[y1:y2, x1:x2]
            masks.append(cropped)
            sub_mask = mask.copy()
    filtered_masks = []
    for mask in masks:
        if mask.shape[1] > 10:
            filtered_masks.append(mask)
    return filtered_masks

def format_time(prediction):
    if prediction[0] == "b":
        prediction[0] = 8
    if prediction[1] == "z" or prediction[1] == "b" or prediction[1] == "d":
        prediction[1] = 0
    if prediction[2] == "z" or prediction[2] == "b" or prediction[2] == "d":
        prediction[2] = 0
    return (int(prediction[0]), int(str(prediction[1]) + str(prediction[2])))

def get_bomb_duration(model):
    masks = get_characters()
    if len(masks) != 3:
        log(f"WARNING: Bomb duration string length != 3 (len={len(masks)}).", config.LOG_WARNING)
    masks = np.array([dataset_util.reshape(mask, config.CHAR_INPUT_DIM[1:]) for mask in masks])
    prediction = classifier.predict(model, masks)
    best_pred = classifier_util.get_best_prediction(prediction)
    return format_time([classifier.LABELS[p] for p in best_pred])
