import config

def log(arg, verbose=0, module=None):
    prefix = "BombSolver" if module is None else module
    if config.VERBOSITY >= verbose:
        print(f"[{prefix}] - {arg}")

LOG_DEBUG = config.LOG_DEBUG
LOG_WARNING = config.LOG_WARNING
