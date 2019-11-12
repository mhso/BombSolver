from glob import glob
import pickle
import cv2
import numpy as np
from keras.utils import to_categorical
from scipy.io import loadmat
import config
import model.dataset_util as dataset_util

def load_emnist_dataset(mat_file_path, max):
    """
    Function taken from https://github.com/NeilNie/EMNIST-Keras
    """
    width, height = config.SERIAL_INPUT_DIM[1:]
    def rotate(img):
        # Used to rotate images (for some reason they are transposed on read-in)
        flipped = np.fliplr(img)
        return np.rot90(flipped)

    # Load convoluted list structure form loadmat
    mat = loadmat(mat_file_path)

    # Load char mapping
    mapping = {kv[0]:kv[1:][0] for kv in mat['dataset'][0][0][2]}
    pickle.dump(mapping, open('../bin/mapping.p', 'wb'))

    # Load training data
    if max == None:
        max = len(mat['dataset'][0][0][0][0][0][0])
    training_images = mat['dataset'][0][0][0][0][0][0][:max].reshape(max, height, width, 1)
    training_labels = mat['dataset'][0][0][0][0][0][1][:max]

    # Load testing data
    if max == None:
        max = len(mat['dataset'][0][0][1][0][0][0])
    else:
        max = int(max / 6)
    testing_images = mat['dataset'][0][0][1][0][0][0][:max].reshape(max, height, width, 1)
    testing_labels = mat['dataset'][0][0][1][0][0][1][:max]

    # Reshape training data to be valid
    _len = len(training_images)
    for i in range(len(training_images)):
        print('%d/%d (%.2lf%%)' % (i + 1, _len, ((i + 1)/_len) * 100), end='\r')
        training_images[i] = rotate(training_images[i])
    print('')

    # Reshape testing data to be valid
    _len = len(testing_images)
    for i in range(len(testing_images)):
        print('%d/%d (%.2lf%%)' % (i + 1, _len, ((i + 1)/_len) * 100), end='\r')
        testing_images[i] = rotate(testing_images[i])
    print('')

    training_images = np.repeat(training_images, 3, axis=3)
    testing_images = np.repeat(testing_images, 3, axis=3)

    training_images = np.reshape(training_images, (-1,) + (config.SERIAL_INPUT_DIM))
    testing_images = np.reshape(testing_images, (-1,) + (config.SERIAL_INPUT_DIM))

    # Convert type to float32
    training_images = training_images.astype('float32')
    testing_images = testing_images.astype('float32')

    # Normalize to prevent issues with model
    training_images /= 255
    testing_images /= 255

    nb_classes = len(mapping)

    if min(training_labels) == 1:
        training_labels += 9
        testing_labels += 9

    return ((training_images, training_labels), (testing_images, testing_labels), mapping, nb_classes)

def load_emnist_letters(max_data=1000):
    train, test, _, _ = load_emnist_dataset("../resources/matlab/emnist-letters", max_data)

    x_train, y_train = train
    x_test, y_test = test

    y_train = to_categorical(y_train, num_classes=config.SERIAL_OUTPUT_DIM)
    y_test = to_categorical(y_test, num_classes=config.SERIAL_OUTPUT_DIM)

    return x_train, y_train, x_test, y_test

def load_emnist_digits(max_data=1000):
    train, test, _, _ = load_emnist_dataset("../resources/matlab/emnist-digits", max_data)

    x_train, y_train = train
    x_test, y_test = test

    y_train = to_categorical(y_train, num_classes=config.SERIAL_OUTPUT_DIM)
    y_test = to_categorical(y_test, num_classes=config.SERIAL_OUTPUT_DIM)

    return x_train, y_train, x_test, y_test

def merge_datasets(letters, digits):
    lx_train, ly_train, lx_test, ly_test = letters
    dx_train, dy_train, dx_test, dy_test = digits
    return (np.concatenate((lx_train, dx_train)), np.concatenate((ly_train, dy_train)),
            np.concatenate((lx_test, dx_test)), np.concatenate((ly_test, dy_test)))

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
        if len(files) == 0:
            images.append(np.zeros(config.SERIAL_INPUT_DIM))
            labels.append(np.array(one_hot_labels))
        for i, file in enumerate(files):
            image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
            reshaped = np.repeat(image.reshape((1,) + config.SERIAL_INPUT_DIM[1:]), 3, axis=0).astype("float32")
            reshaped /= 255
            images.append(reshaped)
            labels.append(np.array(one_hot_labels))

    return dataset_util.extract_test_data(np.array(images), np.array(labels), config.SERIAL_OUTPUT_DIM, 4)
