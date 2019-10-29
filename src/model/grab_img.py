import cv2
from PIL import ImageGrab, Image

def screenshot(x, y, w, h):
    img = ImageGrab.grab((x, y, x + w, y + h))
    return img

def load_test_images():
    images = []
    for i in range(12):
        images.append(Image.open(f"../resources/{i:03d}.png"))
    return images
