from src.tools.Random import Random


class Generator:
    BLOCKED = ['D', 'S', 'X', 'W']

    @staticmethod
    def generate(name, generator_type, x, y, seed=0):
        if generator_type == 2:
            from src.map.GenerateTunneler import Tunneler
            location = Tunneler(x, y, seed)
        elif generator_type == 3:
            from src.map.GenerateBSPTree import BSPTree
            location = BSPTree(x, y, seed)
        elif generator_type == 4:
            from src.map.GenerateTown import GenerateTown
            location = GenerateTown(x, y, seed)
        else:
            from src.map.Location import Location
            return Location(name, None)
        return location.publish(name)

    def __init__(self, x, y, seed=0):
        self.random = Random(seed)
        self.theme = {'X': 'B', 'D': 'Door', 'W': 'Window'}
        self.background = {'!': '.'}
        self.width = x
        self.height = y
        self.str_map = self.make_map(x, y)

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
        from src.map.Location import Location
        location = Location(name, None)
        from src.map.Tile import Tile
        from src.entity.Stock import Stock
        req_height = max(self.height, len(location.tiles))
        for y in range(req_height):
            if y >= len(location.tiles):
                location.tiles.append([])
            req_width = max(self.width, len(location.tiles[0]))
            for x in range(req_width):
                if x >= len(location.tiles[y]):
                    location.tiles[y].append(Tile(location, '?', x, y))
        for self_y in range(self.height):
            for self_x in range(self.width):
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
        pass

    def publish(self, name):
        self.run()
        return self.to_location(name)

    def make_map(self, size_x, size_y):
        r = []
        for y in range(size_y):
            row = []
            for x in range(size_x):
                row.append('.')
            r.append(row)
        return r

    def flip(self, flip_x, flip_y):
        if flip_y:
            self.str_map.reverse()
        if flip_x:
            r = []
            for y in self.str_map:
                r.append(y[::-1])
            self.str_map = r

    def place_mobs(self, location, mobs):
        from src.entity.Stock import Stock
        from src.map.Tile import Tile
        for mob_data in mobs:
            for i in range(mob_data[1]):
                x = self.random.rand_int(1, len(location.tiles[0]) - 2)
                y = self.random.rand_int(1, len(location.tiles) - 2)
                tile = location.get_tile(x, y)
                if not tile.is_land(Tile.CHECK_SOLID):
                    Stock.make(mob_data[0], tile)
