import solvers.compl_wires_solver as solver
import cv2

img = cv2.imread("../resources/misc/Compl_Wires.png", cv2.IMREAD_COLOR)
solver.solve(img, {})
