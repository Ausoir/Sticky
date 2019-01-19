import math


class Space:
    def __init__(self, arg=None, arg2=None):
        self.x = 0
        self.y = 0
        if arg is not None:
            self.load(arg, arg2)

    def __str__(self):
        return '[' + str(self.x) + ',' + str(self.y) + ']'

    def load(self, arg, arg2=None):
        if arg2:
            self.x = arg
            self.y = arg2
        elif arg:
            if isinstance(arg, Space):
                self.x = arg.x
                self.y = arg.y
            elif isinstance(arg, int):
                self.x = arg
                self.y = arg
            elif isinstance(arg, tuple) or isinstance(arg, list):
                self.x = arg[0]
                self.y = arg[1]

    def __iadd__(self, arg):
        if isinstance(arg, Space):
            self.x += arg.x
            self.y += arg.y
        elif isinstance(arg, int):
            self.x += arg
            self.y += arg
        elif isinstance(arg, tuple) or isinstance(arg, list):
            self.x += arg[0]
            self.y += arg[1]
        return self

    def __add__(self, arg):
        if isinstance(arg, Space):
            return Space(self.x + arg.x, self.y + arg.y)
        elif isinstance(arg, int):
            return Space(self.x + arg, self.y + arg)
        elif isinstance(arg, tuple) or isinstance(arg, list):
            return Space(self.x + arg[0], self.y + arg[1])

    def __radd__(self, arg):
        return self.__add__(arg)

    def __sub__(self, arg):
        return self.__add__(-arg)

    def __rsub__(self, arg):
        return arg.__add__(-self)

    def __neg__(self):
        return Space(-self.x, -self.y)

    def __imul__(self, arg):
        if isinstance(arg, Space):
            self.x *= arg.x
            self.y *= arg.y
        elif isinstance(arg, int):
            self.x *= arg
            self.y *= arg
        elif isinstance(arg, tuple) or isinstance(arg, list):
            self.x *= arg[0]
            self.y *= arg[1]
        return self

    def __mul__(self, other):
        return Space(self.x * other, self.y * other)

    def atan(self):  # left is 0, clockwise to 360
        return math.degrees(math.atan2(-self.y, self.x)) + 180

    def abs(self):
        return Space(abs(self.x), abs(self.y))

    def distance(self):
        return math.sqrt((self.x * self.x) + (self.y * self.y))

    def to_list(self):
        return [self.x, self.y]
