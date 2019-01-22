import math


class Math:
    SIN = []
    COS = []

    @staticmethod
    def init():
        for i in range(360):
            Math.SIN.append(math.sin(i))
            Math.COS.append(math.cos(i))

    @staticmethod
    def sin(degree):
        return math.sin(math.radians(degree))
        # return Math.SIN[int(math.radians(degree)) % 360]

    @staticmethod
    def cos(degree):
        return math.cos(math.radians(degree))
        # return Math.COS[int(math.radians(degree)) % 360]
