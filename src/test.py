from time import sleep
from numpy import array
import cv2
from model.grab_img import screenshot
import windows_util as win_util

def sleep_until_start():
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

sleep_until_start()
SW, SH = win_util.get_screen_size()
SC = screenshot(int(SW * 0.43), int(SH*0.36), 300, 300)

cv2.namedWindow("Screenshot")

cv2.imshow("Screenshot", cv2.cvtColor(array(SC).astype("uint8"), cv2.COLOR_RGB2BGR))
cv2.waitKey(0)
