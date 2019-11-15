from glob import glob
import numpy as np
import cv2
import config
import model.dataset_util as dataset_util

def load_dataset():
    images = []
    labels = []
    characters = [x for x in range(10)] + [chr(x) for x in range(97, 123)]
    for label in range(config.SERIAL_OUTPUT_DIM):
        files = glob(f"../resources/labeled_images/serial/{characters[label]}/*.png")
        one_hot_labels = [0] * config.SERIAL_OUTPUT_DIM
        one_hot_labels[label] = 1
        if len(files) == 0:
            images.append(np.zeros(config.SERIAL_INPUT_DIM))
            labels.append(np.array(one_hot_labels))
        for file in files:
            image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
            images.append(dataset_util.reshape(image, config.SERIAL_INPUT_DIM[1:]))
            labels.append(np.array(one_hot_labels))

    return dataset_util.extract_test_data(np.array(images), np.array(labels), config.SERIAL_OUTPUT_DIM, 4)
