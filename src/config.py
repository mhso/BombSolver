# Neural network options.
INPUT_DIM = (3, 64, 64)

OUTPUT_DIM = 39

MAX_GPU_FRACTION = 0.4

CONV_FILTERS = 32

CONV_LAYERS = 4

KERNEL_SIZE = 5

USE_BIAS = False

REGULARIZER_CONST = 0.001

LEARNING_RATE = 0.02

MOMENTUM = 0.9

WEIGHT_DECAY = 1e-4

BATCH_SIZE = 128

EPOCHS_PER_BATCH = 5

VALIDATION_SPLIT = 0.3

LABELS = [
    "Nothing (Side)",
    "Big battery",
    "Small batteries",
    "Serial number",
    "Metal piece without parallel port",
    "Parallel port",
    "Lit SIG indicator",
    "Unlit SIG indicator",
    "Lit NSA indicator",
    "Unlit NSA indicator",
    "Lit BOB indicator",
    "Unlit BOB indicator",
    "Lit FRQ indicator",
    "Lit SND indicator",
    "Unlit SND indicator",
    "Lit CLR indicator",
    "Unlit CLR indicator",
    "Lit CAR indicator",
    "Unlit CAR indicator",
    "Lit IND indicator",
    "Lit MSA indicator",
    "Unlit MSA indicator",
    "Lit TRN indicator",
    "Unlit TRN indicator",
    "Lit FRK indicator",
    "Unlit FRK indicator",
    "Nothing (Front)",
    "Timer",
    "Wires",
    "Button",
    "Symbols",
    "Simon Says",
    "Wire Sequence",
    "Complicated Wires",
    "Memory Game",
    "Who's On First?",
    "Maze",
    "Password",
    "Morse"
]
