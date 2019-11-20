import cv2
import numpy as np
import model.dataset_util as util

img_c = cv2.imread("../resources/labeled_images/characters/8/001.png", cv2.IMREAD_COLOR)
img_g = cv2.imread("../resources/labeled_images/characters/8/001.png", cv2.IMREAD_GRAYSCALE)

img_c = util.reshape(img_c, (32, 32))
img_g = util.reshape(img_g, (32, 32))

print(img_c.shape)
print(img_g.shape)

print(img_c[0, 10:12, 10:12])
print(img_g[0, 10:12, 10:12])
