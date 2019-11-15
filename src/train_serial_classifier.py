from sys import argv
import model.serial_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import model.serial_dataset as dataset
from debug import log

def train_network(model, train_x, train_y, test_x, test_y, steps=500):
    for i in range(steps):
        sample_images, sample_labels = dataset_util.sample_data(train_x, train_y, classifier.BATCH_SIZE)
        result = classifier.train(MODEL, sample_images, sample_labels)
        acc = classifier.evaluate(model, test_x, test_y)[1] * 100
        model_acc = result['acc'][-1]*100
        model_loss = result['loss'][-1]
        save_string = ""
        if i % 20 == 0:
            path = "../resources/trained_models/serial_model"
            classifier_util.save_to_file(model, path)
            save_string = " - Saving model to file..."
        print(f"Step {i+1}/{steps} - Real acc: {acc:.3f}% - "
              + f"Training acc: {model_acc:.3f}% - Model loss: {model_loss}{save_string}")

x_train, y_train, x_test, y_test = dataset.load_dataset()
print(f"Loaded {len(x_train)} training datapoints.")
print(f"Loaded {len(x_test)} testing datapoints.")

FILE_PATH = "../resources/trained_models/serial_model"
log("Building Neural Network model...")
MODEL, _, _ = classifier.build_model()

log("Training network...")
train_network(MODEL, x_train, y_train, x_test, y_test)

log("Saving model to file...")
classifier_util.save_to_file(MODEL, FILE_PATH)
