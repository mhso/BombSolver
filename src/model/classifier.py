import os
import numpy as np
import tensorflow as tf
from keras import losses
from keras.initializers import RandomNormal
from keras.backend.tensorflow_backend import set_session, clear_session
from keras.layers import Dense, Conv2D, BatchNormalization, Input, Flatten, MaxPooling2D, Dropout
from keras.layers.core import Activation
from keras.optimizers import SGD, Adam
from keras.models import Model, clone_model, save_model, load_model
from keras.utils.vis_utils import plot_model
from keras.regularizers import l2
from keras.layers import LeakyReLU
import config
from model.residual import Residual

def set_nn_config():
    # Clean up from previous TF graphs.
    tf.reset_default_graph()
    clear_session()

    # Config options, to stop TF from eating all GPU memory.
    nn_config = tf.ConfigProto()
    nn_config.gpu_options.per_process_gpu_memory_fraction = config.MAX_GPU_FRACTION
    nn_config.gpu_options.allow_growth = True
    set_session(tf.Session(config=nn_config))

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
    set_nn_config()

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

def model_exists(filename):
    return os.path.exists(filename)

def save_to_file(model, filename):
    save_model(model, filename, True, True)

def load_from_file(filename):
    set_nn_config()
    model = load_model(filename, compile=False)
    compile_model(model)
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
    result = model.fit(inputs, expected_out, batch_size=config.BATCH_SIZE, verbose=0,
                       epochs=config.EPOCHS_PER_BATCH, validation_split=config.VALIDATION_SPLIT)
    return result.history
