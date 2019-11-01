import os
from keras.backend.tensorflow_backend import set_session, clear_session
from keras.models import save_model, load_model
import tensorflow as tf
import config

def set_nn_config():
    # Clean up from previous TF graphs.
    tf.reset_default_graph()
    clear_session()

    # Config options, to stop TF from eating all GPU memory.
    nn_config = tf.ConfigProto()
    nn_config.gpu_options.per_process_gpu_memory_fraction = config.MAX_GPU_FRACTION
    nn_config.gpu_options.allow_growth = True
    set_session(tf.Session(config=nn_config))

def model_exists(filename):
    return os.path.exists(filename)

def save_to_file(model, filename):
    save_model(model, filename, True, True)

def load_from_file(filename):
    set_nn_config()
    model = load_model(filename, compile=False)
    return model
