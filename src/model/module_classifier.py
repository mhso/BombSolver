import numpy as np
from keras import losses
from keras.layers import Dense, Input, Flatten
from keras.layers.core import Activation
from keras.optimizers import SGD
from keras.models import Model, load_model
from keras.utils.vis_utils import plot_model
from keras.regularizers import l2
import tensorflow as tf
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
    "Morse"
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
BATCH_SIZE = 128
EPOCHS_PER_BATCH = 5
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
    model.compile(optimizer=SGD(lr=LEARNING_RATE,
                                decay=WEIGHT_DECAY,
                                momentum=MOMENTUM),
                  loss=[losses.categorical_crossentropy],
                  metrics=["accuracy"])

def build_model():
    sess = utils.get_nn_config()
    graph = tf.Graph()
    inp = Input(config.MODULE_INPUT_DIM)

    layer = inp

    layer = utils.conv_layer(layer, CONV_FILTERS, KERNEL_SIZE, REGULARIZER_CONST)

    for i in range(CONV_LAYERS):
        layer = utils.conv_layer(layer, CONV_FILTERS, KERNEL_SIZE, REGULARIZER_CONST)
        #if i % 3 == 0:
        #    layer = Dropout(0.3)(layer)

    out = output_layer(layer)
    model = Model(inputs=inp, outputs=out)
    compile_model(model)
    model._make_predict_function()

    return model, graph, sess

def shape_input(inp):
    reshaped = inp
    if len(inp.shape) < 4:
        reshaped = inp.reshape((1,)+config.MODULE_INPUT_DIM)
    return reshaped

def load_from_file(filename):
    graph = tf.Graph()
    with graph.as_default():
        sess = utils.get_nn_config()
        with sess.as_default():
            model = load_model(filename, compile=False)
            compile_model(model)
            return model, graph, sess
    return None

def evaluate(model, inputs, expected_out):
    score = model.evaluate(inputs, expected_out, verbose=0)
    return (score[0], score[1])

def predict(model, inp):
    with model[1].as_default():
        with model[2].as_default():
            return model[0].predict(shape_input(inp))

def train(model, inputs, expected_out):
    result = model.fit(inputs, expected_out, batch_size=BATCH_SIZE, verbose=0,
                       epochs=EPOCHS_PER_BATCH, validation_split=VALIDATION_SPLIT)
    return result.history
