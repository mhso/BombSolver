from glob import glob
import cv2
import numpy as np
import config
import model.dataset_util as dataset_util

def load_dataset():
    images = []
    labels = []
    for label in range(config.OUTPUT_DIM):
        files = glob(f"../resources/labeled_images/modules/{label}/*.png")
        one_hot_labels = [0] * config.OUTPUT_DIM
        one_hot_labels[label] = 1
        for i, file in enumerate(files):
            image = cv2.imread(file, cv2.IMREAD_COLOR)
            reshaped = image.reshape(config.INPUT_DIM).astype("float32")
            reshaped /= 255
            images.append(reshaped)
            labels.append(np.array(one_hot_labels))
    return dataset_util.extract_test_data(np.array(images), np.array(labels), config.OUTPUT_DIM)
