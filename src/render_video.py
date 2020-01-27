from glob import glob
from sys import argv
from pickle import load
import cv2
import util.windows_util as win_util
from solvers.maze_solver import MAZES, DIRECTIONS

def format_time(s_time, sig_digs=1):
    mins = int(s_time // 60)
    secs = s_time % 60
    secs_str = f"{secs:0.{sig_digs}f}"
    if secs < 10:
        secs_str = "0" + secs_str
    return f"{mins:02d}:{secs_str}"

def format_level(level):
    upper_y = 15
    mid_y = 25
    lower_y = 30
    if len(level) > 9:
        split = level.split("_")
        if len(split) == 1:
            return [(level[:10], upper_y), (level[10:], lower_y)]
        return [("_".join(split[:-1]), upper_y), (split[-1], lower_y)]
    return [(level, mid_y)]

def draw_text(img, text, pt_1, scale, color, thickness=2, font=cv2.FONT_HERSHEY_PLAIN):
    cv2.putText(img, text, pt_1, font, scale, color, thickness)

def draw_rect(img, pt_1, pt_2, color, thickness):
    cv2.rectangle(img, pt_1, pt_2, color, thickness)

def draw_line(img, pt_1, pt_2, color, thickness):
    cv2.line(img, pt_1, pt_2, color, thickness)

def draw_speedrun_splits(img, splits):
    sw, _ = win_util.get_screen_size()
    bar_height = 100
    cv2.rectangle(img, (0, 0), (sw, bar_height), (0, 0, 0), -1)
    start_x = 5
    step_x = 125
    for i, (level, split) in enumerate(splits):
        segment = split if i < 1 else split - splits[i-1][1]
        total_time_str = format_time(split)
        segment_time_str = format_time(segment)
        level_strs = format_level(level)
        x = start_x + (step_x * i)
        cv2.rectangle(img, (step_x*i, 0), (step_x*(i+1), bar_height), (80, 80, 80), -1)
        cv2.rectangle(img, (step_x*i, 0), (step_x*(i+1), bar_height), (0, 0, 0), 1)
        for lvl_s, lvl_y in level_strs:
            cv2.putText(img, lvl_s, (x, lvl_y),
                        cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 1)
        cv2.putText(img, total_time_str, (x, 60),
                    cv2.FONT_HERSHEY_PLAIN, 1.6, (60, 230, 30), 2)
        cv2.putText(img, "("+segment_time_str+")", (x, 90),
                    cv2.FONT_HERSHEY_PLAIN, 1.6, (40, 160, 40), 2)

def draw_speedrun_time(img, s_time):
    sw, _ = win_util.get_screen_size()
    time_str = format_time(s_time, 0)
    draw_text(img, time_str, (sw-180, 50), 2.8, (255, 255, 255), 2)

def draw_modules(img, positions, names):
    offset = 150
    for ((x, y), name) in zip(positions, names):
        draw_rect(img, (x-offset, y-offset),
                  (x+offset, y+offset+10), (0, 0, 255), 5)
        if name is not None:
            text_x = x-(len(name) * 8)
            draw_text(img, name, (text_x, y-offset+30), 1.8, (120, 30, 30), 2)

def draw_module_selected(img, module):
    size = 300
    x, y, index = module
    selected_module = (x, y)
    for i in range(6):
        offset_x = (i % 3) - (index % 3)
        offset_y = 0
        offset_x = offset_x * size
        if (i > 2) ^ (index > 2):
            offset_y = 300 if i > index else -300
        if index != i:
            draw_rect(img, (x+offset_x, y+offset_y),
                        (x+offset_x+size, y+offset_y+size), (0, 0, 255), 5)
    draw_rect(img, (x, y), (x+size, y+size), (35, 255, 35), 5)
    return selected_module

def log_info(img, info):
    sw, sh = win_util.get_screen_size()
    width = 350
    x = sw - width
    y_step = 20
    start_y = 100
    draw_rect(img, (x-10, start_y), (sw, sh), (0, 0, 0), -1)
    max_lines = int(sh // 23) # 47 for 1080.
    for i, s in enumerate(info[-max_lines:]):
        draw_text(img, s, (x, start_y+10+(y_step*i)), 1.2, (255, 255, 255), 1)

def draw_maze(img, maze_name, selected_module):
    maze = MAZES[maze_name]
    N = DIRECTIONS.North
    S = DIRECTIONS.South
    W = DIRECTIONS.West
    E = DIRECTIONS.East
    mod_x, mod_y = selected_module
    draw_text(img, maze_name, (mod_x+100, mod_y+30), 1.5, (0, 0, 255), 2)
    mod_x += 60
    mod_y += 72
    step = 25
    start = 3
    color = (255, 130, 0)
    for y, row in enumerate(maze):
        for x, dirs in enumerate(row):
            x_real = mod_x + start + (x * step)
            y_real = mod_y + start + (y * step)
            if N not in dirs:
                draw_line(img, (x_real, y_real),
                            (x_real+step, y_real), color, 2)
            if S not in dirs:
                draw_line(img, (x_real, y_real+step),
                            (x_real+step, y_real+step), color, 2)
            if W not in dirs:
                draw_line(img, (x_real, y_real),
                            (x_real, y_real+step), color, 2)
            if E not in dirs:
                draw_line(img, (x_real+step, y_real),
                            (x_real+step, y_real+step), color, 2)

def draw_module_info(img, module, selected_module, info):
    if selected_module is None:
        return
    if module == 17: # Maze.
        draw_maze(img, info, selected_module)

def get_draw_order(prop):
    if prop == "debug_bg_img":
        return 0
    if prop == "speedrun_splits":
        return 1
    if prop in ("module_positions", "module_selected"):
        return 2
    return 3

def draw_properties(img, keys, properties):
    add_key, add_value = None, None
    for prop in keys:
        value = properties[prop]
        if prop == "speedrun_splits":
            draw_speedrun_splits(img, value)
        elif prop == "speedrun_time":
            draw_speedrun_time(img, value)
        elif prop == "module_positions":
            names = properties.get("module_names", [None for _ in value])
            draw_modules(img, value, names)
        elif prop == "module_selected":
            add_value = draw_module_selected(img, value)
            add_key = "selected_module"
        elif prop == "module_info":
            draw_module_info(img, value[0], properties.get("selected_module"), value[1])
        elif prop == "log":
            log_info(img, value)
    if add_key is not None:
        properties[add_key] = add_value

if len(argv) == 1:
    print("Expected arg 1 = Video file.")
    exit(0)

RECORD_PATH = "../resources/misc/recorded_runs/" + argv[1] + "/"
FILES = [x for x in glob(RECORD_PATH + "*.bin")]
FILES.sort(key=lambda x: int(x.split("\\")[-1].split(".")[0]))
DATA = []

print(f"Frames: {len(FILES)}")
indicators = 20
loaded = 0
progress = 0
for file in FILES:
    with open(file, "rb") as f:
        DATA.append(load(f))
    loaded += 1
    if int(loaded / len(FILES) * indicators) > progress:
        progress = int(loaded / len(FILES) * indicators)
        print("Loading frames... " + str(int(progress * (100 / indicators))) + "%", end="", flush=True)
        print("\r", end="")
print("")

SW, SH = win_util.get_screen_size()

FPS = 30
FRAMES = 0
MIN_F, MAX_F, = 1000, 0
for i, frame_data in enumerate(DATA[1:], start=1):
    frame_time = frame_data[2] - DATA[i-1][2]
    FRAMES += frame_time
    if frame_time < MIN_F:
        MIN_F = frame_time
    elif frame_time > MAX_F:
        MAX_F = frame_time

AVG_FRAMETIME = FRAMES / len(FILES)
FPS = 1 / AVG_FRAMETIME

print(f"Average FPS: {FPS:.0f}")
print(f"Min FPS: {(1/MAX_F):.0f}")
print(f"Max FPS: {(1/MIN_F):.0f}")

CODEC = cv2.VideoWriter_fourcc(*'XVID')
CAPTURE = cv2.VideoWriter(RECORD_PATH+"rendered.avi", CODEC, float(FPS), (SW, SH), True)

rendered = 0
progress = 0
for i, (image, props, timestamp) in enumerate(DATA):
    image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    key_set = list(props.keys())
    key_set.sort(key=get_draw_order)
    draw_properties(image, key_set, props)
    CAPTURE.write(image)
    if i > 0 and timestamp - DATA[i-1][2] >= AVG_FRAMETIME * 2:
        CAPTURE.write(image)
    rendered += 1
    if int(rendered / len(FILES) * indicators) > progress:
        progress = int(rendered / len(FILES) * indicators)
        print("Rendering... " + str(int(progress * (100 / indicators))) + "%", end="", flush=True)
        print("\r", end="")

print(f"Video rendered to file '{RECORD_PATH}rendered.avi'")

CAPTURE.release()
