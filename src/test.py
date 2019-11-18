from glob import glob
import solvers.maze_solver as solver
import cv2

img = cv2.imread("../resources/misc/Maze2.png", cv2.IMREAD_COLOR)
path = solver.solve(img)
print(path)
