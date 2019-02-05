import math


class Math:
    SIN = []
    COS = []

    @staticmethod
    def init():
        for i in range(360):
            Math.SIN.append(math.sin(math.radians(i)))
            Math.COS.append(math.cos(math.radians(i)))

    @staticmethod
    def sin(degree):
        return math.sin(math.radians(degree))
        # return Math.SIN[int(degree) % 360]

    @staticmethod
    def cos(degree):
        return math.cos(math.radians(degree))
        # return Math.COS[int(degree) % 360]
