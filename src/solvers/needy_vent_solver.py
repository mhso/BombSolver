import features.needy_vent as vent_features

def solve(img):
    chars = vent_features.get_characters(img)
    coords_yes = 222, 135
    coords_no = 222, 175
    return coords_yes if len(chars) < 9 else coords_no
