import features.whos_first as whos_features
from debug import log, LOG_DEBUG

STEP_1_SOLUTION = {
    "yes" : 2, "first" : 1, "display": 5, "okay" : 1,
    "says" : 5, "nothing" : 2, " " : 5, "blank" : 3,
    "no" : 5, "led" : 2, "lead" : 5, "read" : 3,
    "red" : 3, "reed" : 4, "leed" : 4, "holdon" : 5,
    "you" : 3, "youare" : 5, "your": 3, "youre" : 3,
    "ur": 0, "there" : 5, "theyre" : 4, "their": 3,
    "theyare" : 2, "see" : 5, "u" : 1, "cee" : 5
}

STEP_2_SOLUTION = {
    "ready" : [
        "yes", "okay", "what", "middle", "left",
        "press", "right", "blank", "ready", "no",
        "first", "uhhh", "nothing", "wait"
    ],
    "first" : [
        "left", "okay", "yes", "middle", "no",
        "right", "nothing", "uhhh", "wait",
        "ready", "blank", "what", "press", "first"
    ],
    "no" : [
        "blank", "uhhh", "wait", "first", "what",
        "ready", "right", "yes", "nothing", "left",
        "press", "okay", "no", "middle"
    ],
    "blank" : [
        "wait", "right", "okay", "middle", "blank",
        "press", "ready", "nothing", "no", "what",
        "left", "uhhh", "yes", "first"
    ],
    "nothing" : [
        "uhhh", "right", "okay", "middle", "yes",
        "blank", "no", "press", "Left", "what",
        "wait", "first", "nothing", "ready"
    ],
    "yes" : [
        "okay", "right", "uhhh", "middle", "first",
        "what", "press", "ready", "nothing", "yes",
        "left", "blank", "no", "wait"
    ],
    "what" : [
        "uhhh", "what", "left", "nothing", "ready",
        "blank", "middle", "no", "okay", "first",
        "wait", "yes", "press", "right"
    ],
    "uhhh" : [
        "ready", "nothing", "left", "what", "okay",
        "yes", "right", "no", "press", "blank",
        "uhhh", "middle", "wait", "first"
    ],
    "left" : [
        "right", "left", "first", "no", "middle",
        "yes", "blank", "what", "uhhh", "wait",
        "press", "ready", "okay", "nothing"
    ],
    "right" : [
        "yes", "nothing", "ready", "press", "no",
        "wait", "what", "right", "middle", "left",
        "uhhh", "blank", "okay", "first"
    ],
    "middle" : [
        "blank", "ready", "okay", "what", "nothing",
        "press", "no", "wait", "left", "middle",
        "right", "first", "uhhh", "yes"
    ],
    "okay" : [
        "middle", "no", "first", "yes", "uhhh",
        "nothing", "wait", "okay", "left", "ready",
        "blank", "press", "what", "right"
    ],
    "wait" : [
        "uhhh", "no", "blank", "okay", "yes",
        "left", "first", "press", "what", "wait",
        "nothing", "ready", "right", "middle"
    ],
    "press" : [
        "right", "middle", "yes", "ready", "press",
        "okay", "nothing", "uhhh", "blank", "left",
        "first", "what", "no", "wait"
    ],
    "you" : [
        "sure", "you are", "your", "you're", "next",
        "uh huh", "ur", "hold", "what?", "you",
        "uh uh", "like", "done", "u"
    ],
    "youare" : [
        "your", "next", "like", "uh huh", "what?",
        "done", "uh uh", "hold", "you", "u",
        "you're", "sure", "ur", "you are"
    ],
    "your" : [
        "uh uh", "you are", "uh huh", "your", "next",
        "ur", "sure", "u", "you're", "you",
        "what?", "hold", "like", "done"
    ],
    "youre" : [
        "you", "you're", "ur", "next", "uh uh",
        "you are", "u", "your", "what?", "uh huh",
        "sure", "done", "like", "hold"
    ],
    "ur" : [
        "done", "u", "ur", "uh huh", "what?",
        "sure", "your", "hold", "you're", "like",
        "next", "uh uh", "you are", "you"
    ],
    "u" : [
        "uh huh", "sure", "next", "what?", "you're",
        "ur", "uh uh", "done", "u", "you",
        "like", "hold", "you are", "your"
    ],
    "uhhuh" : [
        "uh huh", "your", "you are", "you", "done",
        "hold", "uh uh", "next", "sure", "like",
        "you're", "ur", "u", "what?"
    ],
    "uhuh" : [
        "ur", "u", "you are", "you're", "next",
        "uh uh", "done", "you", "uh huh", "like",
        "your", "sure", "hold", "what?"
    ],
    "what?" : [
        "you", "hold", "you're", "your", "u",
        "done", "uh uh", "like", "you are", "uh huh",
        "ur", "next", "what?", "sure"
    ],
    "done" : [
        "sure", "uh huh", "next", "what?", "your",
        "ur", "you're", "hold", "like", "you",
        "u", "you are", "uh uh", "done"
    ],
    "next" : [
        "what?", "uh huh", "uh uh", "your", "hold",
        "sure", "next", "like", "done", "you are",
        "ur", "you're", "u", "you"
    ],
    "hold" : [
        "you are", "u", "done", "uh uh", "you",
        "ur", "sure", "what?", "you're", "next",
        "hold", "uh huh", "your", "like"
    ],
    "sure" : [
        "youare", "done", "like", "youre", "you",
        "hold", "uhhuh", "ur", "sure", "u",
        "what?", "next", "your", "uhuh"
    ],
    "like" : [
        "youre", "next", "u", "ur", "hold",
        "done", "uhuh", "what?", "uhhuh", "you",
        "like", "sure", "you are", "your"
    ]
}

def solve(img, model):
    words, coords = whos_features.get_words(img, model)
    word_on_screen = words[0]
    words = words[1:]
    log(f"Word on screen: {word_on_screen}", LOG_DEBUG, "Who's On First?")
    log(f"Words on labels: {words}", LOG_DEBUG, "Who's On First?")

    step_1 = STEP_1_SOLUTION.get(word_on_screen, None)
    if step_1 is None:
        return step_1
    step_2_words = STEP_2_SOLUTION.get(words[step_1], None)
    if step_2_words is None:
        return step_2_words

    for word in step_2_words:
        if word in words:
            return coords[words.index(words)]
    return None
