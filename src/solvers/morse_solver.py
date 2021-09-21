from time import time, sleep
from numpy import array
import cv2
from debug import log
from config import LOG_DEBUG
from features import util as features_util

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

WORDS = [ # Ordered by frequencies.
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

def get_word_from_substring(substr):
    """
    Returns index of the word that contains the given substring,
    or None if there are zero, or more than one, of such matches.
    """
    matches = 0
    index = 0
    for i, word in enumerate(WORDS):
        if word.find(substr) != -1:
            matches += 1
            index = i
    return index if matches == 1 else None

def get_word_from_prefix(prefix):
    """
    Returns index of the word that starts with the given prefix,
    or None if there are zero, or more than one, of such matches.
    """
    matches = 0
    index = 0
    for i, word in enumerate(WORDS):
        if word.startswith(prefix):
            matches += 1
            index = i
    return index if matches == 1 else None

def is_lit(pixel, rgb):
    lit_low = (180, 180, 40)
    lit_high = (255, 255, 100)
    return features_util.color_in_range(pixel, rgb, lit_low, lit_high)

def solve(img, screenshot_func):
    pixel = (43, 108)
    rgb = features_util.split_channels(img)

    dot_pause = 0.1 # 15 frames = 0.25 seconds.
    dash_pause = 0.6 # 47 frames ~ 0.75 seconds.
    letter_pause = 1 # 63 frames ~ 1 second
    word_pause = 2.5 # 194 frames ~ 3.3 seconds
    sleep_duration = 0.05
    duration = 0
    solved_from_substr = False
    for i in range(2): # Run twice to ensure the whole sequence of letters are recorded.
        if solved_from_substr:
            log("Solved Morse in first round!", LOG_DEBUG, "Morse")
            break
        lit = is_lit(pixel, rgb)
        checkpoint = time()
        letters = ""
        symbols = ""
        while True:
            sleep(sleep_duration)
            screenshot, _, _ = screenshot_func()
            rgb = features_util.split_channels(cv2.cvtColor(array(screenshot), cv2.COLOR_RGB2BGR))

            if is_lit(pixel, rgb) != lit: # Check if light has changed state.
                lit = not lit
                if lit:
                    duration = time() - checkpoint # Record length of gap.
                    checkpoint = time() # Record time of light being lit.

                    if duration >= letter_pause:
                        letter = LETTERS.get(symbols, '')
                        log(f"LETTER: {letter}", LOG_DEBUG, "Morse")
                        letters += letter
                        if i == 0 and len(letters) > 1 and get_word_from_substring(letters[1:]) is not None:
                            # Terminate if we can already guess from a substring of the word.
                            solved_from_substr = True # Indicate word was solved in first round.
                            break
                        if i == 1 and get_word_from_prefix(letters) is not None:
                            break # Terminate if we can already guess from a prefix of the word.
                        symbols = ""
                    if duration >= word_pause:
                        pos_str = "START" if i == 0 else "END"
                        log(f"=== {pos_str} OF WORD ===", LOG_DEBUG, "Morse")
                        break
                else:
                    duration = time() - checkpoint # Record length of flash.
                    checkpoint = time() # Record time of light being unlit.

                    if duration >= dash_pause:
                        symbols += "-"
                    elif duration >= dot_pause:
                        symbols += "."

    # Return amount of times to press morse button.
    presses = (
        get_word_from_substring(letters[1:]) if solved_from_substr
        else get_word_from_prefix(letters)
    )
    log(f"Word: {WORDS[presses]}", LOG_DEBUG, "Morse")
    return presses, FREQUENCIES[presses]
