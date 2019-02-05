import os


def get_real_elapsed_time() -> float:
    # TODO: this works only on linux
    return os.times()[4]
