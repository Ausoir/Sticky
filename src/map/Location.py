import math

from src.entity.Stock import Stock
from src.game import Global
from src.game.Turn import Turn
from src.map.Field import Field
from src.map.Population import Population
from src.map.Sound import Sound
from src.map.Tile import Tile
from src.tools.Data import Data
from src.tools.Tag import Tag


class Location:
    def __init__(self, name, data):
        self.name = name
        self.tags = Tag()
        self.identity = 0
        self.update_frame = 0
        self.field = Field(self)
        self.sound = Sound(self)
        self.population = Population()
        self.delay = 8
        self.tiles = []
        self.header = None
        if data:
            self.load(data)
        else:
            self.tiles = [[Tile(self, '.', 0, 0)]]
        Turn.add(self.turn)
        Turn.add(self.field.turn)
        Turn.fast_queue.append(self.sound.turn)

    def __str__(self):
        rt = []
        for y in self.tiles:
            row = ''
            for x in y:
                row += x.terrain
            rt.append(row)
        tiles = '%'.join(rt)
        objects = self.population.__str__()
        return self.tags.__str__() + '\n' + tiles + '\n' + objects + '\n'

    def load(self, arg):
        while len(arg) < 3:
            arg.append([])
        self.tags.load(arg[0][0])
        self.load_map(arg, new=True)

    def turn(self):
        if not self.delay:
            self.delay = 400
            self.save()

    def save(self):
        Data.write('../save/' + self.name + '.map', self.__str__())

    def load_map(self, arg, new=False, offset=(0, 0)):
        rows = arg[1][0].split('%')
        row_num = 0
        if new:
            for y in rows:
                row = []
                col_num = 0
                for terrain in y:
                    row.append(Tile(self, terrain, col_num, row_num))
                    col_num += 1
                self.tiles.append(row)
                row_num += 1
        else:
            self.stretch(len(rows[0]) + offset[0], len(rows) + offset[1])
            for y in rows:
                col_num = 0
                for terrain in y:
                    self.tiles[row_num + offset[1]][col_num + offset[0]].set_terrain(terrain)
                    col_num += 1
                row_num += 1
        self.process_terrain()
        objects = []
        for i in arg[2]:
            obj = Stock.get(self, i[2], i)
            if new:
                obj.id = self.get_id()
            obj.relocate(obj.pos.x + offset[0], obj.pos.y + offset[1], force=1)
            obj.add()
            objects.append(obj)
        return objects

    def process_terrain(self):
        for y in self.tiles:
            for x in y:
                x.connect()
                x.update_shader()

    def get_id(self):
        self.identity += 1
        return '#' + str(format(self.identity, 'x'))

    def get_tile(self, x, y, limit=False):
        if self.is_inbound(x, y):
            return self.tiles[y][x]
        elif limit:
            x = max(0, min(len(self.tiles[0]) - 1, x))
            y = max(0, min(len(self.tiles) - 1, y))
            return self.tiles[y][x]

    def is_inbound(self, x, y):
        return 0 <= x < len(self.tiles[0]) and 0 <= y < len(self.tiles)

    def get_tile_from_vec(self, x, y):
        x = math.floor(x / Global.BLOCK)
        y = math.floor(y / Global.BLOCK)
        return self.get_tile(x, y)

    def collide_line(self, x1, y1, x2, y2, function, distance=10):
        degree = math.atan2(y2 - y1, x2 - x1)
        current = [x1 * Global.BLOCK + Global.HALF_BLOCK, y1 * Global.BLOCK + Global.HALF_BLOCK]
        prev_tile = self.get_tile(x1, y1)
        while distance > 0 and (prev_tile.x != x2 or prev_tile.y != y2):
            distance -= 1
            dx = math.cos(degree) * Global.BLOCK
            dy = math.sin(degree) * Global.BLOCK
            current[0] = current[0] + dx
            current[1] = current[1] + dy
            tile = self.get_tile_from_vec(current[0], current[1])
            r = function(prev_tile, tile)
            if r:
                return r
            prev_tile = tile
        return prev_tile

    def collide_land(self, pos1, pos2, flag, distance=10, return_prev=True):
        def fn(prev, tile):
            if tile and tile.is_land(flag):
                if return_prev:
                    return prev
                else:
                    return tile
        return self.collide_line(pos1.x, pos1.y, pos2.x, pos2.y, fn, distance)

    def get_area(self, center_tile, range_x, range_y):
        tiles = []
        for x in range(-range_x, range_x+1):
            for y in range(-range_y, range_y+1):
                tile = self.get_tile(center_tile.x + x, center_tile.y + y)
                if tile:
                    tiles.append(tile)
        return tiles

    def flip(self, flip_x, flip_y):
        if flip_y:
            self.tiles.reverse()
        if flip_x:
            r = []
            for y in self.tiles:
                r.append(y[::-1])
            self.tiles = r
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                self.tiles[y][x].x = x
                self.tiles[y][x].y = y
                for thing in self.tiles[y][x].things:
                    thing.update_vec()
        self.process_terrain()

    def stretch(self, new_x, new_y):
        for y in range(new_y):
            if y >= len(self.tiles):
                self.tiles.append([])
            for x in range(new_x):
                if x >= len(self.tiles[y]):
                    self.tiles[y].append(Tile(self, '?', x, y))
