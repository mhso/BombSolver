from glob import glob
from math import floor, ceil
import numpy as np
import cv2
import config

def resize_img(img, new_size):
    return cv2.resize(img, new_size, cv2.INTER_AREA)

def pad_image(img):
    new_img = img
    h, w, c = img.shape
    dif = abs(h - w)
    if h > w:
        left = np.zeros((h, ceil(dif/2), c))
        right = np.zeros((h, floor(dif/2), c))
        new_img = np.concatenate((left, img, right), 1)
    elif w > h:
        up = np.zeros((ceil(dif/2), w, c))
        down = np.zeros((floor(dif/2), w, c))
        new_img = np.concatenate((up, img, down), 0)
    return new_img

def reshape(cv2_img, size):
    img = cv2_img
    if len(cv2_img.shape) == 2:
        img = img.reshape(img.shape + (1,))
    h, w, c = img.shape
    assert c in (3, 1)
    if h != w:
        img = pad_image(img)
    if (h, w) != size:
        img = resize_img(img, size)
    img = img.reshape(((c,) + size))
    if c == 1:
        img = np.repeat(img, 3, axis=0)
    img = img.astype("float32")
    if np.any(img > 1):
        img = img / 255
    return img

def extract_test_data(images, labels, output_dim, cases_per_label=1):
    test_images = []
    test_labels = []
    indexes = []
    train_images = [x for x in images]
    train_labels = [y for y in labels]
    i = 0
    curr_label = 0
    while len(test_images) < output_dim * cases_per_label:
        label = np.where(labels[i] == 1)[0]
        while label < curr_label:
            i += 1
            label = np.where(labels[i] == 1)[0]
        curr_label += 1
        test_labels.extend(labels[i:i+cases_per_label])
        test_images.extend(images[i:i+cases_per_label])
        indexes.extend([i+x for x in range(cases_per_label)])
    for index in reversed(indexes):
        train_images.pop(index)
        train_labels.pop(index)
    return (np.array(train_images), np.array(train_labels),
            np.array(test_images), np.array(test_labels))

def load_dataset(path, label_names):
    images = []
    labels = []
    for label, name in enumerate(label_names):
        files = glob(f"{path}{name}/*.png")
        one_hot_labels = [0] * config.SERIAL_OUTPUT_DIM
        one_hot_labels[label] = 1
        if len(files) == 0:
            images.append(np.zeros(config.SERIAL_INPUT_DIM))
            labels.append(np.array(one_hot_labels))
        for file in files:
            image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
            images.append(reshape(image, config.SERIAL_INPUT_DIM[1:]))
            labels.append(np.array(one_hot_labels))

    return extract_test_data(np.array(images), np.array(labels), config.SERIAL_OUTPUT_DIM, 4)

def sample_data(images, labels, size):
    indices = [i for i in range(images.shape[0])]
    batch = np.random.choice(indices, size=size, p=[1/len(indices) for _ in indices])
    b_x = np.array([images[i] for i in batch])
    b_y = np.array([labels[i] for i in batch])
    return (b_x, b_y)
