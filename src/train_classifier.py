from sys import argv
import model.module_classifier as module_classifier
import model.character_classifier as character_classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
import config
from debug import log

def train_network(model, classifier, path, train_x, train_y, test_x, test_y, steps=500):
    for i in range(steps):
        sample_images, sample_labels = dataset_util.sample_data(train_x, train_y, classifier.BATCH_SIZE)
        result = classifier.train(model, sample_images, sample_labels)
        acc = classifier.evaluate(model, test_x, test_y)[1] * 100
        model_acc = result['acc'][-1]*100
        model_loss = result['loss'][-1]
        save_string = ""
        if i % 20 == 0:
            classifier_util.save_to_file(model, path)
            save_string = " - Saving model to file..."
        print(f"Step {i+1}/{steps} - Real acc: {acc:.3f}% - "
              + f"Training acc: {model_acc:.3f}% - Model loss: {model_loss}{save_string}")

MODEL_SPECIFIC_VALUES = {
    "modules" : (
        module_classifier,
        [x for x in range(config.OUTPUT_DIM)],
        (config.INPUT_DIM, config.OUTPUT_DIM)
    ),
    "characters" : (
        character_classifier,
        [x for x in range(10)] + [chr(x) for x in range(97, 123)],
        (config.SERIAL_INPUT_DIM, config.SERIAL_OUTPUT_DIM)
    )
}

if len(argv) == 1 or not MODEL_SPECIFIC_VALUES.get(argv[1], False):
    print("Please provide a valid dataset type to train on.")
    print(f"Possible types: {[x for x in MODEL_SPECIFIC_VALUES]}")
    exit(0)

DATA_TYPE = argv[1]
DATASET_PATH = f"../resources/labeled_images/{DATA_TYPE}/"

CLASSIFIER, LABEL_NAMES, DATA_DIMS = MODEL_SPECIFIC_VALUES[DATA_TYPE]

log("Loading dataset...")
X_TRAIN, Y_TRAIN, X_TEST, Y_TEST = dataset_util.load_dataset(
    DATASET_PATH, LABEL_NAMES, DATA_DIMS
)
log(f"Training datapoints: {len(X_TRAIN)}.")
log(f"Testing datapoints:  {len(X_TEST)}.")

log("Building Neural Network model...")
MODEL, _, _ = CLASSIFIER.build_model()

log("Training network...")
FILE_PATH = f"../resources/trained_models/{DATA_TYPE[:-1]}_model"
train_network(MODEL, CLASSIFIER, FILE_PATH, X_TRAIN, Y_TRAIN, X_TEST, Y_TEST)

log("Saving model to file...")
classifier_util.save_to_file(MODEL, FILE_PATH)
