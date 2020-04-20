class World:
    CHUNK = 20

    def __init__(self, location, map_data):
        self.location = location
        self.location.resize(World.CHUNK * 3, World.CHUNK * 3)
        self.cells = [map_data, map_data, map_data, map_data, map_data, map_data, map_data, map_data, map_data]
        self.expand_cell()
        self.test = 0

    def expand_cell(self):
        obj = []
        for count, data in enumerate(self.cells):
            terrains = data[1][0].split('%')
            row_num = int(count / 3)
            col_num = count % 3
            for y, row in enumerate(range(row_num * World.CHUNK, (row_num + 1) * World.CHUNK)):
                for x, col in enumerate(range(col_num * World.CHUNK, (col_num + 1) * World.CHUNK)):
                    tile = self.location.tiles[row][col]
                    tile.set_terrain(terrains[y][x])
                    obj += tile.things
        return obj

    def check_bounds(self, pos):
        if self.test == 1:
            return False
        if pos.x < 14:
            print('push left')
            self.expand_cell()
        elif pos.y < 14:
            print('push up')
            self.expand_cell()
        elif pos.x >= self.location.get_width() - 14:
            print('push right')
            self.expand_cell()
        elif pos.y >= self.location.get_height() - 14:
            print('push down')
            self.expand_cell()
        else:
            return False
        self.test = 1
        # self.update_objects()
        # self.load(data, offset=offset, make=True)
        return True
