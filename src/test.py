import cv2
import solvers.wire_seq_solver as solver

img = cv2.imread("../resources/misc/Wire_Seq_5.png", cv2.IMREAD_COLOR)
solver.solve(img, [0, 0, 0])
