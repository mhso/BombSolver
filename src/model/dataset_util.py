from glob import glob
from math import floor, ceil
import numpy as np
import cv2

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
    img = cv2_img.copy()
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h, w, c = img.shape
    assert c in (3, 1)
    if h != w:
        img = pad_image(img)
    if (h, w) != size:
        img = resize_img(img, size)
    img = img.reshape(((c,) + size))
    img = img.astype("float32")
    if np.any(img > 1):
        img = img / 255
    return img

def extract_test_data(images, labels, output_dim, cases_per_label):
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
        end_of_label = i
        while label == curr_label-1 and end_of_label < labels.shape[0]:
            label = np.where(labels[end_of_label] == 1)[0]
            end_of_label += 1
        rand_indices = np.random.choice([x for x in range(i+1, end_of_label)], size=cases_per_label)
        test_labels.extend(labels[r_i] for r_i in rand_indices)
        test_images.extend(images[r_i] for r_i in rand_indices)
        indexes.extend([r_i for r_i in rand_indices])
    for index in reversed(indexes):
        train_images.pop(index)
        train_labels.pop(index)
    return (np.array(train_images), np.array(train_labels),
            np.array(test_images), np.array(test_labels))

def load_dataset(path, label_names, data_dims, tests_per_label=4):
    input_dim, output_dim = data_dims
    images = []
    labels = []
    for label, name in enumerate(label_names):
        files = glob(f"{path}{name}/*.png")
        one_hot_labels = [0] * output_dim
        one_hot_labels[label] = 1
        if files == []:
            images.append(np.zeros(input_dim))
            labels.append(np.array(one_hot_labels))
        for file in files:
            image = cv2.imread(file, cv2.IMREAD_COLOR)
            images.append(reshape(image, input_dim[1:]))
            labels.append(np.array(one_hot_labels))

    return extract_test_data(np.array(images), np.array(labels), output_dim, tests_per_label)

def sample_data(images, labels, size):
    indices = [i for i in range(images.shape[0])]
    batch = np.random.choice(indices, size=size, p=[1/len(indices) for _ in indices])
    b_x = np.array([images[i] for i in batch])
    b_y = np.array([labels[i] for i in batch])
    return (b_x, b_y)
