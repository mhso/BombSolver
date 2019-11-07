from time import time, sleep

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

FREQUENCIES = [ # Indexing is done using .find.
    "shell", "halls", "slick", "trick", "boxes",
    "leaks", "strobe", "bistro", "flick",
    "bombs", "break", "brick", "steak", "steak",
    "sting", "vector", "beats"
]

def is_lit(pixel):
    lit = ((20, 170, 170), (50, 255, 255)) # TODO: Investigate actual value.
    blue = pixel[:, :, 0]
    green = pixel[:, :, 1]
    red = pixel[:, :, 2]
    if (red[pixel] >= lit[2] and green[pixel] >= lit[1]
            and blue[pixel] >= lit[0] and red[pixel] <= lit[2]
            and green[pixel] <= lit[1] and blue[pixel] <= lit[0]):
        return True
    return False

def solve(img):
    pixel = (30, 50) # Fix dis.
    unlit = ((30, 50, 120), (60, 75, 150)) # Actual = (40, 61, 133).

    dot_pause = 0.5 # TODO: Fix these variables.
    dash_pause = 1
    letter_pause = 2
    word_pause = 3
    for i in range(2): # Run twice to ensure the whole sequence of letters are recorded.
        lit = is_lit(pixel)
        checkpoint = time()
        letters = ""
        symbols = ""
        while True:
            sleep(0.05)
            if is_lit(pixel) != lit: # Check if light has changed state.
                lit = not lit
                if lit:
                    duration = time() - checkpoint # Record length of gap.
                    checkpoint = time() # Record time of light being lit.

                    if duration >= word_pause:
                        break
                    if duration >= letter_pause:
                        letters += LETTERS[symbols]
                        symbols = ""
                else:
                    duration = time() - checkpoint # Record length of flash.
                    checkpoint = time() # Record time of light being unlit.

                    if duration >= dash_pause:
                        symbols += "-"
                    elif duration >= dot_pause:
                        symbols += "."

    return FREQUENCIES.index(letters) # Return amount of times to press morse button.
