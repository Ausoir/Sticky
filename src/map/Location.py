import math

from src.entity.Sound import Sound
from src.entity.Space import Space
from src.entity.Stock import Stock
from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Terrain import Terrain
from src.map.Tile import Tile
from src.tools.Data import Data
from src.tools.List import List
from src.tools.Math import Math


# Handles both map and save functions
from src.tools.Random import Random


class Location:
    @staticmethod
    def make(target, alias, overwrite=True):
        if overwrite or not Data.is_file('data/save/' + target + '.map'):
            r = Location(alias, list(Data.process_raw(Data.read('data/map/' + target + '.map'))))
            from src.entity.Other import Script
            for obj in r.record.copy():
                if isinstance(obj, Script):
                    obj.trigger_make()
            r.save()

    def __init__(self, name, data):
        Stock.location = self
        Turn.add(self.turn)
        from src.entity.Field import Field
        self.seed = 0
        self.identity = 0
        self.name = name
        self.draw_frame = 0
        self.update_frame = 0
        self.attack = Field()
        self.sound = Sound(self)
        self.delay = 8
        self.tiles = {}
        self.edge = 0
        self.record = List()
        self.header = None
        self.draw_tiles = {}
        self.sight_block = [Tile.COLLIDE_FOG, Tile.COLLIDE_PROP, Tile.COLLIDE_TERRAIN]
        self.last_pos = None
        self.load(data)
        self.sight_range = 12
        self.view_range = 12
        self.display_tiles_x = None
        self.display_tiles_y = None
        self.sight_tiles = []
        self.resize()

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
            self.delay = 40
            # self.save()
        self.update_frame += 1
        self.update_fog()

    def draw(self, surface):
        self.draw_frame += 1
        terrains = []
        objects = [[], [], [], [], [], []]
        tiles = self.draw_tiles.values()
        for v in tiles:
            tile_type = v.get_depth()
            if tile_type == 1:
                if v.terrain.background:
                    v.draw_background(surface)
                v.draw(surface)
            elif tile_type == 0:
                v.draw_background(surface)
            else:
                if v.terrain.background:
                    v.draw_background(surface)
                terrains.append(v)
            for thing in v.things:
                objects[thing.depth - 1].append(thing)
        for depth in objects:
            for i in depth:
                i.draw(surface)
        for i in terrains:
            i.draw(surface)
        for v in tiles:
            v.draw_overlay(surface)

    def save(self):
        Data.write('save/' + self.name + '.map', self.__str__())

    def resize(self):
        self.display_tiles_x = min(int(Global.SCREEN_TILES[0] / 2), self.sight_range)
        self.display_tiles_y = min(int(Global.SCREEN_TILES[1] / 2), int(self.sight_range * .7))
        self.sight_tiles = [[], []]
        for x in range(-self.display_tiles_x, self.display_tiles_x + 1):
            for y in range(-self.display_tiles_y, 0):
                self.sight_tiles[0].append([x, y])
            for y in range(self.display_tiles_y + 1):
                if y != 0 or x != 0:
                    self.sight_tiles[1].append([x, y])

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
            data = tile_data[i[1]]
            if flip:
                tile = self.get_tile(((middle - i[0][0] - middle) + offset[0], i[0][1] + offset[1]))
            else:
                tile = self.get_tile((i[0][0] + offset[0], i[0][1] + offset[1]))
            tile.terrain = Terrain(i[1], tile * Global.BLOCK, data[0], data[1], data[2], data[3], data[4], data[5])
            if tile.y > self.edge:
                self.edge = tile.y
        objs = []
        for i in arg[2]:
            obj = Stock.get(i[2], i, loc=self)
            if new:
                obj.id = self.get_id()
            if flip:
                obj.relocate((middle - obj.pos.x - middle) + offset[0], obj.pos.y + offset[1], force=1)
            else:
                obj.relocate(obj.pos.x + offset[0], obj.pos.y + offset[1], force=1)
            obj.add()
            objs.append(obj)
        return objs

    def spawn_mobs(self, number, mob_list, rand=None, spawns=None):
        if number > 0:
            if not rand:
                rand = Random()
            if not spawns:
                spawns = []
            tiles = []
            for i in self.tiles.values():
                if i.terrain and i.is_land(Tile.CHECK_FIRM):
                    tiles.append(i)
            for i in tiles:
                above = self.get_tile(i + (0, -1))
                if above.terrain and not above.is_land(Tile.CHECK_FIRM):
                    spawns.append(above)
            overlaps = []
            if spawns:
                for i in range(number):
                    index = rand.rand_int(0, len(spawns) - 1)
                    pos = spawns[index]
                    overlaps.append(spawns.pop(index))
                    if len(spawns) == 0:
                        spawns = overlaps
                    mob = rand.rand_list(mob_list)
                    if mob:
                        Stock.make(mob, pos)

    def update_fog(self):
        x = Camera.target.pos.x
        y = Camera.target.pos.y
        center = self.get_tile(Camera.target.pos)
        center.update(self)
        self.draw_tiles = {str(x) + ',' + str(y): center}
        direction = Global.player.character.direction
        start = [x * Global.BLOCK + Global.HALF_BLOCK + (Global.HALF_BLOCK * direction) - direction,
                 y * Global.BLOCK + Global.BLOCK - 1]
        view_y = int(self.view_range * .7)
        for i in self.sight_tiles[0]:
            sight = self.collide_sight(start, i)
            if sight:
                sight.update(self)
                if (abs(sight.x - x) < self.view_range and abs(sight.y - y) < view_y) or sight.light:
                    self.draw_tiles[str(sight.x) + ',' + str(sight.y)] = sight
        start[1] = y * Global.BLOCK + 1
        for i in self.sight_tiles[1]:
            sight = self.collide_sight(start, i)
            if sight:
                sight.update(self)
                if (abs(sight.x - x) < self.view_range and abs(sight.y - y) < view_y) or sight.light:
                    self.draw_tiles[str(sight.x) + ',' + str(sight.y)] = sight

    def get_id(self):
        self.identity += 1
        return '#' + str(format(self.identity, 'x'))

    def get_object(self, oid):
        for i in self.record:
            if i.id == oid:
                return i
        return None

    def get_tile(self, arg, create=1):
        Space.reusable.load(arg)
        pos = Space.reusable.to_int()
        key = str(pos.x) + ',' + str(pos.y)
        if key not in self.tiles:
            if not create:
                return None
            self.tiles[key] = Tile(pos.x, pos.y)
        return self.tiles[key]

    def get_tile_from_vec(self, x, y):
        return self.get_tile([Location.get_pos_from_vec(x), Location.get_pos_from_vec(y)])

    @staticmethod
    def get_pos_from_vec(i):
        return math.floor(i / Global.BLOCK)

    def collide_line(self, vec_from, x, y, function, distance=10):
        space = Space(x, y)
        target_pos = vec_from + space
        degree = space.get_atan()
        current = ((vec_from * Global.BLOCK) + (Global.BLOCK / 2, Global.BLOCK / 2)).to_list()
        prev_tile = vec_from
        while distance > 0 and (prev_tile.x != target_pos.x or prev_tile.y != target_pos.y):
            distance -= 1
            current = [current[0] + Math.cos(degree) * Global.BLOCK, current[1] + Math.sin(degree) * Global.BLOCK]
            tile = self.get_tile_from_vec(current[0], current[1])
            r = function(prev_tile, tile)
            if r:
                return r
            prev_tile = tile
        return prev_tile

    def collide_land(self, vec_from, x, y, flag, distance=10):
        def fn(prev, tile):
            if tile.is_land(flag):
                return prev
        return self.collide_line(vec_from, x, y, fn, distance)

    def collide_sight(self, vec_from, tile_to):
        abs_x = abs(tile_to[0])
        abs_y = abs(tile_to[1])
        if abs_x >= abs_y:
            sign = 1 if tile_to[0] >= 0 else -1
            if tile_to[1] == 0:
                slope = [abs_x, Global.BLOCK * sign, 0]
            else:
                slope = [abs_x, Global.BLOCK * sign, tile_to[1] / abs_x * Global.BLOCK]
        else:
            sign = 1 if tile_to[1] >= 0 else -1
            if tile_to[0] == 0:
                slope = [abs_y, 0, Global.BLOCK * sign]
            else:
                slope = [abs_y, tile_to[0] / abs_y * Global.BLOCK, Global.BLOCK * sign]
        distance = slope[0]
        current = vec_from
        tile_from = None
        while distance > 0:
            distance -= 1
            current = [current[0] + slope[1], current[1] + slope[2]]
            tile_from = self.get_tile_from_vec(current[0], current[1])
            if tile_from.is_land(self.sight_block) and distance > 0:
                return None
        return tile_from

    def get_area(self, center_tile, range_x, range_y):
        tiles = []
        for x in range(-range_x, range_x+1):
            for y in range(-range_y, range_y+1):
                tile = self.get_tile(center_tile + (x, y), create=0)
                if tile:
                    tiles.append(tile)
        return tiles
