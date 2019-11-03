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

def output_layer(prev):
    out = Flatten()(prev)

    out = Dense(292, kernel_regularizer=l2(config.REGULARIZER_CONST),
                use_bias=config.USE_BIAS)(out)

    out = Dense(config.OUTPUT_DIM, kernel_regularizer=l2(config.REGULARIZER_CONST),
                use_bias=config.USE_BIAS)(out)
    out = Activation("softmax")(out)

    return out

def save_as_image(model):
    plot_model(model, to_file='../resources/model_graph.png', show_shapes=True)

def compile_model(model):
    model.compile(optimizer=SGD(lr=config.LEARNING_RATE,
                                decay=config.WEIGHT_DECAY,
                                momentum=config.MOMENTUM),
                  loss=[losses.categorical_crossentropy],
                  metrics=["accuracy"])

def build_model():
    utils.set_nn_config()

    inp = Input(config.INPUT_DIM)

    layer = inp

    layer = utils.conv_layer(layer, config.CONV_FILTERS, config.KERNEL_SIZE)

    for i in range(config.CONV_LAYERS):
        layer = utils.conv_layer(layer, config.CONV_FILTERS, config.KERNEL_SIZE)
        #if i % 3 == 0:
        #    layer = Dropout(0.3)(layer)

    out = output_layer(layer)
    model = Model(inputs=inp, outputs=out)
    compile_model(model)
    model._make_predict_function()
    return model

def shape_input(inp):
    reshaped = inp
    if len(inp.shape) < 4:
        reshaped = np.array([inp]).reshape((-1,)+config.INPUT_DIM)
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

def predict(model, inp):
    with model[1].as_default():
        with model[2].as_default():
            return model[0].predict(shape_input(inp))

def train(model, inputs, expected_out):
    result = model.fit(inputs, expected_out, batch_size=config.MODULE_BATCH_SIZE, verbose=0,
                       epochs=config.EPOCHS_PER_BATCH, validation_split=config.VALIDATION_SPLIT)
    return result.history
