import cv2
import features.needy_util

img = cv2.imread("../resources/misc/error_imgs/16.png", cv2.IMREAD_COLOR)
#img = cv2.imread("../resources/training_images/needy_discharge/000.png", cv2.IMREAD_COLOR)
print(features.needy_util.is_active(img))
