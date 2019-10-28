from time import sleep
from debug import log
from model.grab_img import screenshot
import windows_util as win_util

def sleep_until_start():
    while True:
        if win_util.s_pressed():
            break
        sleep(0.1)

def start_level(sw, sh):
    win_util.click(int(sw - sw/2.6), int(sh - sh/3.3))

def wait_for_light():
    sleep(16)

def inspect_side(mx, my, sx, sy, sw, sh):
    win_util.mouse_move(mx, my)
    sleep(0.5)
    return screenshot(sx, sy, sw, sh)

def inspect_bomb(sw, sh):
    mid_x = sw // 2
    mid_y = sh // 2
    win_util.click(mid_x, mid_y + (mid_y // 8))
    sleep(0.5)
    # Inspect front of bomb.
    front_img = screenshot(mid_x - mid_x // 2, sh // 5, int(sw / 1.9), int(sh / 1.65))
    front_img.save("../front.png")
    sleep(0.2)
    # Rotate bomb.
    win_util.mouse_down(mid_x, mid_y, btn="right")
    sleep(0.2)
    # Inspect right side.
    right_img = inspect_side(sw - int(sw / 2.75), mid_y + int(mid_y / 8),
                             mid_x - int(mid_x / 4.7), sh // 20, int(sw // 4), sh - sh // 6)
    right_img.save("../left.png")
    # Inspect left side.
    left_img = inspect_side(int(sw / 2.8), mid_y + int(mid_y / 8),
                            mid_x - int(mid_x / 3.8), sh // 20, int(sw // 4), sh - sh // 6)
    left_img.save("../right.png")
    # Inspect top side.
    top_img = inspect_side(int(sw / 2.75), sh, mid_x - int(mid_x / 4), 0, int(sw // 4), sh)
    top_img.save("../top.png")
    # Inspect bottom side.
    bottom_img = inspect_side(int(sw / 2.75), 0, mid_x - int(mid_x / 4), 0, int(sw // 4), sh)
    bottom_img.save("../bot.png")
    # Inspect back of bomb.
    win_util.mouse_up(mid_x, mid_y, btn="right")
    sleep(0.5)
    win_util.click(sw - 100, 100, btn="right")
    sleep(0.5)
    win_util.click(mid_x, mid_y + (mid_y // 8))
    sleep(0.2)
    win_util.mouse_down(mid_x, mid_y, btn="right")
    sleep(0.5)
    back_img = inspect_side(sw - int(sw / 4.45), mid_y + (mid_y // 9),
                            mid_x - mid_x // 2, sh // 5, int(sw / 1.9), int(sh / 1.65))
    back_img.save("../back.png")
    sleep(0.2)
    win_util.mouse_up(mid_x, mid_y, btn="right")
    return (front_img, back_img, left_img, right_img, top_img, bottom_img)

def partition_main_sides(images):
    side_partitions = []
    for img in images:
        sides = []
        side_partitions.append(sides)
    return side_partitions

def partition_short_sides(images):
    side_partitions = []
    for img in images:
        sides = []
        side_partitions.append(sides)
    return side_partitions

def partition_long_sides(images):
    side_partitions = []
    for img in images:
        sides = []
        side_partitions.append(sides)
    return side_partitions

def partition_sides(images):
    main_sides = partition_short_sides(images[0:2])
    short_sides = partition_short_sides(images[2:4])
    long_sides = partition_long_sides(images[4:6])
    return (main_sides, short_sides, long_sides)

log("Waiting for level selection...")
log("Press S when a level has been selected.")
sleep_until_start()
log("Waiting for level to start...")
SCREEN_W, SCREEN_H = win_util.get_screen_size()
#start_level(screen_w, screen_h)
#wait_for_light()
log("Inspecting bomb...")
IMAGES = inspect_bomb(SCREEN_W, SCREEN_H)
SIDE_PARTITIONS = partition_sides(IMAGES)
