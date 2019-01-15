import math


class Space:
    def __init__(self, para=None, para2=None):
        self.x = 0
        self.y = 0
        if para is not None:
            if para2 is not None:
                self.load(para, para2)
            else:
                self.load(para)

    def __str__(self):
        return '[' + str(self.x) + ',' + str(self.y) + ']'

    def load(self, para, para2=None):
        if para2 is not None:
            self.x = para
            self.y = para2
        else:
            if isinstance(para, Space):
                self.x = para.x
                self.y = para.y
            elif isinstance(para, int):
                self.x = para
                self.y = para
            elif isinstance(para, tuple) or isinstance(para, list):
                self.x = para[0]
                self.y = para[1]

    def __iadd__(self, para):
        if isinstance(para, Space):
            self.x += para.x
            self.y += para.y
        elif isinstance(para, int):
            self.x += para
            self.y += para
        elif isinstance(para, tuple) or isinstance(para, list):
            self.x += para[0]
            self.y += para[1]
        return self

    def __add__(self, para):
        if isinstance(para, Space):
            return Space(self.x + para.x, self.y + para.y)
        elif isinstance(para, int):
            return Space(self.x + para, self.y + para)
        elif isinstance(para, tuple) or isinstance(para, list):
            return Space(self.x + para[0], self.y + para[1])

    def __radd__(self, para):
        return self.__add__(para)

    def __sub__(self, para):
        return self.__add__(-para)

    def __rsub__(self, para):
        return para.__add__(-self)

    def __neg__(self):
        return Space(-self.x, -self.y)

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
