import windows_util as win_util

from main import sleep_until_start

sleep_until_start()

SW, SH = win_util.get_screen_size()
win_util.mouse_move(int(SW * 0.55), int(SH * 0.35))
