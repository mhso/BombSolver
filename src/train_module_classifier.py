from sys import argv
import numpy as np
import model.module_classifier as classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import model.module_dataset as dataset
from debug import log

def train_network(model, train_images, train_labels, test_images, test_labels, steps=500):
    for i in range(steps):
        sample_images, sample_labels = dataset_util.sample_data(train_images, train_labels, classifier.BATCH_SIZE)
        result = classifier.train(model, sample_images, sample_labels)
        acc = classifier.evaluate(model, test_images, test_labels)[1] * 100
        #acc = calculate_accuracy(model, test_images, test_labels)
        model_acc = result['val_acc'][-1]*100
        model_loss = result['val_loss'][-1]
        save_string = ""
        if i % 10 == 0:
            path = "../resources/trained_models/module_model"
            classifier_util.save_to_file(model, path)
            save_string = " - Saving model to file..."
        print(f"Step {i+1}/{steps} - Real acc: {acc:.3f}% - "
              + f"Training acc: {model_acc:.3f}% - Model loss: {model_loss}{save_string}")

def calculate_accuracy(model, images, labels):
    correct = 0
    for i in range(images.shape[0]):
        label = np.where(labels[i] == 1)[0]
        predict = classifier.predict(model, images[i])
        predict_label = classifier_util.get_best_prediction(predict)[0]
        if predict_label == label[0]:
            correct += 1
    return (correct/images.shape[0])*100

log("Loading dataset...")
train_images, train_labels, test_images, test_labels = dataset.load_dataset()
log(f"{train_images.shape[0]} data points loaded.")

MODEL = None
FILE_PATH = "../resources/trained_models/module_model"
if classifier_util.model_exists(FILE_PATH) and "train" not in argv:
    log("Loading Neural Network from file...")
    MODEL = classifier.load_from_file(FILE_PATH)
    classifier.compile_model(MODEL)
else:
    log("Building Neural Network model...")
    MODEL, _, _ = classifier.build_model()

    #classifier.save_as_image(model)
    log("Training network...")
    train_network(MODEL, train_images, train_labels, test_images, test_labels)

log("Saving model to file...")
classifier_util.save_to_file(MODEL, FILE_PATH)
