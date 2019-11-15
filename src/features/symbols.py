import numpy as np
from model import (dataset_util,
                   character_classifier as classifier,
                   classifier_util)
import config

def get_threshold(image):
    return image

def crop_and_split_img(img):
    coords = [
        (50, 40), (50, 90),
        (150, 40), (150, 90)
    ] # Change later.
    w = 50
    h = 50
    images = []
    for i in range(4):
        y, x = coords[i]
        y -= h // 2 # Coords are midpoint of the symbols.
        x -= w // 2
        images.append(img[y:h, x:w, :])
    return images, coords

def segment_image(img):
    return img

def get_characters(img):
    symbols, coords = crop_and_split_img(img)
    masks = []
    for symbol in symbols:
        thresh = get_threshold(symbol)
        mask = segment_image(img)
        masks.append(mask)
    return masks, coords

def reshape_masks(masks):
    resized_masks = []
    for mask in masks:
        reshaped = mask.reshape(mask.shape + (1,))
        padded = dataset_util.pad_image(reshaped)
        resized = dataset_util.resize_img(padded, config.SERIAL_INPUT_DIM[1:])
        repeated = np.repeat(resized.reshape(((1,) + config.SERIAL_INPUT_DIM[1:])), 3, axis=0)
        resized_masks.append(repeated)
    return np.array(resized_masks)

def get_symbols(img, model):
    masks = get_characters(img)
    masks = reshape_masks(masks)
    prediction = classifier.predict(model, masks)
    best_pred = classifier_util.get_best_prediction(prediction)
    return format_label([classifier.LABELS[p] for p in best_pred])
