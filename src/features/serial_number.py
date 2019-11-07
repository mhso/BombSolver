from glob import glob
import math
import numpy as np
import cv2
import config
import model.serial_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
from debug import log

def serial_bounding_box(img):
    a = np.where(img != 0)
    bbox = np.min(a[0]), np.max(a[0]), np.min(a[1]), np.max(a[1])
    return bbox

def get_threshold(img):
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    thresh1 = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)[1]
    y_min, y_max, x_min, x_max = serial_bounding_box(thresh1)
    gray = gray[y_min:y_max, x_min:x_max]
    inverted = 255 - gray
    thresh2 = cv2.threshold(inverted, 50, 255, cv2.THRESH_BINARY_INV)[1]
    return img[y_min:y_max, x_min:x_max], thresh2

def scan_for_red(img, x):
    h, w, _ = img.shape
    if x < 0 or x > w:
        return False
    red_low = config.SERIAL_MIN_RED
    red_high = config.SERIAL_MAX_RED
    step_y = h // 12
    start_y = (h // 10)
    blue = img[:, :, 0]
    green = img[:, :, 1]
    red = img[:, :, 2]
    for i in range(1, 11):
        y = start_y + i * step_y
        pixel = (y, x)
        if (red[pixel] >= red_low[0] and green[pixel] >= red_low[1]
                and blue[pixel] >= red_low[2] and red[pixel] <= red_high[0]
                and green[pixel] <= red_high[1] and blue[pixel] <= red_high[2]):
            return True
    return False

def determine_alignment(img, bbox):
    min_y, max_y, min_x, max_x = bbox
    offset_x = img.shape[1] // 12
    if scan_for_red(img, min_x - offset_x):
        log("Serial number is left aligned.", config.LOG_DEBUG)
        return 1 # Left alignment.
    elif scan_for_red(img, max_x + offset_x):
        log("Serial number is right aligned.", config.LOG_DEBUG)
        return -1
    return 0

def get_segmented_image(img):
    cropped_img, thresh = get_threshold(img)

    bbox = serial_bounding_box(thresh)
    alignment = determine_alignment(cropped_img, bbox)

    min_y, max_y, min_x, max_x = bbox
    copy = cv2.cvtColor(cropped_img[min_y:max_y, min_x:max_x].copy(), cv2.COLOR_BGR2GRAY)

    thresh = cv2.threshold(copy, 50, 255, cv2.THRESH_BINARY_INV)[1]

    _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

    return copy, contours, alignment

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
    for i, c in enumerate(filtered_contours):
        x, y, w, h = cv2.boundingRect(c)
        mid_y = y + (h/2)
        next_y = -1
        if i < len(filtered_contours) - 1:
            x2, y2, w2, h2 = cv2.boundingRect(filtered_contours[i+1])
            next_y = y2 + (h2/2)
        curr_contours.append(c)
        if next_y == -1 or abs(mid_y - next_y) > 20:
            cv2.drawContours(sub_mask, curr_contours, -1, (255, 255, 255), -1)
            x1, y1, x2, y2 = largest_bounding_rect(curr_contours)
            curr_contours = []
            cropped = sub_mask[y1:y2, x1:x2]
            masks.append(cropped)
            sub_mask = mask.copy()
    return masks

def rotate_masks(masks, alignment):
    rotated = []
    for mask in masks:
        if alignment == -1:
            rotated.append(cv2.rotate(mask, cv2.ROTATE_90_COUNTERCLOCKWISE))
        else:
            rotated.append(cv2.rotate(mask, cv2.ROTATE_90_CLOCKWISE))
    return rotated

def get_characters(img):
    image, contours, alignment = get_segmented_image(img)
    masks = get_masked_images(image, contours)
    masks = rotate_masks(masks, alignment)
    return masks, alignment

def reshape_masks(masks):
    resized_masks = []
    for mask in masks:
        reshaped = mask.reshape(mask.shape + (1,))
        padded = dataset_util.pad_image(reshaped)
        resized = dataset_util.resize_img(padded, config.SERIAL_INPUT_DIM[1:])
        repeated = np.repeat(resized.reshape(((1,) + config.SERIAL_INPUT_DIM[1:])), 3, axis=0)
        resized_masks.append(repeated)
    return np.array(resized_masks)

def create_serial_string(predictions, alignment):
    result = ""
    for pred in predictions:
        if classifier.LABELS[pred] == "b":
            pred = 0
        if alignment == 1:
            result += classifier.LABELS[pred]
        else:
            result = classifier.LABELS[pred] + result
    return result.upper()

def get_serial_number(img, model):
    masks, alignment = get_characters(img)
    if not alignment:
        print("ERROR: Could not determine alignment of serial number")
        return None
    masks = reshape_masks(masks)
    prediction = classifier.predict(model, masks)
    best_pred = classifier_util.get_best_prediction(prediction)
    return create_serial_string(best_pred, alignment) # Return actual string.

if __name__ == '__main__':
    FILES = glob("../resources/training_images/serial/test/*.png")
    SERIAL_MODEL = classifier.load_from_file("../resources/trained_models/serial_model")
    classifier.compile_model(SERIAL_MODEL)
    for file in FILES:
        image = cv2.imread(file, cv2.IMREAD_COLOR)
        num = get_serial_number(image, SERIAL_MODEL)
        print(num)
