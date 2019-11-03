import os
from keras.layers import Conv2D, BatchNormalization
from keras.backend.tensorflow_backend import set_session, clear_session
from keras.regularizers import l2
from keras.models import save_model
from keras.layers import LeakyReLU
import tensorflow as tf
from numpy import argmax
import config

def get_nn_config():
    # Clean up from previous TF graphs.
    #tf.reset_default_graph()
    #clear_session()

    # Config options, to stop TF from eating all GPU memory.
    nn_config = tf.ConfigProto()
    nn_config.gpu_options.per_process_gpu_memory_fraction = config.MAX_GPU_FRACTION
    nn_config.gpu_options.allow_growth = True
    return tf.Session(config=nn_config)

def conv_layer(prev, filters, kernel_size):
    conv = Conv2D(filters, kernel_size=(kernel_size, kernel_size), strides=1, padding="same",
                  kernel_regularizer=l2(config.REGULARIZER_CONST))(prev)
    conv = BatchNormalization()(conv)
    conv = LeakyReLU()(conv)
    return conv

def model_exists(filename):
    return os.path.exists(filename)

def save_to_file(model, filename):
    save_model(model, filename, True, True)

def get_best_prediction(prediction):
    return argmax(prediction, axis=1)
