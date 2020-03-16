from random import Random

from src.map.Generator import Generator


class GenerateWarehouse(Generator):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.floor = 'b'
        self.display_floor = 'w'
        self.wall = 'B'
        self.theme = {'.': 'c', 'D': 'Door', 'W': 'Window', 'E': 'Elevator', ':': 'Shelf Full', ';': 'Shelf'}
        self.appliance = ['Bed', 'Sofa', 'Toilet', 'Sink', 'Kitchen', 'Crate', 'Workbench',
                          'Lamp', 'Chair', 'Machine', 'Register', 'Desk', 'Rack']
        self.background = {'!': self.display_floor}
        self.divide = 8
        self.thickness = 4

    def __str__(self):
        r = []
        for y in self.str_map:
            row = ''
            for x in y:
                if x in self.theme:
                    terrain = self.theme[x]
                    if len(terrain) > 1:
                        row += x
                    else:
                        row += self.theme[x]
                else:
                    row += x
            r.append(row)
        return '\n'.join(r)

    def process(self):
        estate, garden = self.iterate(6, 1, self.width - 7, 8)
        estate2, garden2 = self.iterate(0, 10, self.width, self.height)
        self.build_entrance()
        for rect in garden + estate + garden2 + estate2:
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            buildable = [rect[0], rect[1], rect[2] - 1, rect[3] - 1]
            if 4 < width < 10 and 4 < height < 10:
                self.build_pillar(buildable)
            elif 2 < width and 2 < height:
                self.build_display(buildable)
            else:
                self.build_isle(buildable)

    def iterate(self, px, py, px2, py2):
        estate = []
        garden = []
        ratio = self.random.random() * .8 + .1
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

    def build_entrance(self):
        for x in range(5):
            for y in range(5):
                if x == 4 or y == 4:
                    if x == 3:
                        self.str_map[y][x] = 'D'
                    else:
                        rand = self.random.randint(1, 16)
                        if rand == 1:
                            self.str_map[y][x] = 'W'
                        else:
                            self.str_map[y][x] = self.wall
                else:
                    self.str_map[y][x] = '*'

    def build_display(self, estate):
        item = self.appliance[self.random.randint(0, len(self.appliance) - 1)]
        for y in range(estate[1], estate[3]):
            for x in range(estate[0], estate[2]):
                if x == estate[0] or x == estate[2] - 1 or y == estate[1] or y == estate[3] - 1:
                    rand = self.random.randint(1, 3)
                    if rand != 1:
                        self.str_map[y][x] = item
                    else:
                        self.str_map[y][x] = self.display_floor
                else:
                    self.str_map[y][x] = self.wall

    def build_isle(self, estate):
        for y in range(estate[1], estate[3]):
            for x in range(estate[0], estate[2]):
                if x == estate[0] or x == estate[2] - 1 or y == estate[1] or y == estate[3] - 1:
                    rand = self.random.randint(0, 28)
                    if rand % 2 == 0:
                        self.str_map[y][x] = ':'
                    else:
                        self.str_map[y][x] = ';'
                else:
                    self.str_map[y][x] = 'Crate'

    def build_pillar(self, estate):
        for y in range(estate[1] + 1, estate[3] - 1):
            for x in range(estate[0] + 1, estate[2] - 1):
                self.str_map[y][x] = 'w'
        buff = self.random.randint(0, 1)
        if buff == 1:
            for y in range(estate[1] + 1, estate[3] - 1):
                for x in range(estate[0] + 1, estate[2] - 1):
                    self.str_map[y][x] = self.appliance[self.random.randint(0, len(self.appliance) - 1)]
        else:
            for y in range(estate[1] + 1, estate[3] - 1):
                for x in range(estate[0] + 1, estate[2] - 1):
                    self.str_map[y][x] = 'Crate'
            return
        for x in range(estate[0], estate[2]):
            wall = self.wall
            if estate[0] < x < estate[2] - 1 and self.random.randint(1, 4) == 1:
                wall = 'W'
            self.str_map[estate[1]][x] = wall
            self.str_map[estate[3] - 1][x] = wall
        for y in range(estate[1], estate[3]):
            wall = self.wall
            if estate[1] < y < estate[3] - 1 and self.random.randint(1, 12) == 1:
                wall = 'W'
            self.str_map[y][estate[0]] = wall
            self.str_map[y][estate[2] - 1] = wall
        door_pos = self.random.randint(1, 4)
        door_ry = self.random.randint(estate[1] + 2, estate[3] - 2)
        door_rx = self.random.randint(estate[0] + 2, estate[2] - 2)
        if door_pos == 1:
            self.str_map[door_ry][estate[0]] = 'D'
        elif door_pos == 2:
            self.str_map[estate[1]][door_rx] = 'D'
        elif door_pos == 3:
            self.str_map[door_ry][estate[2] - 1] = 'D'
        elif door_pos == 4:
            self.str_map[estate[3] - 1][door_rx] = 'D'
