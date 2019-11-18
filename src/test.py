from glob import glob
import solvers.maze_solver as solver
import cv2

FILES = glob("../resources/misc/Maze3.png")
for file in FILES:
    img = cv2.imread(file, cv2.IMREAD_COLOR)
    path = solver.solve(img)
