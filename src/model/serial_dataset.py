from keras.datasets import mnist
from keras.utils import to_categorical
import config

def load_dataset():
    img_rows = 28
    img_cols = 28

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
    x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255

    y_train = to_categorical(y_train, config.SERIAL_OUTPUT_DIM)
    y_test = to_categorical(y_test, config.SERIAL_OUTPUT_DIM)
    return x_train, y_train, x_test, y_test
