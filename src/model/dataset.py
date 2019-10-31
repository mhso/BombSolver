from glob import glob
import cv2
import numpy as np
import config

def resize_img(img):
    return cv2.resize(img, (config.INPUT_DIM[1], config.INPUT_DIM[2]), cv2.INTER_AREA)

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

def load_dataset():
    images = []
    labels = []
    for label in range(config.OUTPUT_DIM):
        files = glob(f"../resources/labeled_images/{label}/*.png")
        one_hot_labels = [0] * config.OUTPUT_DIM
        one_hot_labels[label] = 1
        for i, file in enumerate(files):
            image = cv2.imread(file, cv2.IMREAD_COLOR)
            images.append(image.reshape(config.INPUT_DIM).astype("float32"))
            labels.append(np.array(one_hot_labels))
    return (np.array(images), np.array(labels))

def sample_data(images, labels):
    indices = [i for i in range(images.shape[0])]
    batch = np.random.choice(indices, size=config.BATCH_SIZE, p=[1/len(indices) for _ in indices])
    b_x = np.array([images[i] for i in batch])
    b_y = np.array([labels[i] for i in batch])
    return (b_x, b_y)
