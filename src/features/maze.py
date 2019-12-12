import cv2
import features.util as features_util

def get_threshold(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted = 255 - gray
    thresh = cv2.threshold(inverted, 190, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def crop_img(img):
    min_y, min_x, max_y, max_x = 72, 60, 230, 218
    return img[min_y:max_y, min_x:max_x]

def get_start_and_end(img):
    red_l = (200, 0, 0)
    red_h = (255, 30, 40)
    white_l = (190, 190, 190)
    white_h = (255, 255, 255)
    rgb = features_util.split_channels(img)
    start_x = 17
    start_y = 16
    gap = 25
    start = None
    end = None
    for j in range(0, 6):
        y = start_y + j * gap
        for i in range(0, 6):
            x = start_x + i * gap
            pixel = (y, x)
            r, g, b = rgb
            if features_util.color_in_range(pixel, rgb, white_l, white_h):
                start = (i, j)
            elif features_util.color_in_range(pixel, rgb, red_l, red_h):
                end = (i, j)
    assert start is not None
    assert end is not None
    return start, end

def get_contour_positions(img):
    contours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
    contours = features_util.combine_contours(contours, 3)
    bboxes = [features_util.largest_bounding_rect(c) for c in contours]

    bboxes.sort(key=lambda x: x[2], reverse=True) # Sort by width of contour bbox.
    bboxes = [features_util.mid_bbox(bbox) for bbox in bboxes]
    return (bboxes[0], bboxes[1])

def get_maze_details(img):
    cropped = crop_img(img)
    start, end = get_start_and_end(cropped)
    thresh = get_threshold(cropped)
    maze_features = get_contour_positions(thresh)
    return start, end, maze_features
