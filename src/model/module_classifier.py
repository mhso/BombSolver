import numpy as np
from keras import losses
from keras.layers import Dense, Conv2D, BatchNormalization, Input, Flatten
from keras.layers.core import Activation
from keras.optimizers import SGD
from keras.models import Model
from keras.utils.vis_utils import plot_model
from keras.regularizers import l2
from keras.layers import LeakyReLU
import tensorflow as tf
import config
import model.classifier_util as utils

def conv_layer(prev, filters, kernel_size):
    conv = Conv2D(filters, kernel_size=(kernel_size, kernel_size), strides=1, padding="same",
                  kernel_regularizer=l2(config.REGULARIZER_CONST))(prev)
    conv = BatchNormalization()(conv)
    conv = LeakyReLU()(conv)
    return conv

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

    layer = conv_layer(layer, config.CONV_FILTERS, config.KERNEL_SIZE)

    for i in range(config.CONV_LAYERS):
        layer = conv_layer(layer, config.CONV_FILTERS, config.KERNEL_SIZE)
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

def predict(model, inp):
    shaped_input = shape_input(inp)
    return model.predict(shaped_input)

def get_best_prediction(prediction):
    return np.argmax(prediction, axis=1)

def train(model, inputs, expected_out):
    result = model.fit(inputs, expected_out, batch_size=config.MODULE_BATCH_SIZE, verbose=0,
                       epochs=config.EPOCHS_PER_BATCH, validation_split=config.VALIDATION_SPLIT)
    return result.history
