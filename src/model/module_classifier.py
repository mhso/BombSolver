from tensorflow.keras import losses
from tensorflow.keras.layers import Dense, Input, Flatten
from tensorflow.keras.layers import Activation
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.utils import plot_model
from tensorflow.keras.regularizers import l2
import config
import model.classifier_util as utils

LABELS = [
    "Nothing (Side)",
    "Big battery",
    "Small batteries",
    "Serial number",
    "Metal piece",
    "Parallel port",
    "Indicator",
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
    "Morse",
    "Needy Vent",
    "Needy Discharge",
    "Needy Knob"
]

# Layer constants.
CONV_FILTERS = 32
CONV_LAYERS = 4
KERNEL_SIZE = 5
USE_BIAS = False
REGULARIZER_CONST = 0.001

# Optimizer constants.
LEARNING_RATE = 0.02
MOMENTUM = 0.9
WEIGHT_DECAY = 1e-4

# Training constants.
BATCH_SIZE = 160
EPOCHS_PER_BATCH = 6
VALIDATION_SPLIT = 0.3
TESTS_PER_LABEL = 4

def output_layer(prev):
    out = Flatten()(prev)

    out = Dense(292, kernel_regularizer=l2(REGULARIZER_CONST),
                use_bias=USE_BIAS)(out)

    out = Dense(config.MODULE_OUTPUT_DIM, kernel_regularizer=l2(REGULARIZER_CONST),
                use_bias=USE_BIAS)(out)
    out = Activation("softmax")(out)

    return out

def save_as_image(model):
    plot_model(model, to_file='../resources/model_graph.png', show_shapes=True)

def compile_model(model):
    model.compile(
        optimizer=SGD(learning_rate=LEARNING_RATE, decay=WEIGHT_DECAY, momentum=MOMENTUM),
        loss=[losses.categorical_crossentropy],
        metrics=["accuracy"]
    )

def build_model():
    utils.set_nn_config()
    inp = Input(config.MODULE_INPUT_DIM)

    layer = inp

    layer = utils.conv_layer(layer, CONV_FILTERS, KERNEL_SIZE, REGULARIZER_CONST)

    for _ in range(CONV_LAYERS):
        layer = utils.conv_layer(layer, CONV_FILTERS, KERNEL_SIZE, REGULARIZER_CONST)

    out = output_layer(layer)
    model = Model(inputs=inp, outputs=out)
    compile_model(model)

    return model

def shape_input(inp):
    reshaped = inp
    if len(inp.shape) < 4:
        reshaped = inp.reshape((1,)+config.MODULE_INPUT_DIM)
    return reshaped

def load_from_file(filename):
    utils.set_nn_config()
    model = load_model(filename, compile=False)
    compile_model(model)
    return model

def evaluate(model, inputs, expected_out):
    score = model.evaluate(inputs, expected_out, verbose=0)
    return (score[0], score[1])

def predict(model, inp):
    return model.predict(shape_input(inp))

def train(model, inputs, expected_out):
    result = model.fit(
        inputs, expected_out, batch_size=BATCH_SIZE, verbose=0,
        epochs=EPOCHS_PER_BATCH, validation_split=VALIDATION_SPLIT
    )
    return result.history
