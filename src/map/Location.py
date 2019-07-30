import math

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
class Location:
    def __init__(self, name, data):
        Stock.location = self
        Turn.add(self)
        from src.entity.Field import Field
        self.type = 0
        self.identity = 0
        self.name = name
        self.attack = Field()
        self.delay = 8
        self.tiles = {}
        self.edge = 0
        self.record = List()
        self.header = None
        self.draw_tiles = {}
        self.sight_block = [Tile.COLLIDE_FOG, Tile.COLLIDE_PROP, Tile.COLLIDE_TERRAIN]
        self.last_pos = None
        self.load(data)
        self.sight_range = 7
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
        meta = str(self.type) + ',' + size + ',' + self.header[2]
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
        self.type = arg[0][0]
        self.load_map(arg)

    def remove(self, arg):
        if arg in self.record:
            self.record.remove(arg)

    def turn(self):
        if not self.delay:
            self.delay = 40
            self.save()
        self.update_fog()

    def draw(self, surface):
        objects = [[], [], [], [], [], []]
        for k, v in self.draw_tiles.items():
            v.draw(surface)
            for thing in v.things:
                objects[thing.depth - 1].append(thing)
        for depth in objects:
            for i in depth:
                i.draw(surface)

    def save(self):
        Data.write('save/' + self.name + '.map', self.__str__())

    def resize(self):
        self.display_tiles_x = min(int(Global.SCREEN_TILES[0] / 2), self.sight_range * 2)
        self.display_tiles_y = min(int(Global.SCREEN_TILES[1] / 2), self.sight_range)
        self.sight_tiles = [[], []]
        for x in range(-self.display_tiles_x, self.display_tiles_x + 1):
            for y in range(-self.display_tiles_y, 0):
                self.sight_tiles[0].append([x, y])
            for y in range(self.display_tiles_y + 1):
                if y != 0 or x != 0:
                    self.sight_tiles[1].append([x, y])

    def load_map(self, arg, new=False, offset=(0, 0)):
        tiles = Data.get_cache('tiles')
        for i in arg[1]:
            data = tiles[i[1]]
            tile = self.get_tile((i[0][0] + offset[0], i[0][1] + offset[1]))
            tile.terrain = Terrain(i[1], tile * Global.BLOCK, data[0], data[1], data[2], data[3], data[4])
            if tile.y > self.edge:
                self.edge = tile.y
        for i in arg[2]:
            obj = Stock.get(i[2], i)
            if new:
                obj.id = self.get_id()
            obj.relocate(obj.pos[0].x + offset[0], obj.pos[0].y + offset[1], force=1)
            obj.add()

    @staticmethod
    def construct_map(biome):
        from src.tools.Random import Random
        map_data = Data.get_line('data/map/map.txt', biome)
        rand = Random()
        terrain = map_data[2][rand.rand_int(0, len(map_data[2]) - 1)]
        r = Location('current', list(Data.process_raw(Data.read('data/map/' + terrain + '.map'))))
        buildings = []
        for i in map_data[3]:
            building = Data.process_raw(Data.read('data/map/' + i + '.map'))
            size = building[0][1]
            inserted = False
            for k, v in enumerate(buildings):
                if size[2] > v[0]:
                    buildings.insert(k, [size[2], size[3], i])
                    inserted = True
                    break
            if not inserted:
                buildings.append([size[2], size[3], i])
        estates = []
        for obj in r.record:
            if obj.name == 'Beacon' and obj.var == 'estate':
                estates.insert(rand.rand_int(0, len(estates)), obj)
        for estate in estates:
            for i in range(len(buildings)):
                building = rand.rand_list(buildings)
                bound = r.check_clearing(estate.pos[0].x, estate.pos[0].y)
                if building[0] < bound[0] and building[1] < bound[1]:
                    building_data = Data.process_raw(Data.read('data/map/' + building[2] + '.map'))
                    r.load_map(building_data, new=True, offset=estate.pos[0].to_list())
                    break
        shop_names = []
        shops = Data.process_raw(Data.read('data/raw/trade.txt'))
        for i in shops:
            shop_names.append(i[0])
        removal = []
        for obj in r.record:
            if obj.name == 'Beacon':
                removal.append(obj)
                if obj.var == 'treasure':
                    data = Data.get_line('data/raw/trade.txt', 'treasure')
                    Stock.make(rand.rand_list(data[1]), obj.pos[0])
                elif obj.var == 'mob':
                    for mob in rand.rand_list(map_data[5]):
                        Stock.make(mob, obj.pos[0])
                elif obj.var in shop_names:
                    data = Data.get_line('data/raw/trade.txt', obj.var)
                    merchandise = []
                    for i in range(rand.rand_int(3, 6)):
                        merchandise.append(rand.rand_list(data[1]))
                    shop = Stock.make('Merchant', obj.pos[0])
                    shop.var = ['shop'] + merchandise
        for i in removal:
            i.remove()
        if map_data[4] > 0:
            tiles = []
            for i in r.tiles.values():
                if i.terrain and i.is_land(Tile.CHECK_FIRM):
                    tiles.append(i)
            ftiles = []
            for i in tiles:
                above = r.get_tile(i + (0, -1))
                if above.terrain and not above.is_land(Tile.CHECK_FIRM):
                    ftiles.append(above)
            if ftiles:
                for i in range(map_data[4]):
                    index = rand.rand_int(0, len(ftiles) - 1)
                    pos = ftiles[index]
                    ftiles.pop(index)
                    for mob in rand.rand_list(map_data[5]):
                        Stock.make(mob, pos)
        if map_data[1]:
            r.name = map_data[0]
        r.save()
        return r

    def check_clearing(self, pos_x, pos_y):
        high_x = 14
        last_y = 0
        for y in range(5):
            last_y = y
            current_x = min(high_x, 10)
            for x in range(current_x + 1):
                if self.get_tile([pos_x + x, pos_y - y]).is_land(Tile.CHECK_FOUNDATION):
                    high_x = min(high_x, x) - 1
                    break
                if x != 0 and self.get_tile([pos_x - x, pos_y - y]).is_land(Tile.CHECK_FOUNDATION):
                    high_x = min(high_x, x) - 1
                    break
        if last_y == 4:
            for y in range(5, 14):
                block = self.get_tile([pos_x + high_x, pos_y - y]).is_land(Tile.CHECK_FOUNDATION)
                block = block or self.get_tile([pos_x - high_x, pos_y - y]).is_land(Tile.CHECK_FOUNDATION)
                block = block or self.get_tile([pos_x, pos_y - y]).is_land(Tile.CHECK_FOUNDATION)
                if block:
                    break
                last_y = y
        if last_y == 13:
            last_y = 40
        return [high_x * 2, last_y]

    def update_fog(self):
        x = Camera.target.pos[0].x
        y = Camera.target.pos[0].y
        self.draw_tiles = {str(x) + ',' + str(y): self.get_tile(Camera.target.pos[0])}
        direction = Global.main.player.character.direction
        start = [x * Global.BLOCK + Global.HALF_BLOCK + (Global.HALF_BLOCK * direction) - direction,
                 y * Global.BLOCK + Global.BLOCK - 1]
        for i in self.sight_tiles[0]:
            sight = self.collide_sight(start, i)
            if sight:
                self.draw_tiles[str(sight.x) + ',' + str(sight.y)] = sight
        start[1] = y * Global.BLOCK + 1
        for i in self.sight_tiles[1]:
            sight = self.collide_sight(start, i)
            if sight:
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

    def collide_land(self, vec_from, x, y, distance=10, flag=(Tile.COLLIDE_TERRAIN)):
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
