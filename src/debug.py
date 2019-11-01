import config

def log(arg, verbosity_level=0):
    if config.VERBOSITY >= verbosity_level:
        print(f"[BombSolver] - {arg}")
