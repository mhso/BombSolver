from time import sleep
import windows_util as win_util

def sleep_until_start():
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

def screenshot_module():
    SW, SH = win_util.get_screen_size()
    x = int(SW * 0.43)
    y = int(SH*0.36)
    return x, y

sleep_until_start()

x, y = screenshot_module()

win_util.click(x+125, y+175)
