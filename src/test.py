import cv2

from solvers import needy_discharge_solver


img = cv2.imread("../resources/misc/error_imgs/20.png", cv2.IMREAD_COLOR)

print(needy_discharge_solver.solve(img))
