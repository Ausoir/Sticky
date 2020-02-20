from src.tools.Random import Random


class Generator:
    BLOCKED = ['D', 'S', 'X', 'W']

    @staticmethod
    def generate(generator_type, x, y, seed=0):
        if generator_type == 2:
            from src.map.GenerateTunneler import Tunneler
            runner = Tunneler(x, y, seed)
        elif generator_type == 3:
            from src.map.GenerateBSPTree import BSPTree
            runner = BSPTree(x, y, seed)
        else:
            from src.map.GenerateTemplate import Template
            runner = Template(x, y, seed)
        runner.run()
        return runner

    def __init__(self, x, y, seed=0):
        self.random = Random(seed)
        self.theme = {'X': 'B', 'D': 'Door', 'W': 'Window'}
        self.background = {'!': '.'}
        self.width = x
        self.height = y
        self.str_map = self.make_map(x, y)
        # self.theme = {'.': '.', '*': '.', 'o': '.', 'X': 'X', 'D': 'Door', 'W': 'Window'}

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

    def transpose(self, location, offset_x=0, offset_y=0):
        for i in location.population.get_all():
            if i.pos.x >= offset_x and i.pos.y >= offset_y:
                i.remove()
        from src.map.Tile import Tile
        from src.entity.Stock import Stock
        req_height = max(offset_y + self.height, len(location.tiles))
        for y in range(req_height):
            if y >= len(location.tiles):
                location.tiles.append([])
            req_width = max(offset_x + self.width, len(location.tiles[0]))
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
                    location.tiles[offset_y + self_y][offset_x + self_x].set_terrain(background)
                    Stock.make(terrain, location.get_tile(offset_x + self_x, offset_y + self_y))
                else:
                    location.tiles[offset_y + self_y][offset_x + self_x].set_terrain(terrain)
        location.process_terrain()

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
