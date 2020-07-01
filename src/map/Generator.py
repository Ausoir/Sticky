from src.entity.Stock import Stock
from src.map.Location import Location
from src.map.Tile import Tile
from src.tools.Random import Random


class Generator:
    BLOCKED = ['D', 'S', 'X', 'W']

    @staticmethod
    def generate_terrain(name, terrain):
        rand = Random()
        if terrain == 'woods':
            gen = Generator.get(terrain)(rand.rand_int(20, 60), rand.rand_int(20, 60), random=rand)
        elif terrain == 'residence':
            gen = Generator.get(terrain)(rand.rand_int(60, 120), rand.rand_int(60, 120), random=rand)
        elif terrain == 'beach residence':
            gen = Generator.get('beach')(rand.rand_int(60, 120), rand.rand_int(60, 120), random=rand)
        elif terrain == 'cove':
            gen = Generator.get('cove')(rand.rand_int(20, 60), rand.rand_int(20, 60), random=rand)
        elif terrain == 'cave':
            gen = Generator.get('cave')(rand.rand_int(20, 60), rand.rand_int(20, 60), random=rand)
        elif terrain == 'village':
            return Generator.get_template(name, 'data/map/town/village', rand)
        elif terrain == 'town':
            return Generator.get_template(name, 'data/map/town/town', rand)
        else:
            gen = Generator.get('field')(40, 40, random=rand)
        r = gen.run(name)
        return r

    @staticmethod
    def get_template(name, directory, rand):
        from src.tools.Data import Data
        building = Data.process_raw(Data.read(directory + '.map'))
        r = Location(name, building)
        Generator.disorient(r, rand)
        r.tags.set('edge', 'travel')
        return r

    @staticmethod
    def get(generator):
        if generator == 'field':
            from src.map.GeneratePerlin import GenerateField
            return GenerateField
        elif generator == 'woods':
            from src.map.GeneratePerlin import GenerateWoods
            return GenerateWoods
        elif generator == 'residence':
            from src.map.GenerateBSPTree import GenerateResidence
            return GenerateResidence
        elif generator == 'beach':
            from src.map.GenerateBSPTree import GenerateBeach
            return GenerateBeach
        elif generator == 'cove':
            from src.map.GeneratePerlin import GenerateCove
            return GenerateCove
        elif generator == 'cave':
            from src.map.GenerateTunneler import GenerateCave
            return GenerateCave
        elif generator == 'island':
            from src.map.GeneratePerlin import GenerateIsland
            return GenerateIsland
        elif generator == 'warehouse':
            from src.map.GenerateWarehouse import GenerateWarehouse
            return GenerateWarehouse

    @staticmethod
    def disorient(location, rand):
        location.rotate(rand.rand_int(0, 3))

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

    def to_location(self, name):
        location = Location(name, None)
        req_height = max(self.get_height(), len(location.tiles))
        for y in range(req_height):
            if y >= len(location.tiles):
                location.tiles.append([])
            req_width = max(self.get_width(), len(location.tiles[0]))
            for x in range(req_width):
                if x >= len(location.tiles[y]):
                    location.tiles[y].append(Tile(location, '?', x, y))
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

    def run(self, name):
        self.process()
        r = self.to_location(name)
        return self.post_process(r)

    def process(self):
        pass

    def post_process(self, location):
        location.tags.set('edge', 'travel')
        location.tags.set('thief', 2)
        return location

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
