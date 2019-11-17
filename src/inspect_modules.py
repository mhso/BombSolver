from time import sleep
import main
import windows_util as win_util

def inspect(labels, labels_to_inspect):
    SW, SH = win_util.get_screen_size()

    filtered_labels = []
    images = []
    for module in range(12):
        mod_index = module if module < 6 else module - 6
        if labels[module] in labels_to_inspect:
            main.select_module(mod_index)
            sleep(1)
            SC, _, _ = main.screenshot_module()
            images.append(SC)
            filtered_labels.append(labels[module])
            main.deselect_module(mod_index)
            sleep(0.5)
        if module == 5: # We have gone through 6 modules, flip the bomb over and proceeed.
            SW, SH = win_util.get_screen_size()
            main.flip_bomb(SW, SH)
            sleep(0.75)
            win_util.mouse_up(SW // 2, SH // 2, btn="right")
            sleep(0.5)
    return images, filtered_labels
