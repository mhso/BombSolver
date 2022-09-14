# import cv2

# from solvers import needy_discharge_solver

# img = cv2.imread("../resources/misc/error_imgs/20.png", cv2.IMREAD_COLOR)

# print(needy_discharge_solver.solve(img))

from time import sleep

def test_stuff():
    for x in range(3):
        for y in range(3):
            if x == 1 and y == 2:
                break
        yield x
    yield (1, 2)

for result in test_stuff():
    print(result)
