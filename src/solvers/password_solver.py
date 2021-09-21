from time import sleep
import features.password as password_features
import features.util as features_util
from debug import log, LOG_DEBUG

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
    attempted_words = {}
    prev_search_word = "" # This is just for logging.
    while True: # DSF-ish traversal of possible passwords.
        characters = password_features.get_password(img, model)
        match = word_matching_prefix(characters[:index])
        attemp_prefix = characters[:index-1]
        attempts = get_attempts(attemp_prefix, attempted_words)
        if attempts > 5:
            index -= 1
        while match is not None:
            if match != prev_search_word:
                log(f"Attempting to write '{match}'", LOG_DEBUG, "Password")
            prev_search_word = match
            if index == 5:
                return True # Match found.
            index += 1
            match = word_matching_prefix(characters[:index])
        if index == 0: # No passwords were found.
            break
        if attempts == 0:
            attempted_words[attemp_prefix] = 1
        else:
            attempted_words[attemp_prefix] += 1
        get_next_char(index-1, click_func)
        sc = sc_func()[0]

        img = features_util.convert_to_cv2(sc)
    return False
