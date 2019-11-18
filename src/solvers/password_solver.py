from time import sleep
import features.password as password_features
import features.util as features_util

PASSWORDS = [
    "about", "after", "again", "below", "could",
    "every", "first", "found", "great", "house",
    "large", "learn", "never", "other", "place",
    "plant", "point", "right", "small", "house",
    "spell", "still", "study", "their", "there",
    "these", "things", "think", "three", "water",
    "where", "which", "world", "would", "write"
]

def word_matching_prefix(prefix):
    for word in PASSWORDS:
        if word.startswith(prefix):
            return word
    return None

def get_next_char(index, click_func):
    start_x = 64
    offset = 42
    x = start_x + index * offset
    y = 216 # 216 = down, 70 = up.
    click_func(x, y)
    sleep(0.3)

def solve(img, sc_func, click_func):
    index = 1
    attemped_words = set()
    while True: # DFS-ish traversal of possible passwords.
        characters = password_features.get_characters(img)
        match = word_matching_prefix(characters[:index])
        if match is not None and match not in attemped_words:
            if index == 5:
                return True # Match found.
            attemped_words.add(match)
            index += 1
        else:
            index -= 1
        get_next_char(index, click_func)
        sc = sc_func()[0]
        img = features_util.convert_to_cv2(sc)
    return False
