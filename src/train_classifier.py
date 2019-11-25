from sys import argv
import cv2
import model.module_classifier as module_classifier
import model.character_classifier as character_classifier
import model.symbol_classifier as symbol_classifier
import model.classifier_util as classifier_util
import model.dataset_util as dataset_util
from model.progress_bar import Progress
import config
from debug import log

def train_network(model, classifier, path, train_x, train_y, test_x, test_y, steps=400):
    prog = Progress(steps)
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
        prog.status = (f"Step {i+1}/{steps} - Real acc: {acc:.3f}% - "
                       + f"Training acc: {model_acc:.3f}% - Model loss: "
                       + f"{model_loss}{save_string}")
        prog.increment()

def test_network(model, classifier, test_x, test_y):
    for (image, label) in zip(test_x, test_y):
        prediction = classifier.predict(model, image)
        best_pred = classifier_util.get_best_prediction(prediction)[0]
        label_num = classifier_util.get_best_prediction(label.reshape((1, -1)))[0]
        print(f"Label: {classifier.LABELS[label_num]} - Prediction: {classifier.LABELS[best_pred]}")
        cv2.imshow("Test", image.reshape(image.shape[1:] + (3,)))
        key = cv2.waitKey(0)
        if key == ord('q'):
            return
        cv2.destroyWindow("Test")

MODEL_SPECIFIC_VALUES = {
    "modules" : (
        module_classifier,
        [x for x in range(config.MODULE_OUTPUT_DIM)],
        (config.MODULE_INPUT_DIM, config.MODULE_OUTPUT_DIM)
    ),
    "characters" : (
        character_classifier,
        [x for x in range(10)] + [chr(x) for x in range(97, 123)],
        (config.CHAR_INPUT_DIM, config.CHAR_OUTPUT_DIM)
    ),
    "symbols" : (
        symbol_classifier,
        [x for x in range(config.SYMBOLS_OUTPUT_DIM)],
        (config.SYMBOLS_INPUT_DIM, config.SYMBOLS_OUTPUT_DIM)
    )
}

if len(argv) == 1 or not MODEL_SPECIFIC_VALUES.get(argv[1], False):
    print("Please provide a valid dataset type to train on.")
    print(f"Possible types: {[x for x in MODEL_SPECIFIC_VALUES]}")
    exit(0)

DATA_TYPE = argv[1]
DATASET_PATH = f"../resources/labeled_images/{DATA_TYPE}/"
MODEL_PATH = f"../resources/trained_models/{DATA_TYPE[:-1]}_model"

CLASSIFIER, LABEL_NAMES, DATA_DIMS = MODEL_SPECIFIC_VALUES[DATA_TYPE]

log("Loading dataset...")
X_TRAIN, Y_TRAIN, X_TEST, Y_TEST = dataset_util.load_dataset(
    DATASET_PATH, LABEL_NAMES, DATA_DIMS, CLASSIFIER.TESTS_PER_LABEL
)
log(f"Training datapoints: {len(X_TRAIN)}.")
log(f"Testing datapoints:  {len(X_TEST)}.")

if len(argv) > 2 and argv[2] == "test":
    MODEL = CLASSIFIER.load_from_file(MODEL_PATH)
    test_network(MODEL, CLASSIFIER, X_TEST, Y_TEST)
else:
    log("Building Neural Network model...")
    MODEL, _, _ = CLASSIFIER.build_model()

    log("Training network...")
    STEPS = 500 if DATA_TYPE == "modules" else 200
    train_network(MODEL, CLASSIFIER, MODEL_PATH, X_TRAIN, Y_TRAIN, X_TEST, Y_TEST, STEPS)

    log("Saving model to file...")
    classifier_util.save_to_file(MODEL, MODEL_PATH)
