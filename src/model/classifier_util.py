import os
from tensorflow.keras.layers import Conv2D, BatchNormalization
from tensorflow.keras.regularizers import l2
from tensorflow.keras.models import save_model
from tensorflow.keras.layers import LeakyReLU
import tensorflow as tf
from numpy import argmax
import config

def set_nn_config():
    # Config options, to stop TF from eating all GPU memory.
    gpus = tf.config.list_physical_devices("GPU")
    max_memory = config.GPU_MEMORY * config.MAX_GPU_FRACTION
    tf.config.experimental.set_virtual_device_configuration(
        gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=max_memory)]
    )

def conv_layer(prev, filters, kernel_size, regularizer_const):
    conv = Conv2D(
        filters, kernel_size=(kernel_size, kernel_size), strides=1, padding="same",
        kernel_regularizer=l2(regularizer_const)
    )(prev)
    conv = BatchNormalization()(conv)
    conv = LeakyReLU()(conv)
    return conv

def model_exists(filename):
    return os.path.exists(filename)

def save_to_file(model, filename):
    save_model(model, filename, True, True)

def get_best_prediction(prediction):
    return argmax(prediction, axis=1)
