import random

mersenne8 = 2**31-1
multiplier = 48271


def NewStdRandom(seed):
    return random.seed(seed)

def Next(random):
    return random*multiplier % mersenne8

