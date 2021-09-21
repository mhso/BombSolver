import cv2

from solvers import compl_wires_solver

img = cv2.imread("../resources/misc/error_imgs/62.png", cv2.IMREAD_COLOR)
test_features = {
    "batteries": 4, "parallel_port": True, "serial_number": "LV3CZ2",
    "last_serial_odd": False, "contains_wovel": False
}
print(compl_wires_solver.solve(img, test_features))
