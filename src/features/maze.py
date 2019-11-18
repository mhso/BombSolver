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

def get_contour_positions(img):
    _, contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = features_util.unite_contours(contours, 3)
    bboxes = [features_util.largest_bounding_rect(c) for c in contours]
    assert len(bboxes) == 4

    bboxes.sort(key=lambda x: x[2]) # Sort by width of contour bbox.
    bboxes = [features_util.mid_bbox(bbox) for bbox in bboxes]
    return (bboxes[0], bboxes[1], bboxes[2], bboxes[3])

def get_maze_details(img):
    cropped = crop_img(img)
    thresh = get_threshold(cropped)
    # cv2.namedWindow("Test")
    # cv2.imshow("Test", thresh)
    # key = cv2.waitKey(0)
    # if key == ord('q'):
    #     exit(0)
    return get_contour_positions(thresh)
