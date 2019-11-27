import traceback
from glob import glob
from cv2 import imwrite
import config


LOG_DEBUG = config.LOG_DEBUG
LOG_WARNING = config.LOG_WARNING

def log(arg, verbose=0, module="BombSolver"):
    if config.VERBOSITY >= verbose:
        print(f"[{module}] - {arg}")

def handle_module_exception(module_name, module_img):
    log(f"WARNING: Could not solve '{module_name}'.", config.LOG_WARNING)
    log(traceback.format_exc(10), config.LOG_DEBUG)
    path = "../resources/misc/error_imgs/"
    file_name = len(glob(path + "*.png"))
    imwrite(f"{path}{file_name}.png", module_img)
