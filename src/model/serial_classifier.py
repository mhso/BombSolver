import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
import config

def build_model():
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3),
                     activation='relu',
                     input_shape=config.SERIAL_INPUT_DIM))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(config.SERIAL_OUTPUT_DIM, activation='softmax'))

    compile_model(model)
    model._make_predict_function()

    return model

def compile_model(model):
    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])

def train(model, inputs, expected_out):
    result = model.fit(inputs, expected_out, batch_size=config.SERIAL_BATCH_SIZE,
                       epochs=config.EPOCHS_PER_BATCH)
    return result.history

def evaluate(model, inputs, expected_out):
    score = model.evaluate(inputs, expected_out, verbose=0)
    return (score[0], score[1])

def predict(model, inp):
    return model.predict(inp)
