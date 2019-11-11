def color_in_range(pixel, rgb, lo_rgb, hi_rgb):
    red, green, blue = rgb
    return (red[pixel] >= lo_rgb[0] and green[pixel] >= lo_rgb[1]
            and blue[pixel] >= lo_rgb[2] and red[pixel] <= hi_rgb[0]
            and green[pixel] <= hi_rgb[1] and blue[pixel] <= hi_rgb[2])

def split_channels(img_bgr):
    blue = img_bgr[:, :, 0]
    green = img_bgr[:, :, 1]
    red = img_bgr[:, :, 2]
    return (red, green, blue)
