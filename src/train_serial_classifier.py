from sys import argv
import model.serial_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import model.serial_dataset as dataset
from keras.utils import to_categorical
from debug import log
from numpy import where, array
import cv2

def calculate_accuracy(model, test_x, test_y):
    return classifier.evaluate(model, test_x, test_y)[1] * 100

def train_network(model, train_x, train_y, test_x, test_y, steps=500):
    for i in range(steps):
        sample_images, sample_labels = dataset_util.sample_data(train_x, train_y, classifier.BATCH_SIZE)
        result = classifier.train(MODEL, sample_images, sample_labels)
        acc = calculate_accuracy(MODEL, test_x, test_y)
        model_acc = result['acc'][-1]*100
        model_loss = result['loss'][-1]
        save_string = ""
        if i % 20 == 0:
            path = "../resources/trained_models/serial_model"
            classifier_util.save_to_file(model, path)
            save_string = " - Saving model to file..."
        print(f"Step {i+1}/{steps} - Real acc: {acc:.3f}% - "
              + f"Training acc: {model_acc:.3f}% - Model loss: {model_loss}{save_string}")

def visualize(x, y):
    cv2.namedWindow("Test")
    for i in range(x.shape[0]):
        img = array(x[i])
        label = where(y[i] == 1)
        img = img.reshape((28, 28, 3))
        print(label)
        cv2.imshow("Test", img)
        key = cv2.waitKey(0)
        if key == ord('q'):
            break

"""
data_amount = 20000
x_train_l, y_train_l, x_test_l, y_test_l = dataset.load_emnist_letters(data_amount)
x_train_d, y_train_d, x_test_d, y_test_d = dataset.load_emnist_digits(data_amount)
x_train, y_train, x_test, y_test = dataset.merge_datasets((x_train_l, y_train_l, x_test_l, y_test_l),
                                                          (x_train_d, y_train_d, x_test_d, y_test_d))
"""

x_train, y_train, x_test, y_test = dataset.load_dataset()
print(f"Loaded {len(x_train)} training datapoints.")
print(f"Loaded {len(x_test)} testing datapoints.")

MODEL = None
FILE_PATH = "../resources/trained_models/serial_model"
if classifier_util.model_exists(FILE_PATH) and "train" not in argv:
    log("Loading Neural Network from file...")
    MODEL, _, _ = classifier.load_from_file(FILE_PATH)
    classifier.compile_model(MODEL)
else:
    log("Building Neural Network model...")
    MODEL, _, _ = classifier.build_model()

    log("Training network...")
    train_network(MODEL, x_train, y_train, x_test, y_test)

log("Saving model to file...")
classifier_util.save_to_file(MODEL, FILE_PATH)
