# Misc options.
VERBOSITY = 2
LOG_WARNING = 1
LOG_DEBUG = 2

# Neural network options.
INPUT_DIM = (3, 64, 64)
SERIAL_INPUT_DIM = (3, 32, 32)

OUTPUT_DIM = 20
SERIAL_OUTPUT_DIM = 36

MAX_GPU_FRACTION = 0.4

CONV_FILTERS = 32

CONV_LAYERS = 4

KERNEL_SIZE = 5

USE_BIAS = False

REGULARIZER_CONST = 0.001

LEARNING_RATE = 0.02

MOMENTUM = 0.9

WEIGHT_DECAY = 1e-4

MODULE_BATCH_SIZE = 128
SERIAL_BATCH_SIZE = 204

EPOCHS_PER_BATCH = 5
SERIAL_EPOCHS_PER_BATCH = 10

VALIDATION_SPLIT = 0.3

# Image analysis specific
SERIAL_MIN_RED = (110, 0, 0)
SERIAL_MAX_RED = (255, 99, 71)

WIRE_COLOR_RANGE = [
    ((0, 0, 0), (25, 25, 25)), # Black.
    ((220, 220, 0), (255, 255, 20)), # Yellow.
    ((30, 30, 120), (100, 100, 255)), # Blue.
    ((200, 200, 200), (255, 255, 255)), # White.
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
