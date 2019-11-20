from time import time, sleep
from numpy import array
import cv2
from debug import log
from config import LOG_DEBUG

LETTERS = {
    ".-"    : "a",
    "-..."  : "b",
    "-.-."  : "c",
    "-.."   : "d",
    "."     : "e",
    "..-."  : "f",
    "--."   : "g",
    "...."  : "h",
    ".."    : "i",
    ".---"  : "j",
    "-.-"   : "k",
    ".-.."  : "l",
    "--"    : "m",
    "-."    : "n",
    "---"   : "o",
    ".--."  : "p",
    "--.-"  : "q",
    ".-."   : "r",
    "..."   : "s",
    "-"     : "t",
    "..-"   : "u",
    "...-"  : "v",
    ".--"   : "w",
    "-..-"  : "x",
    "-.--"  : "y",
    "--.."  : "z"
}

WORDS = [ # Indexing is done using WORDS.index().
    "shell", "halls", "slick", "trick",
    "boxes", "leaks", "strobe", "bistro",
    "flick", "bombs", "break", "brick",
    "steak", "sting", "vector", "beats"
]

FREQUENCIES = [
    "3.505", "3.515", "3.522", "3.532",
    "3.535", "3.542", "3.545", "3.552",
    "3.555", "3.565", "3.572", "3.575",
    "3.582", "3.592", "3.595", "3.600"
]

def is_lit(pixel, rgb):
    lit_low = (40, 180, 180)
    lit_high = (100, 255, 255)
    red, green, blue = rgb
    return (red[pixel] >= lit_low[2] and green[pixel] >= lit_low[1]
            and blue[pixel] >= lit_low[0] and red[pixel] <= lit_high[2]
            and green[pixel] <= lit_high[1] and blue[pixel] <= lit_high[0])

def split_colors(img):
    blue = img[:, :, 0]
    green = img[:, :, 1]
    red = img[:, :, 2]
    return (red, green, blue)

def solve(img, screenshot_func):
    pixel = (43, 108)
    rgb = split_colors(img)

    dot_pause = 0.1 # 15 frames = 0.25 seconds.
    dash_pause = 0.6 # 47 frames ~ 0.75 seconds.
    letter_pause = 1 # 63 frames ~ 1 second
    word_pause = 2.5 # 194 frames ~ 3.3 seconds
    sleep_duration = 0.05
    duration = 0
    for _ in range(2): # Run twice to ensure the whole sequence of letters are recorded.
        lit = is_lit(pixel, rgb)
        checkpoint = time()
        letters = ""
        symbols = ""
        while True:
            sleep(sleep_duration)
            sc, _, _ = screenshot_func()
            rgb = split_colors(cv2.cvtColor(array(sc), cv2.COLOR_RGB2BGR)) # Grab new image.

            if is_lit(pixel, rgb) != lit: # Check if light has changed state.
                lit = not lit
                if lit:
                    duration = time() - checkpoint # Record length of gap.
                    checkpoint = time() # Record time of light being lit.

                    if duration >= word_pause:
                        letters += LETTERS[symbols]
                        log("=== END OF WORD ===", LOG_DEBUG, "Morse")
                        break
                    if duration >= letter_pause:
                        log("--- END OF LETTER ---", LOG_DEBUG, "Morse")
                        letter = LETTERS.get(symbols, '')
                        log(f"LETTER: {letter}", LOG_DEBUG, "Morse")
                        letters += letter
                        symbols = ""
                else:
                    duration = time() - checkpoint # Record length of flash.
                    checkpoint = time() # Record time of light being unlit.

                    if duration >= dash_pause:
                        symbols += "-"
                    elif duration >= dot_pause:
                        symbols += "."

    log(f"Word: {letters}", LOG_DEBUG, "Morse")
    # Return amount of times to press morse button.
    presses = WORDS.index(letters)
    return presses, FREQUENCIES[presses]
