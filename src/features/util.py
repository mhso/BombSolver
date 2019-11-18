from numpy import array
import math
import cv2

def color_in_range(pixel, rgb, lo_rgb, hi_rgb):
    red, green, blue = rgb
    return (red[pixel] >= lo_rgb[0] and green[pixel] >= lo_rgb[1]
            and blue[pixel] >= lo_rgb[2] and red[pixel] <= hi_rgb[0]
            and green[pixel] <= hi_rgb[1] and blue[pixel] <= hi_rgb[2])

def split_channels(img_bgr):
    blue = img_bgr[:, :, 0]
    green = img_bgr[:, :, 1]
    red = img_bgr[:, :, 2]
    return (red, green, blue)

def convert_to_cv2(img):
    return cv2.cvtColor(array(img), cv2.COLOR_RGB2BGR)

def mid_bbox(bbox):
    return (bbox[0] + (bbox[2]/2), bbox[1] + (bbox[3]/2))

def eucl_dist(p_1, p_2):
    return math.sqrt((p_2[0] - p_1[0]) ** 2 + (p_2[1] - p_1[1]) ** 2)

def unite_contours(contours, threshold):
    united_contours = []
    curr_contours = []
    for i, c in enumerate(contours):
        bbox = cv2.boundingRect(c)
        mid = mid_bbox(bbox)
        next_mid = None
        if i < len(contours) - 1:
            bbox2 = cv2.boundingRect(contours[i+1])
            next_mid = mid_bbox(bbox2)
        curr_contours.append(c)
        if next_mid is None or eucl_dist(mid, next_mid) > threshold:
            united_contours.append(curr_contours)
            curr_contours = []
    return united_contours

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
    return (min_x, min_y, max_x-min_x, max_y-min_y)
