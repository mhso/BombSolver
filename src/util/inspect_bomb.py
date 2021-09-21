from time import sleep
import util.windows_util as win_util
from model.grab_img import screenshot

SW, SH = win_util.get_screen_size()
LEVEL_COORDS = {
    "first_bomb" : int(SH * 0.35),
    "old-new" : int(SH * 0.47),
    "double_your_money" : int(SH * 0.53),
    "step_up" : int(SH * 0.58),
    "pick_up_pace_1" : int(SH * 0.62),
    "hidden_message" : int(SH * 0.26),
    "somethings_different" : int(SH * 0.30),
    "one_giant_leap" : int(SH * 0.35),
    "fair_game" : int(SH * 0.39),
    "pick_up_pace_2" : int(SH * 0.44),
    "no_room_for_error" : int(SH * 0.48),
    "eight_modules" : int(SH * 0.53),
    "small_wrinkle" : int(SH * 0.64),
    "multi-tasker" : int(SH * 0.35),
    "the_knob" : int(SH * 0.305),
    "hardcore" : int(SH * 0.55)
}

def next_level_page():
    sw, sh = win_util.get_screen_size()
    win_util.click(int(sw * 0.65), int(sh * 0.70))

def select_level(level):
    win_util.click(int(SW * 0.55), LEVEL_COORDS[level])

def continue_button():
    sw, sh = win_util.get_screen_size()
    x = sw // 2
    y = int(sh * 0.65)
    win_util.click(x, y)
    sleep(1)
    win_util.click(x, y)

def select_bombs_menu():
    sw, sh = win_util.get_screen_size()
    x = sw // 2
    y = int(sh * 0.56)
    win_util.click(x, y)

def inspect_side(mx, my, sx, sy, sw, sh):
    win_util.mouse_move(mx, my)
    sleep(0.5)
    SC = screenshot(sx, sy, sw, sh)
    sleep(0.2)
    return SC

def flip_bomb(SW, SH):
    mid_x = SW // 2
    mid_y = SH // 2
    win_util.click(SW - 100, 100, btn="right")
    sleep(0.5)
    win_util.click(mid_x, mid_y + (mid_y // 8))
    sleep(0.2)
    win_util.mouse_down(mid_x, mid_y, btn="right")
    sleep(0.5)
    win_util.mouse_move(SW - int(SW / 4.4), mid_y + (mid_y // 9))
    sleep(0.5)

def inspect_bomb(inspect_both_sides=True):
    sw, sh = win_util.get_screen_size()
    mid_x = sw // 2
    mid_y = sh // 2
    win_util.click(mid_x, mid_y + (mid_y // 8))
    sleep(0.5)
    # Inspect front of bomb.
    front_img = screenshot(460, 220, 1000, 640)
    sleep(0.2)
    # Rotate bomb.
    win_util.mouse_down(mid_x, mid_y, btn="right")
    sleep(0.2)
    # Inspect right side.
    right_img = inspect_side(sw - int(sw / 2.74), mid_y + int(mid_y / 8), 755, 60, 480, 900)
    # Inspect left side.
    left_img = inspect_side(int(sw / 2.76), mid_y + int(mid_y / 8), 755, 60, 480, 900)
    # Inspect top side.
    top_img = inspect_side(int(sw / 2.75), sh, 720, 0, 480, sh)
    # Inspect bottom side.
    bottom_img = inspect_side(int(sw / 2.75), 0, 720, 0, 480, sh)
    win_util.mouse_up(mid_x, mid_y, btn="right")
    sleep(0.5)
    return_tupl = (front_img, left_img, right_img, top_img, bottom_img)
    if inspect_both_sides:
        # Only capture images of the back of the bomb if there are more than 5 modules.
        flip_bomb(sw, sh)
        back_img = screenshot(460, 220, 1000, 640)
        sleep(0.4)
        win_util.mouse_up(mid_x, mid_y, btn="right")
        return_tupl = (back_img,) + return_tupl
    else:
        win_util.click(200, 200, btn="right")
        sleep(0.4)
        win_util.click(mid_x, mid_y + (mid_y // 8))
        sleep(0.5)
    return return_tupl

def partition_main_sides(images):
    side_partitions = []
    for img in images:
        sides = []
        sides.append(img.crop((105, 60, 361, 316)))
        sides.append(img.crop((384, 62, 640, 318)))
        sides.append(img.crop((658, 62, 914, 318)))
        sides.append(img.crop((86, 344, 342, 600)))
        sides.append(img.crop((373, 344, 629, 600)))
        sides.append(img.crop((648, 344, 904, 600)))
        side_partitions.extend(sides)
    return side_partitions

def partition_short_sides(images):
    side_partitions = []
    for img in images:
        sides = []
        sides.append(img.crop((30, 168, 202, 410)))
        sides.append(img.crop((238, 165, 400, 415)))
        sides.append(img.crop((30, 450, 200, 712)))
        sides.append(img.crop((238, 450, 400, 712)))
        side_partitions.extend(sides)
    return side_partitions

def partition_long_sides(images):
    side_partitions = []
    # Left side.
    side_partitions.append(images[0].crop((98, 144, 242, 356)))
    side_partitions.append(images[0].crop((282, 144, 425, 354)))
    side_partitions.append(images[0].crop((90, 388, 240, 714)))
    side_partitions.append(images[0].crop((282, 388, 430, 714)))
    side_partitions.append(images[0].crop((90, 748, 240, 956)))
    side_partitions.append(images[0].crop((282, 748, 430, 956)))
    # Right side.
    side_partitions.append(images[1].crop((100, 136, 240, 300)))
    side_partitions.append(images[1].crop((270, 134, 420, 300)))
    side_partitions.append(images[1].crop((90, 344, 240, 650)))
    side_partitions.append(images[1].crop((276, 344, 434, 650)))
    side_partitions.append(images[1].crop((80, 694, 240, 926)))
    side_partitions.append(images[1].crop((274, 690, 440, 926)))
    return side_partitions

def partition_sides(images):
    faces = len(images)-4
    main_sides = partition_main_sides(images[:faces])
    short_sides = partition_short_sides(images[faces:faces+2])
    long_sides = partition_long_sides(images[faces+2:])
    return (main_sides, short_sides, long_sides)
