class Line:
    def __init__(self, pt, ptd):
        self.pt = pt
        self.ptd = ptd

    def __str__(self):
        return '[' + self.pt.__str__() + ',' + self.ptd.__str__() + ']'

    def cross_line(self, l2):
        o1 = Line.get_orientation(self.pt, self.ptd, l2.pt)
        o2 = Line.get_orientation(self.pt, self.ptd, l2.ptd)
        o3 = Line.get_orientation(l2.pt, l2.ptd, self.pt)
        o4 = Line.get_orientation(l2.pt, l2.ptd, self.ptd)
        if o1 != o2 and o3 != o4:
            if self.cross_point(l2.pt) != self.cross_point(l2.ptd):
                return 1
        return 0

    @staticmethod
    def get_orientation(a, b, c):
        v = ((a.y - b.y) * (c.x - a.x)) - ((a.x - b.x) * (c.y - a.y))
        if v == 0:
            return 0
        elif v > 0:
            return 1
        else:
            return 2

    def get_slope(self):
        if self.ptd.x - self.pt.x == 0:
            return 999999
        else:
            return (self.ptd.y - self.pt.y) / (self.ptd.x - self.pt.x)

    def cross_point(self, pt):
        return ((pt.x - self.pt.x) * self.get_slope()) - (pt.y - self.pt.y) >= 0
