import math

from src.entity.Stock import Stock
from src.game import Global
from src.game.Turn import Turn
from src.map.Field import Field
from src.map.Population import Population
from src.map.Sound import Sound
from src.map.Tile import Tile


class Location:
    def __init__(self, data, make=False):
        self.field = Field(self)
        self.sound = Sound(self)
        self.population = Population()
        self.tiles = [[]]
        self.push_status = [0, 0]
        self.header = None
        if data:
            self.load(data, make)
        Turn.add(self.field.turn)

    def __str__(self):
        rt = []
        for y in self.tiles:
            row = ''
            for x in y:
                row += x.get_icon()
            rt.append(row)
        tiles = '%'.join(rt)
        objects = self.population.__str__()
        return tiles + '\n' + objects + '\n'

    def load(self, arg, make=True, offset=(0, 0)):
        while len(arg) < 3:
            arg.append([])
        rows = arg[1][0].split('%')
        row_num = 0
        if make:
            resize_x = max(len(rows[0]) + offset[0], self.get_width())
            resize_y = max(len(rows) + offset[1], self.get_height())
        else:
            resize_x = len(rows[0]) + offset[0]
            resize_y = len(rows) + offset[1]
        self.resize(resize_x, resize_y)
        for y in rows:
            col_num = 0
            for terrain in y:
                self.tiles[row_num + offset[1]][col_num + offset[0]].set_terrain(terrain)
                col_num += 1
            row_num += 1
        if make:
            for prop in self.population.get_all():
                if offset[0] <= prop.pos.x < offset[0] + len(rows[0])\
                        and offset[1] <= prop.pos.y < offset[1] + len(rows):
                    prop.remove()
        objects = []
        for i in arg[2]:
            obj = Stock.get(self, i[2], i)
            obj.relocate(to=obj.pos.get_neighbor(offset[0], offset[1]), force=True)
            obj.add()
            objects.append(obj)
        return objects

    def process_terrain(self):
        for y in self.tiles:
            for x in y:
                x.connect()
                x.update_shader()

    def get_width(self):
        return len(self.tiles[0])

    def get_height(self):
        return len(self.tiles)

    def get_tile(self, x, y, limit=False):
        if self.is_inbound(x, y):
            return self.tiles[y][x]
        elif limit:
            x = max(0, min(self.get_width() - 1, x))
            y = max(0, min(self.get_height() - 1, y))
            return self.tiles[y][x]

    def is_inbound(self, x, y):
        return 0 <= x < self.get_width() and 0 <= y < self.get_height()

    def get_tile_from_vec(self, x, y):
        x = math.floor(x / Global.BLOCK)
        y = math.floor(y / Global.BLOCK)
        return self.get_tile(x, y, limit=True)

    def collide_line(self, x1, y1, x2, y2, function, distance=-1):
        degree = math.atan2(y2 - y1, x2 - x1)
        current = [x1 * Global.BLOCK + Global.HALF_BLOCK, y1 * Global.BLOCK + Global.HALF_BLOCK]
        prev_tile = self.get_tile(x1, y1, limit=True)
        while distance != 0 and (prev_tile.x != x2 or prev_tile.y != y2):
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

    def collide_land(self, pos1, pos2, flag, distance=-1, return_prev=True):
        def fn(prev, tile):
            if tile:
                is_int = isinstance(flag, int)
                if (is_int and tile.get_solidity() >= flag) or (not is_int and tile.is_land(flag)):
                    if return_prev:
                        return prev
                    else:
                        return tile
        return self.collide_line(pos1.x, pos1.y, pos2.x, pos2.y, fn, distance)

    def flip(self, flip_x, flip_y):
        if flip_y:
            self.tiles.reverse()
        if flip_x:
            r = []
            for y in self.tiles:
                r.append(y[::-1])
            self.tiles = r

    def mirror_axis(self):
        copy = []
        for x in self.tiles[0]:
            copy.append([None] * self.get_height())
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                copy[x][y] = self.tiles[y][x]
        self.tiles = copy

    def update_objects(self):
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                self.tiles[y][x].x = x
                self.tiles[y][x].y = y
                for thing in self.tiles[y][x].things:
                    thing.update_vec()

    def rotate(self, times):
        if times == 1:  # clockwise 90
            self.mirror_axis()
            self.flip(1, 0)
        elif times == 2:  # 180
            self.flip(1, 1)
        elif times == 3:  # counter clockwise 90
            self.mirror_axis()
            self.flip(0, 1)
        else:  # 0
            return
        self.update_objects()

    def resize(self, new_x, new_y):
        new = []
        for y in range(new_y):
            row = []
            for x in range(new_x):
                if self.is_inbound(x, y):
                    row.append(self.tiles[y][x])
                else:
                    row.append(Tile(self, '?', x, y))
            new.append(row)
        self.tiles = new

    def on_sleep(self, time):
        for i in self.population.get_all():
            i.on_sleep(time)
