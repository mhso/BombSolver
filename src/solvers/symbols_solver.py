import features.symbols as symbols_features

def solve(image, model):
    symbols = symbols_features.get_symbols(image, model)
    return symbols
