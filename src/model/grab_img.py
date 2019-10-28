from PIL import ImageGrab

def screenshot(x, y, w, h):
    img = ImageGrab.grab((x, y, x + w, y + h))
    return img
