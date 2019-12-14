import traceback
from glob import glob
from cv2 import imwrite
import config
import view.overlay

LOG_DEBUG = config.LOG_DEBUG
LOG_WARNING = config.LOG_WARNING
LOGS = []

def log(arg, verbose=0, module="BombSolver"):
    print_str = f"[{module}] - {arg}"
    LOGS.append(print_str)
    if config.VERBOSITY >= verbose:
        print(print_str)
    if config.VERBOSITY == config.LOG_OVERLAY:
        view.overlay.GUIOverlay.add_status("log", LOGS)

def handle_module_exception(module_name, module_img):
    log(f"WARNING: Could not solve '{module_name}'.", config.LOG_WARNING)
    log(traceback.format_exc(10), config.LOG_DEBUG)
    path = "../resources/misc/error_imgs/"
    file_name = len(glob(path + "*.png"))
    imwrite(f"{path}{file_name}.png", module_img)
