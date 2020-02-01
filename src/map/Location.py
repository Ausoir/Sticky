import math

from src.entity.Sound import Sound
from src.entity.Space import Space
from src.entity.Stock import Stock
from src.game import Global
from src.game.Turn import Turn
from src.map.Terrain import Terrain
from src.map.Tile import Tile
from src.tools.Data import Data
from src.tools.List import List


class Location:
    @staticmethod
    def make(target, alias, overwrite=True):
        if overwrite or not Data.is_file('data/save/' + target + '.map'):
            r = Location(alias, list(Data.process_raw(Data.read('data/map/' + target + '.map'))))
            from src.entity.Other import Scripter
            for obj in r.record.copy():
                if isinstance(obj, Scripter):
                    obj.trigger_make()
            r.save()

    def __init__(self, name, data):
        Stock.location = self
        Turn.add(self.turn)
        from src.entity.Field import Field
        self.seed = 0
        self.identity = 0
        self.name = name
        self.update_frame = 0
        self.attack = Field()
        self.sound = Sound(self)
        self.delay = 8
        self.tiles = {}
        self.edge = 0
        self.record = List()
        self.header = None
        self.load(data)

    def __str__(self):
        high_x = -9999
        high_y = -9999
        low_x = 9999
        low_y = 9999
        for k, v in self.tiles.items():
            if v.terrain or v.things:
                params = k.split(',')
                x = int(params[0])
                y = int(params[1])
                if x < low_x:
                    low_x = x
                if x > high_x:
                    high_x = x
                if y < low_y:
                    low_y = y
                if y > high_y:
                    high_y = y
        size = '[' + ','.join([str(low_x), str(low_y), str(high_x - low_x), str(high_y - low_y)]) + ']'
        meta = str(self.seed) + ',' + size + ',' + self.header[2]
        rt = []
        for tile in self.tiles.values():
            if tile.terrain:
                rt.append(tile.__str__())
        tiles = ','.join(rt)
        r = []
        for i in self.record:
            r.append('['+i.__str__()+']')
        objects = ','.join(r)
        return meta + '\n' + tiles + '\n' + objects + '\n'

    def load(self, arg):
        while len(arg) < 3:
            arg = arg + [[]]
        self.header = arg[0]
        self.seed = arg[0][0]
        self.load_map(arg)

    def remove(self, arg):
        if arg in self.record:
            self.record.remove(arg)

    def turn(self):
        if not self.delay:
            self.delay = 400
            self.save()

    def save(self):
        Data.write('../save/' + self.name + '.map', self.__str__())

    def load_map(self, arg, new=False, offset=(0, 0), flip=False):
        tile_data = Data.get_cache('tiles')
        middle = 0
        if flip:
            if arg[1]:
                lowest = arg[1][0][0][0]
                highest = lowest
            else:
                lowest = arg[2][0][1][0]
                highest = lowest
            for i in arg[1]:
                if i[0][0] < lowest:
                    lowest = i[0][0]
                elif i[0][0] > highest:
                    highest = i[0][0]
            for i in arg[2]:
                if i[1][0] < lowest:
                    lowest = i[1][0]
                elif i[1][0] > highest:
                    highest = i[1][0]
            middle = int((highest - lowest) / 2)
        for i in arg[1]:
            data = tile_data[i[2]]
            if flip:
                tile = self.get_tile(((middle - i[0] - middle) + offset[0], i[1] + offset[1]))
            else:
                tile = self.get_tile((i[0] + offset[0], i[1] + offset[1]))
            tile.terrain = Terrain(i[2], data[0], data[1], data[2], data[3])
            if tile.y > self.edge:
                self.edge = tile.y
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        for i in self.tiles.values():
            if i.terrain and i.terrain.type == 1:
                for k, neighbors in enumerate(directions):
                    tile = self.get_tile((i.x + neighbors[0], i.y + neighbors[1]), create=False)
                    if tile and tile.terrain and tile.terrain.type == 2:
                        i.terrain.joint_neighbors[k] = 1
        objects = []
        for i in arg[2]:
            obj = Stock.get(i[2], i, loc=self)
            if new:
                obj.id = self.get_id()
            if flip:
                obj.relocate((middle - obj.pos.x - middle) + offset[0], obj.pos.y + offset[1], force=1)
            else:
                obj.relocate(obj.pos.x + offset[0], obj.pos.y + offset[1], force=1)
            obj.add()
            objects.append(obj)
        return objects

    def get_id(self):
        self.identity += 1
        return '#' + str(format(self.identity, 'x'))

    def get_object(self, oid):
        for i in self.record:
            if i.id == oid:
                return i
        return None

    def get_tile(self, arg, create=True):
        Space.reusable.load(arg)
        pos = Space.reusable.to_int()
        key = str(pos.x) + ',' + str(pos.y)
        if key not in self.tiles:
            if not create:
                return None
            self.tiles[key] = Tile(self, pos.x, pos.y)
        return self.tiles[key]

    def get_tile_from_vec(self, x, y):
        x = math.floor(x / Global.BLOCK)
        y = math.floor(y / Global.BLOCK)
        return self.get_tile([x, y])

    def collide_line(self, x1, y1, x2, y2, function, distance=10):
        degree = math.atan2(y2 - y1, x2 - x1)
        current = [x1 * Global.BLOCK + Global.HALF_BLOCK, y1 * Global.BLOCK + Global.HALF_BLOCK]
        prev_tile = self.get_tile([x1, y1])
        while distance > 0 and (prev_tile.x != x2 or prev_tile.y != y2):
            distance -= 1
            current[0] = current[0] + math.cos(degree) * Global.BLOCK
            current[1] = current[1] + math.sin(degree) * Global.BLOCK
            tile = self.get_tile_from_vec(current[0], current[1])
            r = function(prev_tile, tile)
            if r:
                return r
            prev_tile = tile
        return prev_tile

    def collide_land(self, pos1, pos2, flag, distance=10):
        def fn(prev, tile):
            if tile.is_land(flag):
                return prev
        return self.collide_line(pos1.x, pos1.y, pos2.x, pos2.y, fn, distance)

    def get_area(self, center_tile, range_x, range_y):
        tiles = []
        for x in range(-range_x, range_x+1):
            for y in range(-range_y, range_y+1):
                tile = self.get_tile(center_tile + (x, y), create=0)
                if tile:
                    tiles.append(tile)
        return tiles
