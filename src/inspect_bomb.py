from time import sleep
from sys import argv
import main
import windows_util as win_util
from debug import log

def restart_level():
    SW, SH = win_util.get_screen_size()
    win_util.click(int(SW * 0.9), int(SH * 0.8), btn="right")
    sleep(1)
    win_util.click(int(SW * 0.73), int(SH * 0.65))
    sleep(1)
    win_util.click(int(SW * 0.73), int(SH * 0.45))
    sleep(2)
    win_util.click(int(SW * 0.52), int(SH * 0.53))
    sleep(0.8)
    win_util.click(int(SW * 0.55), int(SH * 0.53))
    sleep(0.5)

def inspect_and_reset(callback):
    log("Waiting for user to press S")
    main.sleep_until_start()

    inspections = -1
    if len(argv) > 1:
        inspections = int(argv[1])

    inspect_str = "infinitely many" if inspections == -1 else str(inspections)
    log(f"Running {inspect_str} times.")

    while inspections and not win_util.q_pressed():
        if "skip" not in argv:
            main.start_level()
            main.wait_for_light()
        log("Inspecting bomb...")
        IMAGES = main.inspect_bomb()
        SIDE_PARTITIONS = main.partition_sides(IMAGES)

        callback(SIDE_PARTITIONS)

        inspections -= 1
        restart_level()
