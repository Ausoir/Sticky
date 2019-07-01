import random


# Sync'ed random
class Random:
    seed = 123

    @staticmethod
    def init(seed):
        Random.seed = seed
        random.seed(seed)

    @staticmethod
    def get_instance(seed):
        return random.Random(seed)

    @staticmethod
    def rand_bool():
        return random.randint(0, 1)

    @staticmethod
    def rand_float():
        return random.random()

    @staticmethod
    def rand_int(arg1, arg2):
        return random.randint(arg1, arg2)

    @staticmethod
    def rand_seed():
        return random.SystemRandom().randint(1, 999999)

    @staticmethod
    def gauss(arg1, arg2):
        return random.gauss(arg1, arg2)
