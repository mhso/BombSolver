from threading import Thread
import numpy as np
import cv2
import config
import model.character_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import features.util as features_util
import util.windows_util as win_util
from debug import log
from model.grab_img import screenshot

def get_threshold(img):
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)[1]

    opening = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((2, 2), dtype="uint8"), iterations=1)
    return opening

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

def get_masked_images(image):
    contours = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)[0]
    contours.sort(key=lambda c: features_util.mid_bbox(cv2.boundingRect(c)))
    mask = np.zeros(image.shape[:2], dtype="uint8")
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

def get_duration_characters():
    SW, SH = win_util.get_screen_size()
    sc = screenshot(int(SW * 0.47), int(SH * 0.54), 80, 38)
    img = cv2.cvtColor(np.array(sc), cv2.COLOR_RGB2BGR)
    thresh = get_threshold(img)
    return get_masked_images(thresh)

def get_module_characters():
    SW, SH = win_util.get_screen_size()
    sc = screenshot(int(SW * 0.524), int(SH * 0.547), 36, 25)
    img = cv2.cvtColor(np.array(sc), cv2.COLOR_RGB2BGR)
    thresh = get_threshold(img)
    masks = get_masked_images(thresh)
    if len(masks) == 1 and masks[0].shape[1] > 20:
        mask1 = masks[0][:, :masks[0].shape[1]//2]
        mask2 = masks[0][:, masks[0].shape[1]//2:]
        masks = [mask1, mask2]
    return masks

def fix_number(val):
    result = ""
    for c in val:
        if c == "i":
            result += "1"
        elif c == "b":
            result += "8"
        else:
            result += c
    return int(result)

def format_time(prediction):
    result = [5, 0, 0]
    if prediction[0] == "b":
        result[0] = 8
    if prediction[1] == "3":
        result[1] = 3
    if prediction[2] == "5":
        result[2] = 5
    return (int(result[0]), int(str(result[1]) + str(result[2])))

def get_details_async(model, holder):
    duration_masks = get_duration_characters()
    if len(duration_masks) != 3:
        log(f"WARNING: Bomb duration string length != 3 (len={len(get_duration_characters)}).",
            config.LOG_WARNING)
    module_masks = get_module_characters()
    masks = duration_masks + module_masks
    masks = np.array([dataset_util.reshape(mask, config.CHAR_INPUT_DIM[1:]) for mask in masks])
    prediction = classifier.predict(model, masks)
    best_pred = classifier_util.get_best_prediction(prediction)
    labels = [classifier.LABELS[p] for p in best_pred]
    holder.append(format_time(labels[:3]))
    holder.append(fix_number(labels[3:5]))

def get_bomb_details(model, storing_list):
    Thread(target=get_details_async, args=(model, storing_list)).start()
