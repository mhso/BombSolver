from debug import log
from features.button import get_button_features

def solve_button(img, features, model):
    text, color = get_button_features(img, model)
    print(f"Button text: {text}, color: {color}")
