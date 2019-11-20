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

def get_attempts(prefix, attemped_words):
    return attemped_words.get(prefix, 0)

def solve(img, model, sc_func, click_func):
    index = 1
    attemped_words = {}
    while True: # DSF-ish traversal of possible passwords.
        characters = password_features.get_password(img, model)
        match = word_matching_prefix(characters[:index])
        attempts = get_attempts(match[:-1], attemped_words)
        if match is not None and attempts < 5:
            if index == 5:
                return True # Match found.
            if attempts == 0:
                attemped_words[match[-1]] = 1
            else:
                attemped_words[match[-1]] += 1
            index += 1
        else:
            index -= 1
        if index == 0: # No passwords were found.
            break
        get_next_char(index-1, click_func)
        sc = sc_func()[0]
        img = features_util.convert_to_cv2(sc)
    return False
