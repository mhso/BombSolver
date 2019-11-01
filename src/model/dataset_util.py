import numpy as np
import cv2

def resize_img(img, new_size):
    return cv2.resize(img, new_size, cv2.INTER_AREA)

def pad_image(img):
    new_img = img
    h, w, c = img.shape
    dif = abs(h - w)
    if h > w:
        zeros = np.zeros((h, int(dif/2), c), dtype="uint8")
        new_img = np.concatenate((zeros, img, zeros), 1)
    elif w > h:
        zeros = np.zeros((int(dif/2), w, c), dtype="uint8")
        new_img = np.concatenate((zeros, img, zeros), 0)
    return new_img

def sample_data(images, labels, size):
    indices = [i for i in range(images.shape[0])]
    batch = np.random.choice(indices, size=size, p=[1/len(indices) for _ in indices])
    b_x = np.array([images[i] for i in batch])
    b_y = np.array([labels[i] for i in batch])
    return (b_x, b_y)
