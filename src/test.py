from src.tools.Random import Random


class Test:
    @staticmethod
    def interpolate(arg1, arg2, alpha):
        return arg1 * (1 - alpha) + alpha * arg2

    @staticmethod
    def make_empty(width, height):
        r = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(0)
            r.append(row)
        return r

    def __init__(self):
        self.rand = Random().random

    def make_base(self, x, y):
        noise = []
        for i in range(y):
            row = []
            for j in range(x):
                val = self.rand.random()
                row.append(val)
            noise.append(row)
        return noise

    def make_smooth(self, arg, octave):
        width = len(arg[0])
        height = len(arg)
        r = Test.make_empty(width, height)
        period = 2 << octave
        frequency = 1.0 / period
        for i in range(height):
            sample_i0 = int(i / period) * period
            sample_i1 = int((sample_i0 + period) % height)
            horizontal_blend = (i - sample_i0) * frequency
            for j in range(width):
                sample_j0 = int(j / period) * period
                sample_j1 = int((sample_j0 + period) % width)
                vertical_blend = (j - sample_j0) * frequency
                top = Test.interpolate(arg[sample_i0][sample_j0], arg[sample_i1][sample_j0], horizontal_blend)
                bottom = Test.interpolate(arg[sample_i0][sample_j1], arg[sample_i1][sample_j1], horizontal_blend)
                r[i][j] = Test.interpolate(top, bottom, vertical_blend)
        return r

    def make_perlin(self, width, height):
        r = self.make_empty(width, height)
        base = self.make_base(width, height)
        for level in range(1, 5):
            graph = self.make_smooth(base, level)
            for i in range(height):
                for j in range(width):
                    r[i][j] += graph[i][j] * (1 / level)
        return r

    def radialize(self, base):
        width = len(base[0])
        height = len(base)
        center_x = int(width / 2)
        center_y = int(height / 2)
        for i in range(height):
            for j in range(width):
                val = (abs(i - center_y) / center_y) + (abs((j - center_x)) / center_x)
                base[i][j] /= min(1.0, max(.1, val / 4))
        return base

    def normalize(self, base):
        width = len(base[0])
        height = len(base)
        maximum = 0
        for i in range(height):
            for j in range(width):
                if base[i][j] > maximum:
                    maximum = base[i][j]
        for i in range(height):
            for j in range(width):
                base[i][j] = base[i][j] / maximum
        return base

    def draw(self):
        gen = self.make_perlin(128, 64)
        gen = self.radialize(gen)
        gen = self.normalize(gen)
        for i in gen:
            row = ''
            for j in i:
                if j > .9:
                    row += '0'
                elif j > .7:
                    row += 'o'
                elif j > .5:
                    row += '.'
                else:
                    row += ' '
            print(row)


test = Test()
test.draw()

