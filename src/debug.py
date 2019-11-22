import config

def log(arg, verbose=0, module="BombSolver"):
    if config.VERBOSITY >= verbose:
        print(f"[{module}] - {arg}")

LOG_DEBUG = config.LOG_DEBUG
LOG_WARNING = config.LOG_WARNING
