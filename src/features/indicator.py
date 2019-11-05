from glob import glob
from time import sleep
import math
import numpy as np
import cv2
import config
import model.serial_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import windows_util as win_util
from debug import log

def indicator_bbox(img):
    a = np.where(img != 0)
    bbox = np.min(a[0]), np.max(a[0]), np.min(a[1]), np.max(a[1])
    return bbox

def get_threshold(img):
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    inverted = 255 - gray
    thresh = cv2.threshold(inverted, 52, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

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

def get_segmented_image(image):
    thresh = get_threshold(image)
    bbox = indicator_bbox(thresh)
    min_y, max_y, min_x, max_x = bbox
    thresh = thresh[min_y:max_y, min_x:max_x]
    _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return thresh, contours, bbox # alignment.

def get_masked_images(image, contours):
    mask = np.zeros(image.shape[:2])

    filtered_contours = []
    for c in contours:
        ps = math.pow(cv2.arcLength(c, True), 2)
        circularity = 0
        if ps > 0:
            circularity = (4*math.pi*cv2.contourArea(c))/ps
        if circularity > 0.08:
            filtered_contours.append(c)

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

    lit = len(masks) > 3

    if lit: # Remove the lit indicator blob.
        log("Indicator is lit", 1)
        index = 0
        max_w = 0
        for i, mask in enumerate(masks):
            if mask.shape[0] > max_w:
                max_w = mask.shape[0]
                index = i
        masks.pop(index)
    else:
        log("Indicator is not lit", 1)

    return masks, lit

def check_color(image, x, y, lit):
    h, w = image.shape[:2]
    if y >= h or y < 0:
        return False
    unlit_min = (25, 25, 25)
    unlit_max = (45, 45, 45)
    lit_min = (230, 230, 230)
    lit_max = (255, 255, 255)
    min_c, max_c = (lit_min, lit_max) if lit else (unlit_min, unlit_max)
    blue = image[:, :, 0]
    green = image[:, :, 1]
    red = image[:, :, 2]
    pixel = (y, x)
    return (red[pixel] >= min_c[0] and green[pixel] >= min_c[1]
            and blue[pixel] >= min_c[2] and red[pixel] <= max_c[0]
            and green[pixel] <= max_c[1] and blue[pixel] <= max_c[2])

def determine_alignment(image, bbox, lit):
    mid_x = (bbox[3] + bbox[2]) // 2
    bot_y = bbox[1]-10 if lit else bbox[1]+60
    top_y = bbox[0]+10 if lit else bbox[0]-60
    if check_color(image, mid_x, bot_y, lit): # Left aligned.
        log("Indicator is left aligned.", 1)
        return 1
    if check_color(image, mid_x, top_y, lit):
        log("Indicator is right aligned.", 1)
        return -1
    log("WARNING: Indicator alignment could not be determined!")
    return 0

def rotate_masks(masks, alignment):
    rotated = []
    for mask in masks:
        if alignment == -1:
            rotated.append(cv2.rotate(mask, cv2.ROTATE_90_COUNTERCLOCKWISE))
        else:
            rotated.append(cv2.rotate(mask, cv2.ROTATE_90_CLOCKWISE))
    return rotated

def get_characters(image):
    h, w = image.shape[:2]
    edge_crop = 20
    image = image[edge_crop:h-edge_crop, edge_crop:w-edge_crop, :]
    thresh, contours, bbox = get_segmented_image(image)
    masks, lit = get_masked_images(image, contours)
    alignment = determine_alignment(image, bbox, lit)
    masks = rotate_masks(masks, alignment)
    return masks, lit

def reshape_masks(masks):
    resized_masks = []
    for mask in masks:
        reshaped = mask.reshape(mask.shape + (1,))
        padded = dataset_util.pad_image(reshaped)
        resized = dataset_util.resize_img(padded, config.SERIAL_INPUT_DIM[1:])
        repeated = np.repeat(resized.reshape(((1,) + config.SERIAL_INPUT_DIM[1:])), 3, axis=0)
        resized_masks.append(repeated)
    return np.array(resized_masks)

def format_time(prediction):
    return prediction[0] + prediction[1] + prediction[2]

def get_indicator_features(image, model):
    masks, lit = get_characters(image)
    masks = reshape_masks(masks)
    prediction = classifier.predict(model, masks)
    best_pred = classifier_util.get_best_prediction(prediction)
    return lit, format_time([classifier.LABELS[p] for p in best_pred])

def sleep_until_start():
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

if __name__ == '__main__':
    #sleep_until_start()
    cv2.namedWindow("Test")
    FILES = glob("../resources/training_images/indicators/test/*.png")
    for file in FILES:
        image = cv2.imread(file)
        PATH = "../resources/training_images/timer/"
        INDEX = len(glob(PATH+"*.png"))
        masks, lit = get_characters(image)
        for mask in masks:
            cv2.imshow("Test", mask)
            key = cv2.waitKey(0)
            if key == ord('q'):
                exit(0)
