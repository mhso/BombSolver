from sys import argv
import model.serial_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import model.serial_dataset as dataset
from debug import log
import config

def calculate_accuracy(model, test_x, test_y):
    return classifier.evaluate(model, test_x, test_y)[1]

def train_network(model, train_x, train_y, test_x, test_y, steps=50):
    for i in range(steps):
        sample_images, sample_labels = dataset_util.sample_data(train_x, train_y, config.SERIAL_BATCH_SIZE)
        result = classifier.train(MODEL, sample_images, sample_labels)
        acc = calculate_accuracy(MODEL, test_x, test_y)
        model_acc = result['val_acc'][-1]*100
        model_loss = result['val_loss'][-1]
        save_string = ""
        if i % 10 == 0:
            path = "../resources/trained_models/model"
            classifier_util.save_to_file(model, path)
            save_string = " - Saving model to file..."
        print(f"Step {i+1}/{steps} - Real acc: {acc:.3f}% - "
              + f"Training acc: {model_acc:.3f}% - Model loss: {model_loss}{save_string}")

x_train, y_train, x_test, y_test = dataset.load_dataset()

MODEL = None
FILE_PATH = "../resources/trained_models/serial_model"
if classifier_util.model_exists(FILE_PATH) and "train" not in argv:
    log("Loading Neural Network from file...")
    MODEL = classifier_util.load_from_file(FILE_PATH)
    classifier.compile_model(MODEL)
else:
    log("Building Neural Network model...")
    MODEL = classifier.build_model()

    #classifier.save_as_image(model)
    log("Training network...")
    train_network(MODEL, x_train, y_train, x_test, y_test)

if not classifier_util.model_exists(FILE_PATH):
    log("Saving model to file...")
    classifier_util.save_to_file(MODEL, FILE_PATH)
