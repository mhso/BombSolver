import features.util as features_util
import config
from debug import log, LOG_DEBUG

def get_indicator_ratio(img):
    min_y, max_y = 125, 246
    x = 66
    min_rgb = config.DISCHARGE_MIN_RED
    max_rgb = config.DISCHARGE_MAX_RED
    rgb = features_util.split_channels(img)
    filled_height = 0
    for y in range(min_y, max_y):
        if features_util.color_in_range((y, x), rgb, min_rgb, max_rgb):
            filled_height += 1

    total_height = max_y - min_y
    return filled_height / total_height

def solve(img):
    indicator_ratio = get_indicator_ratio(img)
    full_drain_secs = 9
    time_to_drain_secs = full_drain_secs * indicator_ratio
    log(
        f"Discharge should be drained for {time_to_drain_secs:.1f} seconds.",
        LOG_DEBUG, "Needy Discharge"
    )
    return time_to_drain_secs
