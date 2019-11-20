PASSWORDS = [
    "about", "after", "again", "below", "could",
    "every", "first", "found", "great", "house",
    "large", "learn", "never", "other", "place",
    "plant", "point", "right", "small", "house",
    "spell", "still", "study", "their", "there",
    "these", "things", "think", "three", "water",
    "where", "which", "world", "would", "write"
]

CHARACTERS = [
    ["h", "e", "z", "m", "l"],
    ["o", "o", "u", "i", "n"],
    ["j", "t", "p", "b", "s"],
    ["m", "q", "j", "t", "x"],
    ["d", "w", "f", "c", "c"],
    ["p", "b", "b", "s", "e"]
]

CHAR_INDEXES = [3, 0, 4, 0, 2]

def word_matching_prefix(prefix):
    for word in PASSWORDS:
        if word.startswith(prefix):
            return word
    return None

def get_characters():
    return "".join([CHARACTERS[x][i] for i, x in enumerate(CHAR_INDEXES)])

def get_next_char(index):
    CHAR_INDEXES[index] += 1
    if CHAR_INDEXES[index] == 6:
        CHAR_INDEXES[index] = 0
    return get_characters()

def get_attempts(prefix, attemped_words):
    return attemped_words.get(prefix, 0)

def solve():
    index = 1
    attempted_words = {}
    while True: # DSF-ish traversal of possible passwords.
        characters = get_characters()
        print(characters)
        match = word_matching_prefix(characters[:index])
        attemp_prefix = characters[:index-1]
        attempts = get_attempts(attemp_prefix, attempted_words)
        if match is not None:
            if index == 5:
                return True # Match found.
            index += 1
        elif attempts > 4:
            index -= 1
        if index == 0: # No passwords were found.
            break
        if attempts == 0:
            attempted_words[attemp_prefix] = 1
        else:
            attempted_words[attemp_prefix] += 1
        get_next_char(index-1)
    return False

print(solve())
