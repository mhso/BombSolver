import features.symbols as symbols_features

COLUMNS = [
    [0, 1, 2, 3, 4, 5, 6],
    [7, 0, 6, 8, 9, 5, 10],
    [11, 12, 8, 13, 14, 2, 9],
    [15, 16, 17, 4, 13, 10, 18],
    [20, 18, 17, 21, 16, 22, 23],
    [15, 7, 24, 25, 20, 26, 27]
]

def solve(image, model):
    symbols, coords = symbols_features.get_symbols(image, model)
    column = 0
    for i in range(6):
        if set(symbols).issubset(COLUMNS[i]):
            column = i
            break
    try:
        zipped = sorted(zip(symbols, coords), key=lambda a: COLUMNS[column].index(a[0]))
        return [c for (s, c) in zipped]
    except ValueError:
        return None
