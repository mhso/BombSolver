from time import sleep
import main
import windows_util as win_util

def inspect():
    SW, SH = win_util.get_screen_size()
    MID_X = SW // 2
    MID_Y = SH // 2
    win_util.click(SW - 100, 100, btn="right")
    sleep(1)
    win_util.click(MID_X, MID_Y + (MID_X // 8))
    sleep(0.5)

    images = []
    for module in range(12):
        main.select_module(module)
        sleep(0.5)
        SC, _, _ = main.screenshot_module()
        images.append(SC)
        main.deselect_module(module)
        sleep(0.5)
        if module == 5: # We have gone through 6 modules, flip the bomb over and proceeed.
            SW, SH = win_util.get_screen_size()
            main.flip_bomb(SW, SH)
            sleep(0.75)
            win_util.mouse_up(SW // 2, SH // 2, btn="right")
            sleep(0.5)
    return images
