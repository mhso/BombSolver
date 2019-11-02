from sys import argv
import numpy as np
import cv2
import model.module_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import model.module_dataset as dataset
from view.graphs import plot_prediction
import config
from debug import log

def train_network(model, train_images, train_labels, test_images, test_labels, steps=500):
    for i in range(steps):
        sample_images, sample_labels = dataset_util.sample_data(train_images, train_labels, config.MODULE_BATCH_SIZE)
        result = classifier.train(MODEL, sample_images, sample_labels)
        acc = calculate_accuracy(MODEL, test_images, test_labels)
        model_acc = result['val_acc'][-1]*100
        model_loss = result['val_loss'][-1]
        save_string = ""
        if i % 10 == 0:
            path = "../resources/trained_models/model"
            classifier_util.save_to_file(model, path)
            save_string = " - Saving model to file..."
        print(f"Step {i+1}/{steps} - Real acc: {acc:.3f}% - "
              + f"Training acc: {model_acc:.3f}% - Model loss: {model_loss}{save_string}")

def extract_test_data(images, labels):
    test_images = []
    test_labels = []
    indexes = []
    train_images = [x for x in images]
    train_labels = [y for y in labels]
    i = 0
    curr_label = 0
    while len(test_images) < config.OUTPUT_DIM:
        label = np.where(labels[i] == 1)[0]
        while label < curr_label:
            i += 1
            label = np.where(labels[i] == 1)[0]
        curr_label += 1
        test_labels.append(labels[i])
        test_images.append(images[i])
        indexes.append(i)
    for index in reversed(indexes):
        train_images.pop(index)
        train_labels.pop(index)
    return (np.array(train_images), np.array(train_labels),
            np.array(test_images), np.array(test_labels))

def calculate_accuracy(model, images, labels):
    correct = 0
    for i in range(images.shape[0]):
        label = np.where(labels[i] == 1)[0]
        predict = classifier.predict(model, images[i])
        predict_label = classifier.get_best_prediction(predict)[0]
        if predict_label == label[0]:
            correct += 1
    return (correct/images.shape[0])*100

log("Loading dataset...")
train_images, train_labels, test_images, test_labels = dataset.load_dataset()
log(f"{images.shape[0]} data points loaded.")

MODEL = None
FILE_PATH = "../resources/trained_models/model"
if classifier_util.model_exists(FILE_PATH) and "train" not in argv:
    log("Loading Neural Network from file...")
    MODEL = classifier_util.load_from_file(FILE_PATH)
    classifier.compile_model(MODEL)
else:
    log("Building Neural Network model...")
    MODEL = classifier.build_model()

    #classifier.save_as_image(model)
    log("Training network...")
    train_network(MODEL, train_images, train_labels, test_images, test_labels)

if not classifier_util.model_exists(FILE_PATH):
    log("Saving model to file...")
    classifier_util.save_to_file(MODEL, FILE_PATH)

if "test" in argv:
    for i in range(test_images.shape[0]):
        label = np.where(labels[i] == 1)[0]
        max_index = -1
        max_val = 0
        predict = classifier.predict(MODEL, test_images[i])
        predict_label = classifier.get_best_prediction(predict)[0]
        print(f"Predicted: {predict_label} ({config.LABELS[predict_label]})")
        img = cv2.cvtColor(test_images[i].reshape((64, 64, 3)).astype("uint8"), cv2.COLOR_BGR2RGB)
        plot_prediction(cv2.resize(img, (256, 256), interpolation=cv2.INTER_AREA), predict[0])
