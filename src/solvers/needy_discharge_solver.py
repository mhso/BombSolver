import features.util as features_util
import config
from debug import log, LOG_DEBUG

FULL_DRAIN_TIME = 9

def get_indicator_ratio(img):
    """
    Get a ratio of how filled up the capacitor indicator is.
    This tells us how long the module has been active.
    (We could just look at the numbers on the countdown display,
    but this is more fun and also faster).
    """
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
    """
    Discarge/drain the capacitor in order to reset
    the needy module to the 45 second countdown.
    """
    indicator_ratio = get_indicator_ratio(img)
    time_to_drain_secs = FULL_DRAIN_TIME * indicator_ratio
    log(
        f"Discharge should be drained for {time_to_drain_secs:.1f} seconds.",
        LOG_DEBUG, "Needy Discharge"
    )

    return time_to_drain_secs
