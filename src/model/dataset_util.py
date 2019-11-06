from math import floor, ceil
import numpy as np
import cv2

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

def resize_img(img, new_size):
    return cv2.resize(img, new_size, cv2.INTER_AREA)

def pad_image(img):
    new_img = img
    h, w, c = img.shape
    dif = abs(h - w)
    if h > w:
        left = np.zeros((h, ceil(dif/2), c), dtype="uint8")
        right = np.zeros((h, floor(dif/2), c), dtype="uint8")
        new_img = np.concatenate((left, img, right), 1)
    elif w > h:
        left = np.zeros((ceil(dif/2), w, c), dtype="uint8")
        right = np.zeros((floor(dif/2), w, c), dtype="uint8")
        new_img = np.concatenate((left, img, right), 0)
    return new_img

def sample_data(images, labels, size):
    indices = [i for i in range(images.shape[0])]
    batch = np.random.choice(indices, size=size, p=[1/len(indices) for _ in indices])
    b_x = np.array([images[i] for i in batch])
    b_y = np.array([labels[i] for i in batch])
    return (b_x, b_y)
