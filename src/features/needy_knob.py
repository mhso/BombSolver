import cv2
import features.util as features_util

def get_threshold(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def segment_image(img):
    contours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    contours.sort(key=lambda c: features_util.mid_bbox(cv2.boundingRect(c))[0])
    contours = features_util.combine_contours(contours, 3, 20)

    for c in contours:
        if 15 < cv2.contourArea(c[0]) < 35:
            return True
    return False

def get_directions(img):
    bboxes = [ # In clock-wise order.
        (110, 138, 122, 162),
        (152, 194, 176, 206),
        (208, 138, 220, 162),
        (152, 96, 176, 108),
    ]
    dirs = []
    for min_y, min_x, max_y, max_x in bboxes:
        thresh = get_threshold(img[min_y:max_y, min_x:max_x])
        dirs.append(segment_image(thresh))

    return dirs

def get_led_states(img):
    coords = [
        (195, 77), (219, 94), (236, 120),
        (236, 179), (219, 205), (195, 222),
        (204, 57), (236, 78), (258, 112),
        (258, 187), (236, 220), (204, 242)
    ]
    lit_low = (130, 190, 25)
    lit_high = (220, 255, 100)
    rgb = features_util.split_channels(img)
    states = []
    for y, x in coords:
        states.append(features_util.color_in_range((y, x), rgb, lit_low, lit_high))
    return states

def get_dial_orientation(img):
    dial_y_min, dial_x_min, dial_y_max, dial_x_max = 130, 118, 194, 182
    rgb = features_util.split_channels(img)
    mid_y = (dial_y_min + dial_y_max) / 2
    mid_x = (dial_x_min + dial_x_max) / 2
    offset = 16
    coords = [
        (mid_y - offset, mid_x), (mid_y, mid_x + offset),
        (mid_y + offset, mid_x), (mid_y, mid_x - offset)
    ]
    red_min = (190, 30, 0)
    red_max = (255, 85, 40)
    for i, (y, x) in enumerate(coords):
        if features_util.color_in_range((int(y), int(x)), rgb, red_min, red_max):
            return i
    return -1

def test_with(img):
    threshes = get_directions(img)
    for thresh in threshes:
        cv2.imshow("Test", thresh)
        key = cv2.waitKey(0)
        if key == ord('q'):
            return
        cv2.destroyWindow("Test")
