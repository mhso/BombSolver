import matplotlib.pyplot as plt

def plot_prediction(image, prediction):
    fig = plt.figure()
    a = fig.add_subplot(1, 2, 1)
    plt.imshow(image)
    a.set_title("Image")
    b = fig.add_subplot(1, 2, 2)
    x = [i+1 for i in range(prediction.shape[0])]
    prediction[prediction < 0] = 0
    b.bar(x, prediction)
    b.set_title("Predictions")
    plt.show()
