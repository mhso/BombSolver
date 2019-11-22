import features.symbols as symbols_features

COLUMNS = [ # Each column is listed in the order they appear in the manual.
    [0, 1, 2, 3, 4, 5, 6],
    [7, 0, 6, 8, 9, 5, 10],
    [11, 12, 8, 13, 14, 2, 9],
    [15, 16, 17, 4, 13, 10, 18],
    [19, 18, 17, 20, 16, 21, 22],
    [15, 7, 23, 24, 19, 25, 26]
]

def solve(image, model):
    symbols, coords = symbols_features.get_symbols(image, model)
    column = 0
    for i in range(6):
        # Find the column where every symbol can be found within it.
        if set(symbols).issubset(COLUMNS[i]):
            column = i
            break
    # Sort the symbols and coords by the indexes of the symbols within their given column.
    zipped = sorted(zip(symbols, coords), key=lambda a: COLUMNS[column].index(a[0]))
    return [c for (s, c) in zipped]
