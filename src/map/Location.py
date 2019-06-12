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
    OBJECT_ID = 0

    def __init__(self, name, data):
        Stock.location = self
        Turn.add(self)
        from src.entity.Field import Field
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
        self.display_tiles_x = None
        self.display_tiles_y = None
        self.sight_tiles = []
        self.resize()

    def __str__(self):
        meta = str(Turn.frame) + ',' + str(Location.OBJECT_ID) + ',' + self.header[2] + ',' + self.header[3]
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
        Turn.frame = arg[0][0]
        Location.OBJECT_ID = arg[0][1]
        from src.map import Script
        script = getattr(Script, arg[0][2])
        objects = self.load_map(arg)
        for i in script(arg[0][3], self, objects):
            i.add()

    def load_map(self, arg, new=False, offset=(0, 0)):
        tiles = Data.get_cache('tiles')
        for i in arg[1]:
            data = tiles[i[1]]
            tile = self.get_tile((i[0][0] + offset[0], i[0][1] + offset[1]))
            tile.terrain = Terrain(i[1], tile * Global.BLOCK, data[0], data[1], data[2], data[3], data[4])
            if tile.y > self.edge:
                self.edge = tile.y
        objects = []
        for i in arg[2]:
            obj = Stock.get(i[2], i)
            if new:
                obj.id = self.get_id()
            obj.relocate(obj.pos[0].x + offset[0], obj.pos[0].y + offset[1], force=1)
            objects.append(obj)
        return objects

    def resize(self):
        self.display_tiles_x = min(int(Global.SCREEN_TILES[0] / 2), 14)
        self.display_tiles_y = min(int(Global.SCREEN_TILES[1] / 2), 7)
        self.sight_tiles = []
        for x in range(-self.display_tiles_x, self.display_tiles_x + 1):
            for y in range(-self.display_tiles_y, self.display_tiles_y + 1):
                if y != 0 or x != 0:
                    self.sight_tiles.append([x, y])

    def remove(self, arg):
        if arg in self.record:
            self.record.remove(arg)

    def turn(self):
        if not self.delay:
            self.delay = 40
            Data.write('save/' + self.name + '.map', self.__str__())
        self.update_fog()

    def update_fog(self):
        x = Camera.target.pos[0].x
        y = Camera.target.pos[0].y
        self.draw_tiles = {str(x) + ',' + str(y): self.get_tile(Camera.target.pos[0])}
        direction = Global.main.player.character.direction
        start = (x * Global.BLOCK + Global.HALF_BLOCK + (direction*Global.HALF_BLOCK - direction), y * Global.BLOCK + 1)
        for i in self.sight_tiles:
            sight = self.collide_sight(start, i)
            if sight:
                self.draw_tiles[str(sight.x) + ',' + str(sight.y)] = sight

    def draw(self, surface):
        objects = [[], [], [], [], [], []]
        for k, v in self.draw_tiles.items():
            v.draw(surface)
            for thing in v.things:
                objects[thing.depth - 1].append(thing)
        for depth in objects:
            for i in depth:
                i.draw(surface)

    @staticmethod
    def get_id():
        Location.OBJECT_ID += 1
        return '#' + str(format(Location.OBJECT_ID, 'x'))

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
        if abs_x > abs_y:
            sign = 1 if tile_to[0] >= 0 else -1
            if tile_to[1] == 0:
                slope = [abs_x, Global.BLOCK * sign, 0]
            else:
                slope = [abs_x, Global.BLOCK * sign, tile_to[1] / tile_to[0] * Global.BLOCK]
        else:
            sign = 1 if tile_to[1] >= 0 else -1
            if tile_to[0] == 0:
                slope = [abs_y, 0, Global.BLOCK * sign]
            else:
                slope = [abs_y, tile_to[0] / tile_to[1] * Global.BLOCK, Global.BLOCK * sign]
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

    def get_routes(self, pos):
        options = []
        right = self.get_tile(pos + (1, 0))
        upright = self.get_tile(pos + (1, -1))
        left = self.get_tile(pos + (-1, 0))
        upleft = self.get_tile(pos + (-1, -1))
        ground = self.get_tile(pos + (0, 1))
        air = self.get_tile(pos + (0, -1))
        if ground.is_land(Tile.CHECK_LANDABLE) or pos.is_climbable():
            if not air.is_land(Tile.CHECK_LARGE) and air.is_climbable():
                options.append((0, -1))
            if not right.is_land(Tile.CHECK_LARGE):
                if self.get_tile(pos + (1, 1)).is_land(Tile.CHECK_LANDABLE) or right.is_climbable():
                    options.append((1, 0))
                else:
                    options.append((1, 1))
            elif not upright.is_land(Tile.CHECK_LARGE):
                options.append((1, -1))
            if not left.is_land(Tile.CHECK_LARGE):
                if self.get_tile(pos + (-1, 1)).is_land(Tile.CHECK_LANDABLE) or left.is_climbable():
                    options.append((-1, 0))
                else:
                    options.append((-1, 1))
            elif not upleft.is_land(Tile.CHECK_LARGE):
                options.append((-1, -1))
            if not ground.is_land(Tile.CHECK_LARGE) and ground.is_climbable() and ground.y < self.edge:
                options.append((0, 1))
        else:
            options.append((0, 1))
        return options
