import math


class Space:
    reusable = None

    def __init__(self, arg=None, arg2=None):
        self.x = 0
        self.y = 0
        if arg is not None:
            self.load(arg, arg2)

    def __str__(self):
        return '[' + str(self.x) + ',' + str(self.y) + ']'

    def load(self, arg, arg2=None):
        if arg2 is not None:
            self.x = arg
            self.y = arg2
        else:
            if isinstance(arg, Space):
                self.x = arg.x
                self.y = arg.y
            elif isinstance(arg, tuple) or isinstance(arg, list):
                self.x = arg[0]
                self.y = arg[1]
            else:
                self.x = arg
                self.y = arg

    def __eq__(self, arg):
        if isinstance(arg, Space):
            return self.x == arg.x and self.y == arg.y
        elif isinstance(arg, tuple) or isinstance(arg, list):
            return self.x == arg[0] and self.y == arg[1]
        else:
            return self.x == arg and self.y == arg

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iadd__(self, arg):
        if isinstance(arg, Space):
            self.x += arg.x
            self.y += arg.y
        elif isinstance(arg, tuple) or isinstance(arg, list):
            self.x += arg[0]
            self.y += arg[1]
        else:
            self.x += arg
            self.y += arg
        return self

    def __add__(self, arg):
        if isinstance(arg, Space):
            return Space(self.x + arg.x, self.y + arg.y)
        elif isinstance(arg, tuple) or isinstance(arg, list):
            return Space(self.x + arg[0], self.y + arg[1])
        else:
            return Space(self.x + arg, self.y + arg)

    def __radd__(self, arg):
        return self.__add__(arg)

    def __sub__(self, arg):
        if isinstance(arg, Space):
            return Space(self.x - arg.x, self.y - arg.y)
        elif isinstance(arg, tuple) or isinstance(arg, list):
            return Space(self.x - arg[0], self.y - arg[1])
        else:
            return Space(self.x - arg, self.y - arg)

    def __rsub__(self, arg):
        if isinstance(arg, Space):
            self.x -= arg.x
            self.y -= arg.y
        elif isinstance(arg, tuple) or isinstance(arg, list):
            self.x -= arg[0]
            self.y -= arg[1]
        else:
            self.x -= arg
            self.y -= arg

    def __neg__(self):
        return Space(-self.x, -self.y)

    def __imul__(self, arg):
        if isinstance(arg, Space):
            self.x *= arg.x
            self.y *= arg.y
        elif isinstance(arg, tuple) or isinstance(arg, list):
            self.x *= arg[0]
            self.y *= arg[1]
        else:
            self.x *= arg
            self.y *= arg
        return self

    def __mul__(self, arg):
        if isinstance(arg, Space):
            return Space(self.x * arg.x, self.y * arg.y)
        elif isinstance(arg, tuple) or isinstance(arg, list):
            return Space(self.x * arg[0], self.y * arg[1])
        else:
            return Space(self.x * arg, self.y * arg)

    def get_atan(self):  # left is 0, clockwise to 360
        return math.degrees(math.atan2(self.y, self.x))

    def abs(self):
        return Space(abs(self.x), abs(self.y))

    def distance(self):
        return math.sqrt((self.x * self.x) + (self.y * self.y))

    def difference(self):
        return abs(self.x) + abs(self.y)

    def sum(self):
        return self.x + self.y

    def to_int(self):
        self.load(math.floor(self.x), math.floor(self.y))
        return self

    def to_list(self):
        return [self.x, self.y]
