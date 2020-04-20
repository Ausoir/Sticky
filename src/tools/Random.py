import math
import random


# Sync'ed random
class Random:
    def __init__(self, seed=0):
        if not seed:
            self.seed = Random.rand_seed()
        else:
            self.seed = seed
        self.random = random.Random(self.seed)

    def reset(self, seed):
        self.random = random.Random(seed)

    def rand_rand(self):
        return Random(self.rand_int(0, 999999))

    def rand_bool(self):
        return self.random.randint(0, 1)

    def rand_float(self):
        return self.random.random()

    def rand_int(self, arg1, arg2):
        if arg1 == arg2:
            return arg1
        return self.random.randint(arg1, arg2)

    def gauss(self, arg1, arg2):
        return self.random.gauss(arg1, arg2)

    def rand_list(self, arg):
        return arg[self.rand_int(0, len(arg) - 1)]

    def rand_log(self, arg1):
        return int(math.log(self.random.randint(1, arg1), arg1) * arg1)

    @staticmethod
    def rand_seed():
        return random.SystemRandom().randint(1, 999999)

    @staticmethod
    def seed_list(seed, arg):
        return arg[seed % len(arg)]

    @staticmethod
    def seed_int(seed, arg1, arg2):
        if arg1 == arg2:
            return arg1
        return seed % (arg2 - arg1 + 1) + arg1
