import cv2
import solvers.knob_solver as solver

img = cv2.imread("../resources/misc/Knob2.png", cv2.IMREAD_COLOR)
print(solver.solve(img))
