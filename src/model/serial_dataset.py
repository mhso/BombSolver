from glob import glob
import cv2
import numpy as np
from keras.datasets import mnist
from keras.utils import to_categorical
import config
import model.dataset_util as dataset_util

def load_dataset():
    img_rows = 32
    img_cols = 32

    images = []
    labels = []
    characters = [x for x in range(10)] + [chr(x) for x in range(97, 123)]
    for label in range(config.SERIAL_OUTPUT_DIM):
        files = glob(f"../resources/labeled_images/serial/{characters[label]}/*.png")
        one_hot_labels = [0] * config.SERIAL_OUTPUT_DIM
        one_hot_labels[label] = 1
        for i, file in enumerate(files):
            image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
            reshaped = image.reshape(config.SERIAL_INPUT_DIM).astype("float32")
            reshaped /= 255
            images.append(reshaped)
            labels.append(np.array(one_hot_labels))

    return dataset_util.extract_test_data(np.array(images), np.array(labels), config.SERIAL_OUTPUT_DIM)
