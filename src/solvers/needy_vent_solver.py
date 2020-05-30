import features.needy_vent as vent_features
import config
from debug import log

def solve(img):
    chars = vent_features.get_characters(img)
    coords = 0, 0
    if len(chars) < 9:
        log(f"Press 'Yes'.", config.LOG_DEBUG, "Needy Vent")
        coords = 222, 135
    else:
        log(f"Press 'No'.", config.LOG_DEBUG, "Needy Vent")
        coords = 222, 175
    return coords
