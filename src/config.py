# Misc options.
VERBOSITY = 2
LOG_WARNING = 1
LOG_DEBUG = 2
LOG_OVERLAY = 3

# Neural network options.
MODULE_INPUT_DIM = (3, 64, 64)
CHAR_INPUT_DIM = (3, 32, 32)
SYMBOLS_INPUT_DIM = (3, 32, 32)

MODULE_OUTPUT_DIM = 23
CHAR_OUTPUT_DIM = 36
SYMBOLS_OUTPUT_DIM = 27

GPU_MEMORY = 8192
MAX_GPU_FRACTION = 0.4

# Image analysis specific
SERIAL_MIN_RED = (110, 0, 0)
SERIAL_MAX_RED = (255, 99, 71)

DISCHARGE_MIN_RED = (200, 0, 0)
DISCHARGE_MAX_RED = (255, 50, 50)

WIRE_COLOR_RANGE = [
    ((0, 0, 0), (25, 25, 25)), # Black.
    ((190, 190, 0), (255, 255, 50)), # Yellow.
    ((30, 30, 120), (100, 100, 255)), # Blue.
    ((175, 175, 175), (255, 255, 255)), # White.
    ((139, 0, 0), (255, 99, 71)) # Red.
]

BUTTON_COLOR_RANGE = [
    ((190, 190, 190), (255, 255, 255)), # White.
    ((170, 130, 0), (255, 255, 50)), # Yellow.
    ((20, 30, 120), (110, 110, 255)), # Blue.
    ((139, 0, 0), (255, 100, 100)) # Red.
]

SIMON_COLOR_RANGE = [
    ((240, 100, 30), (255, 140, 60)), # Red.
    ((15, 200, 235), (50, 235, 255)), # Blue.
    ((30, 240, 190), (65, 255, 230)), # Green.
    ((160, 170, 45), (230, 255, 110)) # Yellow.
]
