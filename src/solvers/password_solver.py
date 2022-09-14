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
    attempted_prefixes = {} # Keep track of attempts for word prefixes.
    prev_search_word = "" # This is just for logging.
    password_found = False

    while True: # DSF-ish traversal of possible passwords.
        characters = password_features.get_password(img, model) # Get current set of characters.
        match = word_matching_prefix(characters[:index]) # Get a word that matches current prefix.
        attempt_prefix = characters[:index-1]
        attempts = get_attempts(attempt_prefix, attempted_prefixes)

        if attempts > 5: # No matching word was found with the current prefix.
            index -= 1 # Go back to the previous letter and change it.

        while match is not None: # Move through letters until prefix no longer matches or full password is found.
            if match != prev_search_word:
                log(f"Attempting to write '{match}'", LOG_DEBUG, "Password")

            prev_search_word = match

            if index == 5: # We have found a full matching word with 5 letters.
                password_found = True
                break

            index += 1 # Move to next letter.
            match = word_matching_prefix(characters[:index]) # Get new match for longer prefix.

        if index == 0 or password_found: # No password was found.
            break

        if attempts == 0:
            attempted_prefixes[attempt_prefix] = 1
        else:
            attempted_prefixes[attempt_prefix] += 1

        # Cycle to next letter for the current index.
        get_next_char(index-1, click_func)
        sc = sc_func()[0]

        img = features_util.convert_to_cv2(sc)

        yield False

    yield password_found
