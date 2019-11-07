import config

def log(arg, verbose=0):
    if config.VERBOSITY >= verbose:
        print(f"[BombSolver] - {arg}")
