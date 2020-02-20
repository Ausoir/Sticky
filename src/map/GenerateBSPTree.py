from src.map.Generator import Generator
from src.tools import Direction


class BSPTree(Generator):
    def __init__(self, x, y, seed=0):
        super().__init__(x, y, seed=seed)
        self.background['!'] = '*'
        self.theme['1'] = 'Weed'
        self.theme['2'] = 'Dandelion'
        self.theme['3'] = 'Bush'
        self.background['Door'] = 'w'
        self.background['Lamp'] = '.'
        self.divide = 10
        self.thickness = 8

    def run(self):
        estate, garden = self.iterate(0, 0, self.width, self.height)
        for rect in garden:
            for y in range(rect[1], rect[3] - 1):
                for x in range(rect[0], rect[2] - 1):
                    self.str_map[y][x] = '*'
        for rect in estate:
            for y in range(rect[1] + 1, rect[3] - 1):
                for x in range(rect[0] + 1, rect[2] - 1):
                    self.str_map[y][x] = '*'
            buildable = [rect[0] + 1, rect[1] + 1, rect[2] - 1, rect[3] - 1]
            self.build_on_estate(buildable)
        self.adapt_tiles()

    def adapt_tiles(self):
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.str_map[y][x] == '*':
                    rand = self.random.rand_int(1, 24)
                    if rand == 1:
                        self.str_map[y][x] = '1'
                    elif rand == 2:
                        self.str_map[y][x] = '2'
                    elif rand == 3:
                        self.str_map[y][x] = '3'
                if self.str_map[y][x] == 'X':
                    blocked = []
                    for i in Direction.coord.values():
                        if self.str_map[y + i[1]][x + i[0]] in Generator.BLOCKED:
                            blocked.append(1)
                        else:
                            blocked.append(0)
                    if self.str_map[y][x] == 'X':
                        if blocked == [1, 0, 1, 0] or blocked == [0, 1, 0, 1]:
                            rand = self.random.rand_int(1, 16)
                            if rand == 1:
                                self.str_map[y][x] = 'W'

    def build_on_estate(self, estate):
        for y in range(estate[1] + 1, estate[3] - 1):
            for x in range(estate[0] + 1, estate[2] - 1):
                self.str_map[y][x] = 'w'
        for x in range(estate[0] + 1, estate[2] - 1):
            self.str_map[estate[1] + 1][x] = 'X'
            self.str_map[estate[3] - 2][x] = 'X'
        for y in range(estate[1] + 1, estate[3] - 1):
            self.str_map[y][estate[0] + 1] = 'X'
            self.str_map[y][estate[2] - 2] = 'X'
        door_pos = self.random.rand_int(1, 4)
        door_ry = self.random.rand_int(estate[1] + 3, estate[3] - 3)
        door_rx = self.random.rand_int(estate[0] + 3, estate[2] - 3)
        if door_pos == 1:
            self.str_map[door_ry][estate[0] + 1] = 'D'
            self.str_map[door_ry + 1][estate[0]] = 'Lamp'
        elif door_pos == 2:
            self.str_map[estate[1] + 1][door_rx] = 'D'
            self.str_map[estate[1]][door_rx + 1] = 'Lamp'
        elif door_pos == 3:
            self.str_map[door_ry][estate[2] - 2] = 'D'
            self.str_map[door_ry - 1][estate[2] - 1] = 'Lamp'
        elif door_pos == 4:
            self.str_map[estate[3] - 2][door_rx] = 'D'
            self.str_map[estate[3] - 1][door_rx - 1] = 'Lamp'

    def iterate(self, px, py, px2, py2):
        estate = []
        garden = []
        ratio = self.random.rand_float() * .6 + .2
        new_height = (py2 - py) * ratio
        new_height_iv = (py2 - py) * (1 - ratio)
        new_width = (px2 - px) * ratio
        new_width_iv = (px2 - px) * (1 - ratio)
        if max(new_width, new_width_iv) > max(new_height, new_height_iv):
            area = [px, py, px + new_width, py2]
            area2 = [px + new_width, py, px + new_width + new_width_iv, py2]
            if new_width > self.thickness:
                new_estate, new_garden = self.iterate(area[0], area[1], area[2], area[3])
                if not new_estate:
                    estate.append([int(x) for x in area])
                else:
                    estate += new_estate
                    garden += new_garden
            else:
                garden.append([int(x) for x in area])
            if new_width_iv > self.thickness:
                new_estate, new_garden = self.iterate(area2[0], area2[1], area2[2], area2[3])
                if not new_estate:
                    estate.append([int(x) for x in area2])
                else:
                    estate += new_estate
                    garden += new_garden
            else:
                garden.append([int(x) for x in area2])
        else:
            area = [px, py, px2, py + new_height]
            area2 = [px, py + new_height, px2, py + new_height + new_height_iv]
            if new_height > self.thickness:
                new_estate, new_garden = self.iterate(area[0], area[1], area[2], area[3])
                if not new_estate:
                    estate.append([int(x) for x in area])
                else:
                    estate += new_estate
                    garden += new_garden
            else:
                garden.append([int(x) for x in area])
            if new_height_iv > self.thickness:
                new_estate, new_garden = self.iterate(area2[0], area2[1], area2[2], area2[3])
                if not new_estate:
                    estate.append([int(x) for x in area2])
                else:
                    estate += new_estate
                    garden += new_garden
            else:
                garden.append([int(x) for x in area2])
        return estate, garden

    def get_volume(self, arg):
        return (arg[2] - arg[0]) * (arg[3] - arg[1])
