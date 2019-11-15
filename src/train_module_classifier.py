from sys import argv
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
        model_acc = result['val_acc'][-1]*100
        model_loss = result['val_loss'][-1]
        save_string = ""
        if i % 10 == 0:
            path = "../resources/trained_models/module_model"
            classifier_util.save_to_file(model, path)
            save_string = " - Saving model to file..."
        print(f"Step {i+1}/{steps} - Real acc: {acc:.3f}% - "
              + f"Training acc: {model_acc:.3f}% - Model loss: {model_loss}{save_string}")

log("Loading dataset...")
train_images, train_labels, test_images, test_labels = dataset.load_dataset()
log(f"{train_images.shape[0]} data points loaded.")

FILE_PATH = "../resources/trained_models/module_model"
log("Building Neural Network model...")
MODEL, _, _ = classifier.build_model()

#classifier.save_as_image(model)
log("Training network...")
train_network(MODEL, train_images, train_labels, test_images, test_labels)

log("Saving model to file...")
classifier_util.save_to_file(MODEL, FILE_PATH)
