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

def get_threshold(img, color):
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    if color > 1:
        gray = 255 - gray
    thresh_values = [60, 90, 90, 90]
    thresh = cv2.threshold(gray, thresh_values[color], 255, cv2.THRESH_BINARY_INV)[1]
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

def get_segmented_image(image, color):
    cy_min, cx_min, cy_max, cx_max = 152, 48, 190, 200
    image = image[cy_min:cy_max, cx_min:cx_max, :]
    thresh = get_threshold(image, color)
    _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return thresh, contours

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

    filtered_contours.sort(key=lambda c: cv2.boundingRect(c)[0])

    masks = []
    curr_contours = []
    sub_mask = mask.copy()
    for i, c in enumerate(filtered_contours):
        x, y, w, h = cv2.boundingRect(c)
        mid_x = x + (w/2)
        next_x = -1
        if i < len(filtered_contours) - 1:
            x2, y2, w2, h2 = cv2.boundingRect(filtered_contours[i+1])
            next_x = x2 + (w2/2)
        curr_contours.append(c)
        if next_x == -1 or abs(mid_x - next_x) > 10:
            cv2.drawContours(sub_mask, curr_contours, -1, (255, 255, 255), -1)
            x1, y1, x2, y2 = largest_bounding_rect(curr_contours)
            curr_contours = []
            cropped = sub_mask[y1:y2, x1:x2]
            masks.append(cropped)
            sub_mask = mask.copy()

    return masks

def color_in_range(img, pixel, low, high):
    blue = img[:, :, 0]
    green = img[:, :, 1]
    red = img[:, :, 2]
    return (red[pixel] >= low[0] and green[pixel] >= low[1]
            and blue[pixel] >= low[2] and red[pixel] <= high[0]
            and green[pixel] <= high[1] and blue[pixel] <= high[2])

def get_button_color(image):
    color_ranges = config.BUTTON_COLOR_RANGE
    pixel = 210, 120
    for i, (low, high) in enumerate(color_ranges):
        if color_in_range(image, pixel, low, high):
            return i
    return -1

def get_characters(image):
    color = get_button_color(image)
    color_names = ["White", "Yellow", "Blue", "Red"]
    if color == -1:
        log("WARNING: Button color could not be determined.", config.LOG_WARNING)
    else:
        log(f"Button color: {color_names[color]}", config.LOG_DEBUG)
    thresh, contours = get_segmented_image(image, color)
    masks = get_masked_images(image, contours)
    return masks, color

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

def get_button_features(image, model):
    masks, color = get_characters(image)
    if len(masks) == 4:
        return "Hold", color
    elif len(masks) == 8:
        return "Detonate", color
    else:
        masks = reshape_masks([masks[0]])
        prediction = classifier.predict(model, masks[0])
        best_pred = classifier_util.get_best_prediction(prediction)
        if best_pred[0] == "a":
            return "Abort", color
        return "Press", color

def get_strip_color(img, pixel):
    colors = config.BUTTON_COLOR_RANGE
    for i, (low, high) in enumerate(colors):
        if color_in_range(img, pixel, low, high):
            return i
    return -1

def sleep_until_start():
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

if __name__ == '__main__':
    #sleep_until_start()
    cv2.namedWindow("Test")
    #FILES = glob("../resources/training_images/button/test/*.png")
    #for file in FILES:
    file = "../resources/training_images/button/test/0.png"
    image = cv2.imread(file)
    masks, _ = get_characters(image)

    for mask in masks:
        cv2.imshow("Test", mask)
        key = cv2.waitKey(0)
        if key == ord('q'):
            exit(0)
