import random


# Sync'ed random
class Random:
    seed = 123

    @staticmethod
    def init(seed):
        Random.seed = seed
        random.seed(seed)

    @staticmethod
    def rand_bool():
        return random.randint(0, 1)

    @staticmethod
    def rand_int(arg1, arg2):
        return random.randint(arg1, arg2)

    @staticmethod
    def rand_seed():
        return Random.rand_int(1, 99999)

    @staticmethod
    def gauss(arg1, arg2):
        return random.gauss(arg1, arg2)
