from src.map.GenerateBSPTree import BSPTree
from src.map.Location import Location
from src.tools.Data import Data


class GenerateTown(BSPTree):
    def __init__(self, x, y, seed=0):
        super().__init__(x, y, seed=seed)
        self.buildings = []
        self.buildings_list = []
        for i in ['house1', 'house2', 'house3', 'house4', 'house5', 'house6', 'warehouse']:
            building = Data.process_raw(Data.read('map/buildings/' + i + '.map'))
            tiles = building[1][0].split('%')
            self.buildings_list.append([building, len(tiles[0]), len(tiles)])

    def to_location(self, name):
        location = super().to_location(name)
        for i in self.buildings:
            data = Data.process_raw(i[0].__str__())
            location.load_map(data, offset=[i[1], i[2]])
        num = int(len(self.buildings) * (self.random.rand_float() + .5))
        self.place_mobs(location, [['Looter', num], ['Tank', 1]])
        return location

    def build_on_garden(self, estate):
        self.build_on_estate(estate)

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
            if align == 4:
                possible_buildings.append([i, self.random.rand_bool()])
            elif align == 3:
                possible_buildings.append([i, True])
            elif align == 2:
                possible_buildings.append([i, False])
        if possible_buildings:
            building = self.random.rand_list(possible_buildings)
            self.make_building(building[0], size_x, size_y, estate[0], estate[1], rotate=building[1])

    def make_building(self, building, estate_x, estate_y, start_x, start_y, rotate=False):
        location = Location('building', building[0])
        location.flip(self.random.rand_int(0, 1), self.random.rand_int(0, 1))
        if rotate:
            location.rotate()
            offset_x = (estate_x - building[2])
            offset_y = (estate_y - building[1])
        else:
            offset_x = (estate_x - building[1])
            offset_y = (estate_y - building[2])
        offset_x = self.random.rand_int(0, offset_x)
        offset_y = self.random.rand_int(0, offset_y)
        self.buildings.append([location, start_x + offset_x, start_y + offset_y])
