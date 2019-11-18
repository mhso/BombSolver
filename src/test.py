from glob import glob
import solvers.maze_solver as solver
import cv2

img = cv2.imread("../resources/misc/Maze.png", cv2.IMREAD_COLOR)
positions = solver.solve(img)
