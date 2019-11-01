from glob import glob
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
    if "rounds=" in argv:
        for s in argv[1:]:
            if s.find("rounds=") != -1:
                inspections = int(s.split("=")[1])

    while inspections and not win_util.q_pressed():
        if "skip" not in argv:
            main.start_level()
            main.wait_for_light()
        log("Inspecting bomb...")
        IMAGES = main.inspect_bomb()
        SIDE_PARTITIONS = main.partition_sides(IMAGES)

        callback(SIDE_PARTITIONS)

        NUM_IMAGES = len(glob("../resources/training_images/*.png"))
        INDEX = NUM_IMAGES
        for side in SIDE_PARTITIONS:
            for img in side:
                img.save(f"../resources/training_images/{INDEX:03d}.png")
                INDEX += 1

        log(f"Captured {INDEX-NUM_IMAGES} images. Total images: {INDEX}")

        inspections -= 1
        restart_level()
