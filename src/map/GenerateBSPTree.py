from src.map.Generator import Generator
from src.tools.Data import Data


class BSPTree(Generator):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.background['!'] = '*'
        self.theme['1'] = 'Weed'
        self.theme['2'] = 'Bush'
        self.theme['3'] = 'Tree'
        self.background['Door'] = 'w'
        self.background['Lamp'] = '.'
        self.thickness = 10

    def process(self):
        estate, garden = self.iterate(0, 0, self.get_width(), self.get_height())
        for rect in garden:
            self.fill_rect('*', rect[0], rect[1], rect[2] - 1, rect[3] - 1)
            buildable = [rect[0] + 1, rect[1] + 1, rect[2] - 1, rect[3] - 1]
            self.build_on_garden(buildable)
        for rect in estate:
            self.fill_rect('*', rect[0] + 1, rect[1] + 1, rect[2] - 1, rect[3] - 1)
            buildable = [rect[0] + 1, rect[1] + 1, rect[2] - 1, rect[3] - 1]
            self.build_on_estate(buildable)
        self.adapt_tiles()

    def adapt_tiles(self):
        for y in range(1, self.get_height() - 1):
            for x in range(1, self.get_width() - 1):
                if self.str_map[y][x] == '*':
                    rand = self.random.rand_int(1, 24)
                    if rand == 1:
                        self.str_map[y][x] = '1'
                    elif rand == 2:
                        self.str_map[y][x] = '2'
                    elif rand == 4:
                        if not self.has_neighbor(x, y, lambda p: p in Generator.BLOCKED):
                            self.str_map[y][x] = '3'

    def build_on_garden(self, estate):
        pass

    def build_on_estate(self, estate):
        self.fill_rect('w', estate[0] + 1, estate[1] + 1, estate[2] - 1, estate[3] - 1)
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


class GenerateTown(BSPTree):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.buildings = []
        self.buildings_list = []
        self.load_buildings()

    def load_buildings(self):
        for i in ['house1', 'house2', 'house3', 'house4', 'house5', 'house6', 'warehouse']:
            building = Data.process_raw(Data.read('data/map/building/' + i + '.map'))
            tiles = building[1][0].split('%')
            self.buildings_list.append([building, len(tiles[0]), len(tiles)])

    def process(self):
        margin_x = int(self.get_width() / 12)
        margin_y = int(self.get_height() / 12)
        estate, garden = self.iterate(-1, -1, self.get_width() + 1, self.get_height() + 1)
        for rect in garden + estate:
            self.fill_rect('*', rect[0] + 1, rect[1] + 1, rect[2] - 1, rect[3] - 1)
            buildable = [rect[0] + 1, rect[1] + 1, rect[2] - 1, rect[3] - 1]
            if buildable[0] > margin_x and buildable[2] < self.get_width() - margin_x\
                    and buildable[1] > margin_y and buildable[3] < self.get_height() - margin_y:
                self.build_on_estate(buildable)
        self.adapt_tiles()

    def post_process(self, location):
        entrance = self.find_entrance(location)
        location.tags.set('enterx', entrance.x, add=True)
        location.tags.set('entery', entrance.y, add=True)
        return location

    def to_location(self, name):
        location = super().to_location(name)
        for i in self.buildings:
            data = Data.process_raw(i[0].__str__())
            location.load(data, offset=[i[1], i[2]], make=True)
        num = int(len(self.buildings) * (self.random.rand_float() + .5))
        self.place_mobs(location, [['Looter', num, '.'], ['Tank', 1, '.']])
        return location

    def build_on_estate(self, estate):
        for y in range(estate[1] + 1, estate[3] - 1):
            for x in range(estate[0] + 1, estate[2] - 1):
                self.str_map[y][x] = '*'
        size_x = estate[2] - estate[0]
        size_y = estate[3] - estate[1]
        possible_buildings = []
        for i in self.buildings_list:
            align = 0
            if size_x >= i[1] and size_y >= i[2]:
                align = 2
            if size_x >= i[2] and size_y >= i[1]:
                align += 1
            if align == 3:
                possible_buildings.append([i, self.random.rand_int(0, 3)])
            elif align == 2:
                possible_buildings.append([i, self.random.rand_list([0, 2])])
            elif align == 1:
                possible_buildings.append([i, self.random.rand_list([1, 3])])
        if possible_buildings:
            building = self.random.rand_list(possible_buildings)
            self.make_building(building[0], size_x, size_y, estate[0], estate[1], rotate=building[1])

    def make_building(self, building, estate_x, estate_y, start_x, start_y, rotate=0):
        from src.map.Location import Location
        location = Location('building', building[0])
        location.flip(self.random.rand_int(0, 1), self.random.rand_int(0, 1))
        location.rotate(rotate)
        if rotate in [1, 3]:
            offset_x = (estate_x - building[2])
            offset_y = (estate_y - building[1])
        else:
            offset_x = (estate_x - building[1])
            offset_y = (estate_y - building[2])
        offset_x = self.random.rand_int(0, offset_x)
        offset_y = self.random.rand_int(0, offset_y)
        self.buildings.append([location, start_x + offset_x, start_y + offset_y])


class GeneratePortTown(GenerateTown):
    def __init__(self, x, y, random=None):
        super().__init__(x, y, random)
        self.theme['3'] = 'Palm Tree'

    def load_buildings(self):
        for i in ['house1', 'house2', 'house3', 'house4', 'house5', 'house6', 'warehouse']:
            building = Data.process_raw(Data.read('data/map/building/' + i + '.map'))
            tiles = building[1][0].split('%')
            self.buildings_list.append([building, len(tiles[0]), len(tiles)])

    def process(self):
        margin_x = int(self.get_width() / 12)
        margin_y = int(self.get_height() / 12)
        border = self.random.rand_int(int(self.get_width() / 8), int(self.get_width() / 4))
        self.fill_rect('~', 0, 0, border - 4, self.get_height())
        estate, garden = self.iterate(border, -1, self.get_width() + 1, self.get_height() + 1)
        for rect in garden + estate:
            self.fill_rect('*', rect[0] + 1, rect[1] + 1, rect[2] - 1, rect[3] - 1)
            buildable = [rect[0] + 1, rect[1] + 1, rect[2] - 1, rect[3] - 1]
            if buildable[0] > margin_x and buildable[2] < self.get_width() - margin_x\
                    and buildable[1] > margin_y and buildable[3] < self.get_height() - margin_y:
                self.build_on_estate(buildable)
        self.adapt_tiles()

    def post_process(self, location):
        location.rotate(self.random.rand_int(0, 3))
        location = super().post_process(location)
        return location
