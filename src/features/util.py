import math
import numpy as np
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
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def mid_bbox(bbox):
    return (bbox[0] + (bbox[2]/2), bbox[1] + (bbox[3]/2))

def eucl_dist(p_1, p_2):
    return math.sqrt((p_2[0] - p_1[0]) ** 2 + (p_2[1] - p_1[1]) ** 2)

def crop_to_content(img, padding=0):
    a = np.where(img != 0)
    y_min, y_max, x_min, x_max = (np.min(a[0]), np.max(a[0]), np.min(a[1]), np.max(a[1]))
    pad_left = padding if x_min - padding >= 0 and y_min - padding >= 0 else 0
    pad_right = padding+1 if padding != 0 and x_max + padding < img.shape[1] and y_max + padding < img.shape[0] else 0
    return (y_min-pad_left, y_max+pad_right, x_min-pad_left, x_max+pad_right)

def combine_contours(contours, thresh_x, thresh_y=None):
    combined_contours = []
    curr_contours = []
    for i, c in enumerate(contours):
        bbox = cv2.boundingRect(c)
        mid = mid_bbox(bbox)
        next_mid = None
        if i < len(contours) - 1:
            bbox2 = cv2.boundingRect(contours[i+1])
            next_mid = mid_bbox(bbox2)
        curr_contours.append(c)
        if (next_mid is None or (eucl_dist(mid, next_mid) > thresh_x if thresh_y is None else
                abs(next_mid[0] - mid[0]) > thresh_x or abs(next_mid[1] - mid[1]) > thresh_y)):
            combined_contours.append(curr_contours)
            curr_contours = []
    return combined_contours

def contour_within(small, large, x_dist):
    bbox_small = cv2.boundingRect(small)
    bbox_large = cv2.boundingRect(large)
    mid_small = mid_bbox(bbox_small)
    mid_large = mid_bbox(bbox_large)
    if cv2.contourArea(small) > cv2.contourArea(large):
        bbox_large, bbox_small = bbox_small, bbox_large
    return (abs(mid_small[0] - mid_large[0]) < x_dist or
            (bbox_large[0] < bbox_small[0] and bbox_large[1] < bbox_small[1] and
             bbox_large[0] + bbox_large[2] > bbox_small[0] + bbox_small[2] and
             bbox_large[1] + bbox_large[3] > bbox_small[1] + bbox_small[3]))

def combine_contours_better(contours, thresh_x, thresh_y=None):
    combined_contours = []
    curr_contours = [contours[0]]
    print(len(contours))
    for i, c in enumerate(contours[1:], 1):
        prev = curr_contours[-1]
        if not contour_within(c, prev, thresh_x):
            combined_contours.append(curr_contours)
            curr_contours = []
        curr_contours.append(c)
    combined_contours.append([contours[-1]])
    return combined_contours

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
