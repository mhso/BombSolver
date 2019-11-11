from time import sleep
import windows_util as win_util

def sleep_until_start():
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

sleep_until_start()

SW, SH = win_util.get_screen_size()
win_util.mouse_move(160, SH-190)
