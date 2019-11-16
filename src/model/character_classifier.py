import keras
from keras.layers import Dense, Dropout, Flatten, Input
from keras.layers import MaxPooling2D, Activation
from keras.models import Model, load_model
from keras.optimizers import SGD
from tensorflow import Graph
import config
import model.classifier_util as utils

LABELS = [str(x) for x in range(10)] + [chr(x) for x in range(97, 123)]

# Layer constants.
CONV_FILTERS = 32
KERNEL_SIZE = 3
REGULARIZER_CONST = 0.001

# Optimizer constants.
LEARNING_RATE = 0.02
MOMENTUM = 0.9
WEIGHT_DECAY = 1e-4

# Training constants.
BATCH_SIZE = 256
EPOCHS_PER_BATCH = 10
VALIDATION_SPLIT = 0.3

def build_model():
    sess = utils.get_nn_config()
    graph = Graph()
    inp = Input(config.CHAR_INPUT_DIM)

    layer = utils.conv_layer(inp, CONV_FILTERS, KERNEL_SIZE, REGULARIZER_CONST)
    layer = utils.conv_layer(layer, CONV_FILTERS*2, KERNEL_SIZE, REGULARIZER_CONST)
    layer = Dropout(0.25)(layer)
    layer = MaxPooling2D(pool_size=(2, 2), padding="same")(layer)
    layer = Dense(512, activation='relu')(layer)
    layer = MaxPooling2D(pool_size=(2, 2), padding="same")(layer)
    layer = Flatten()(layer)
    layer = Dense(256, activation='relu')(layer)
    layer = Dropout(0.5)(layer)
    out = Dense(config.CHAR_OUTPUT_DIM, activation='softmax')(layer)

    model = Model(inputs=inp, outputs=out)

    compile_model(model)
    model._make_predict_function()

    return model, graph, sess

def compile_model(model):
    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=SGD(lr=LEARNING_RATE,
                                decay=WEIGHT_DECAY,
                                momentum=MOMENTUM),
                  metrics=['accuracy'])

def train(model, inputs, expected_out):
    result = model.fit(inputs, expected_out, batch_size=BATCH_SIZE,
                       epochs=EPOCHS_PER_BATCH, verbose=0)
    return result.history

def evaluate(model, inputs, expected_out):
    score = model.evaluate(inputs, expected_out, verbose=0)
    return (score[0], score[1])

def load_from_file(filename):
    graph = Graph()
    with graph.as_default():
        sess = utils.get_nn_config()
        with sess.as_default():
            model = load_model(filename, compile=False)
            compile_model(model)
            return model, graph, sess
    return None

def shape_input(inp):
    reshaped = inp
    if len(inp.shape) < 4:
        reshaped = inp.reshape((1,)+config.CHAR_INPUT_DIM)
    return reshaped

def predict(model, inp):
    with model[1].as_default():
        with model[2].as_default():
            return model[0].predict(shape_input(inp))
