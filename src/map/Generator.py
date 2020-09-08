from src.entity.Stock import Stock
from src.game import Global
from src.map.Tile import Tile
from src.tools.Random import Random


class Generator:
    BLOCKED = ['D', 'S', 'X', 'W']

    @staticmethod
    def generate(generator):
        size_x = 39
        size_y = 39
        if generator in ['bamboo', 'forest', 'woods', 'field']:
            from src.map.GeneratePerlin import GeneratePerlin
            r = GeneratePerlin(size_x, size_y)
            if generator == 'bamboo':
                r.background['!'] = ';'
                r.disposition = [[.7, 'Bamboo'], [.695, 'Fruit Tree'], [.69, 'Tree'], [.4, '\"'], [0, ';']]
            elif generator == 'woods':
                r.background['!'] = ';'
                r.disposition = [[.85, 'Tree'], [.84, 'Fruit Tree'], [.75, '\"'], [.4, ';'], [0, '.']]
            elif generator == 'forest':
                r.disposition = [[.85, 'Tree'], [.84, 'Weed'], [.8, 'Bush'], [.75, '#'], [.25, ':'], [0, '.']]
            elif generator == 'field':
                r.background['Rock'] = '.'
                r.disposition = [[.75, '#'], [.5, ':'], [0, '.']]
            r.run()
        elif generator == 'cave':
            from src.map.GenerateTunneler import GenerateCave
            GenerateCave(size_x, size_y).run()
        elif generator == 'mansion':
            from src.map.GenerateTunneler import GenerateMansion
            GenerateMansion(size_x, size_y).run()
        elif generator == 'temple':
            from src.map.GenerateTunneler import GenerateMansion
            r = GenerateMansion(size_x, size_y)
            r.theme['.'] = 'H'
            r.theme['X'] = 'W'
            r.run()
        elif generator == 'warehouse':
            from src.map.GenerateWarehouse import GenerateWarehouse
            GenerateWarehouse(size_x, size_y).run()
        elif generator == 'lab':
            from src.map.GenerateWarehouse import GenerateWarehouse
            r = GenerateWarehouse(size_x, size_y)
            r.display_floor = 'K'
            r.wall = 'J'
            r.theme = {'.': 'j', 'D': 'Window', 'W': 'Window', ':': 'Brain', ';': 'Brain', 'Box': 'Floodlight'}
            r.appliance = ['Brain']
            r.run()
        Global.world.dirty = True
        Global.world.location.process_terrain()

    @staticmethod
    def make_map(x, y, arg=None):
        r = []
        for rows in range(y):
            row = []
            for col in range(x):
                row.append(arg)
            r.append(row)
        return r

    def __init__(self, x, y, random=None):
        if random is None:
            random = Random()
        self.random = random
        self.theme = {}
        self.background = {'!': '.'}
        self.str_map = Generator.make_map(x, y)
        self.fill_rect('.', 0, 0, x, y)
        self.start = [32, 19]

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

    def to_location(self):
        location = Global.world.location
        for self_y in range(self.get_height()):
            for self_x in range(self.get_width()):
                terrain = self.theme.get(self.str_map[self_y][self_x])
                if not terrain:
                    terrain = self.str_map[self_y][self_x]
                if len(terrain) > 1:
                    background = self.background.get(terrain)
                    if not background:
                        background = self.background['!']
                    location.tiles[self_y][self_x].set_terrain(background)
                    Stock.make(terrain, location.get_tile(self_x, self_y))
                else:
                    location.tiles[self_y][self_x].set_terrain(terrain)
        return location

    def run(self):
        self.process()
        return self.to_location()

    def process(self):
        pass

    def fill_rect(self, terrain, x1, y1, x2, y2):
        for y in range(y1, y2):
            for x in range(x1, x2):
                self.str_map[y][x] = terrain

    def flip(self, flip_x, flip_y):
        if flip_y:
            self.str_map.reverse()
        if flip_x:
            r = []
            for y in self.str_map:
                r.append(y[::-1])
            self.str_map = r

    def outline(self, terrain):
        for x in range(self.get_width()):
            self.str_map[0][x] = terrain
            self.str_map[self.get_height() - 1][x] = terrain
        for y in range(self.get_height()):
            self.str_map[y][0] = terrain
            self.str_map[y][self.get_width() - 1] = terrain

    def has_neighbor(self, x, y, fn):
        for i in Global.cardinal_coord:
            if fn(self.str_map[y + i[1]][x + i[0]]):
                return True

    def get_width(self):
        return len(self.str_map[0])

    def get_height(self):
        return len(self.str_map)

    def find_entrance(self, location, terrain='.'):
        possibles = []
        for x in range(location.get_width()):
            possibles.append(location.get_tile(x, 0))
            possibles.append(location.get_tile(x, location.get_height() - 1))
        for y in range(location.get_height()):
            possibles.append(location.get_tile(0, y))
            possibles.append(location.get_tile(location.get_width() - 1, y))
        possibles = list(filter(lambda tile: tile.get_icon() == terrain, possibles))
        return self.random.rand_list(possibles)

    def place_mobs(self, location, mobs):
        possibles = {}
        terrains = []
        for mob_data in mobs:
            terrains.append(mob_data[2])
        for y in range(location.get_height()):
            for x in range(location.get_width()):
                tile = location.get_tile(x, y)
                if tile.get_icon() in terrains and not tile.is_land(Tile.COLLIDE_UNIT):
                    if tile.get_icon() not in possibles:
                        possibles[tile.get_icon()] = []
                    possibles[tile.get_icon()].append(tile)
        for mob_data in mobs:
            if len(possibles[mob_data[2]]) > mob_data[1]:
                for i in range(mob_data[1]):
                    tile = self.random.rand_list(possibles[mob_data[2]])
                    Stock.make(mob_data[0], tile)
