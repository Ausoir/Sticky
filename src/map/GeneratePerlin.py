import math

from src.map.Generator import Generator


class GeneratePerlin(Generator):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.background = {'!': '*'}
        self.layers = 6

    @staticmethod
    def interpolate(arg1, arg2, alpha):
        return arg1 * (1 - alpha) + alpha * arg2

    @staticmethod
    def make_smooth(arg, octave):
        width = len(arg[0])
        height = len(arg)
        r = Generator.make_map(width, height)
        period = 1 << octave
        frequency = 1.0 / period
        for i in range(height):
            sample_i0 = int(i / period) * period
            sample_i1 = int((sample_i0 + period) % height)
            horizontal_blend = (i - sample_i0) * frequency
            for j in range(width):
                sample_j0 = int(j / period) * period
                sample_j1 = int((sample_j0 + period) % width)
                vertical_blend = (j - sample_j0) * frequency
                top = GeneratePerlin.interpolate(arg[sample_i0][sample_j0], arg[sample_i1][sample_j0], horizontal_blend)
                bot = GeneratePerlin.interpolate(arg[sample_i0][sample_j1], arg[sample_i1][sample_j1], horizontal_blend)
                r[i][j] = GeneratePerlin.interpolate(top, bot, vertical_blend)
        return r

    @staticmethod
    def radialize(base):
        width = len(base[0])
        height = len(base)
        center_x = int(width / 2)
        center_y = int(height / 2)
        for i in range(height):
            for j in range(width):
                val = math.sqrt(pow((i - center_y) / center_y, 2) + pow((j - center_x) / center_x, 2))
                val *= .2
                base[i][j] /= min(1.0, max(.1, val))
        return base

    @staticmethod
    def normalize(base):
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

    def process(self):
        pass

    def make_base(self, x, y):
        noise = []
        for i in range(y):
            row = []
            for j in range(x):
                val = self.random.rand_float()
                row.append(val)
            noise.append(row)
        return noise

    def make_perlin(self, width, height):
        r = Generator.make_map(width, height, arg=0)
        base = self.make_base(width, height)
        for level in range(1, self.layers):
            graph = self.make_smooth(base, level)
            for i in range(height):
                for j in range(width):
                    r[i][j] += graph[i][j] * (1 / level)
        return r


class GenerateIsland(GeneratePerlin):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.background = {'!': '*', 'Cove': '.', 'Beach Residence': '.'}
        self.layers = 9
        self.town_candidates = []

    def process(self):
        r = self.make_perlin(self.get_width(), self.get_height())
        r = self.radialize(r)
        r = self.normalize(r)
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                value = r[y][x]
                if value > .8:
                    self.str_map[y][x] = 'Mountain'
                elif value > .795:
                    self.str_map[y][x] = 'Cave'
                elif value > .79:
                    self.str_map[y][x] = 'Hill Residence'
                    self.town_candidates.append([x, y])
                elif value > .7:
                    self.str_map[y][x] = 'Woods'
                elif value > .56:
                    self.str_map[y][x] = '*'
                elif value > .558:
                    self.str_map[y][x] = 'Residence'
                elif value > .556:
                    self.str_map[y][x] = 'Village'
                    self.town_candidates.append([x, y])
                elif value > .507:
                    self.str_map[y][x] = '.'
                elif value > .505:
                    self.str_map[y][x] = 'Village'
                    self.town_candidates.append([x, y])
                elif value > .503:
                    if self.has_neighbor(x, y, lambda p: p == '~'):
                        self.str_map[y][x] = 'Beach Residence'
                elif value > .5:
                    self.str_map[y][x] = 'Cove'
                elif value > .3:
                    self.str_map[y][x] = '~'
                else:
                    self.str_map[y][x] = '='
        for i in range(3):
            coords = self.random.rand_list(self.town_candidates)
            self.str_map[coords[1]][coords[0]] = 'Town'


class GenerateWoods(GeneratePerlin):
    def process(self):
        r = self.make_perlin(self.get_width(), self.get_height())
        r = self.normalize(r)
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                value = r[y][x] + self.random.rand_float() * .2
                if value > .75:
                    self.str_map[y][x] = 'Tree'
                elif value > .65:
                    self.str_map[y][x] = 'Weed'
                elif value > .64:
                    self.str_map[y][x] = 'Plant'
                elif value > .6:
                    self.str_map[y][x] = 'Bush'
                elif value > .59:
                    self.str_map[y][x] = 'Killer Ivy'
                elif value > .4:
                    self.str_map[y][x] = '*'
                else:
                    self.str_map[y][x] = '.'

    def post_process(self, location):
        rx = int(self.get_width() / 2)
        ry = int(self.get_height() / 2)
        while location.get_tile(rx, ry).get_icon() != '.':
            rx += self.random.rand_int(-1, 1)
            ry += self.random.rand_int(-1, 1)
        location.tags.set('enterx', rx)
        location.tags.set('entery', ry)
        return super().post_process(location)


class GenerateField(GeneratePerlin):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.background = {'!': '*', 'Rock': '.'}

    def process(self):
        r = self.make_perlin(self.get_width(), self.get_height())
        r = self.normalize(r)
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                value = r[y][x]
                if value > .95:
                    self.str_map[y][x] = 'Tree'
                elif value > .85:
                    self.str_map[y][x] = 'Bush'
                elif value > .8:
                    self.str_map[y][x] = 'Weed'
                elif value > .78:
                    self.str_map[y][x] = 'Plant'
                elif value > .55:
                    self.str_map[y][x] = '*'
                elif value > .54:
                    self.str_map[y][x] = 'Rock'
                else:
                    self.str_map[y][x] = '.'

    def post_process(self, location):
        rx = int(self.get_width() / 2)
        ry = int(self.get_height() / 2)
        while location.get_tile(rx, ry).get_icon() != '.':
            rx += self.random.rand_int(-1, 1)
            ry += self.random.rand_int(-1, 1)
        location.tags.set('enterx', rx)
        location.tags.set('entery', ry)
        return super().post_process(location)


class GenerateCove(GeneratePerlin):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.background = {'!': '.'}
        self.layers = 4

    def process(self):
        r = self.make_perlin(self.get_width(), self.get_height())
        r = self.radialize(r)
        r = self.normalize(r)
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                value = r[y][x]
                if value > .72:
                    self.str_map[y][x] = '~'
                elif value > .7:
                    self.str_map[y][x] = 'Rock'
                elif value > .4:
                    self.str_map[y][x] = '.'
                else:
                    self.str_map[y][x] = 'R'
        rx = int(self.get_width() / 2)
        self.outline('R')
        self.fill_rect('.', rx - 4, 0, rx + 4, int(self.get_height() / 2))
        self.fill_rect('~', rx - 2, 0, rx + 2, int(self.get_height() / 2))

    def post_process(self, location):
        self.disorient(location, self.random)
        entrance = self.find_entrance(location)
        location.tags.set('enterx', entrance.x)
        location.tags.set('entery', entrance.y)
        return super().post_process(location)
