import features.util as features_util

def crop_image(img):
    min_y, min_x, max_y, max_x = 48, 128, 68, 178
    return img[min_y:max_y, min_x:max_x]

def is_active(img):
    cropped = crop_image(img)
    h, w = cropped.shape
    y = h/2
    step_x = w // 12
    start_x = (w // 10)
    min_red = (170, 0, 0)
    max_red = (255, 70, 70)
    rgb = features_util.split_channels(cropped)
    threshold = 5
    amount = 0
    for i in range(1, 11):
        x = start_x + i * step_x
        pixel = (y, x)
        if features_util.color_in_range(pixel, rgb, min_red, max_red):
            amount += 1
            if amount == threshold:
                return True
    return False
