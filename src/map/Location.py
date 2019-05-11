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

    def __init__(self, data):
        Stock.location = self
        Turn.add(self)
        from src.entity.unit.action.Field import Field
        self.name = data[0]
        self.attack = Field()
        self.delay = 8
        self.tiles = {}
        self.edge = 0
        self.record = List()
        self.load(list(Data.process_raw(Data.read('save/'+data[0]+'.map'))))
        self.bg = [Data.run_cache('data/image/background/desert_1'),
                   Data.run_cache('data/image/background/desert_2')]
        for i in self.bg:
            i.resize(Global.DISPLAY)

    def __str__(self):
        meta = str(Turn.frame) + ',' + str(Location.OBJECT_ID)
        ry = []
        for tile_row in self.tiles.values():
            rx = []
            for tile in tile_row.values():
                if tile.terrain:
                    rx.append(tile.__str__())
            if rx:
                ry.append(','.join(rx))
        tiles = ','.join(ry)

        r = []
        for i in self.record:
            r.append('['+i.__str__()+']')
        objects = ','.join(r)
        return meta + '\n' + tiles + '\n' + objects + '\n'

    def load(self, arg):
        while len(arg) < 3:
            arg = arg + [[]]
        Turn.frame = arg[0][0]
        Location.OBJECT_ID = arg[0][1]
        tiles = Data.get_cache('tiles')
        for i in arg[1]:
            x = i[0][0]
            y = i[0][1]
            tile = self.get_tile(x, y)
            data = tiles[i[1]]
            tile.terrain = Terrain(i[1], tile * [Global.BLOCK, Global.BLOCK], data[0], data[1], data[2], data[3])
            if y > self.edge:
                self.edge = y
        for i in arg[2]:
            Stock.get(i[2], i).add()

    def remove(self, arg):
        if arg in self.record:
            self.record.remove(arg)

    def turn(self):
        if not self.delay:
            self.delay = 40
            Data.write('save/' + self.name + '.map', self.__str__())

    def draw(self, surface):
        rel = Camera.get_relative_tile_pos(Camera.pos[0], Camera.pos[1])
        mag = .1
        for i in self.bg:
            y = Global.CENTER[1] + 200 - Camera.pos[1] + max(-400/mag, min(1600, Camera.pos[1]))*mag*.5
            x = (Camera.pos[0]*mag) % Global.DISPLAY[0]
            i.draw(surface, x - Camera.pos[0], y)
            if x > -Global.CENTER[0]:
                i.draw(surface, x - Global.DISPLAY[0] - Camera.pos[0], y)
            if x < Global.CENTER[0]:
                i.draw(surface, x + Global.DISPLAY[0] - Camera.pos[0], y)
            mag *= 2
        depth_3 = []
        for k, v in self.tiles.items():
            if -rel[0] - Camera.sight[0] < k < -rel[0] + Camera.sight[0]:
                for k2, v2 in v.items():
                    if -rel[1] - Camera.sight[1] < k2 < -rel[1] + Camera.sight[1]:
                        if v2.terrain and v2.terrain.type > 0:
                            depth_3.append(v2)
                        else:
                            v2.draw(surface)
        for i in depth_3:
            i.draw(surface)

    @staticmethod
    def get_id():
        Location.OBJECT_ID += 1
        return '#' + str(format(Location.OBJECT_ID, 'x'))

    def get_object(self, id):
        for i in self.record:
            if i.id == id:
                return i
        return None

    def get_tile(self, x=None, y=None, create=1):
        if y is not None:
            tmp = Space(x, y).to_int()
        else:
            tmp = Space(x).to_int()
        if tmp.x not in self.tiles:
            if not create:
                return None
            self.tiles[tmp.x] = {}
        if tmp.y not in self.tiles[tmp.x]:
            if not create:
                return None
            self.tiles[tmp.x][tmp.y] = Tile(tmp.x, tmp.y)
        return self.tiles[tmp.x][tmp.y]

    def get_tile_from_vec(self, x, y):
        return self.get_tile(math.floor(x / Global.BLOCK), math.floor(y / Global.BLOCK))

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
        right = self.get_tile(pos.x + 1, pos.y)
        left = self.get_tile(pos.x - 1, pos.y)
        ground = self.get_tile(pos.x, pos.y + 1)
        air = self.get_tile(pos.x, pos.y - 1)
        if ground.is_land(Tile.CHECK_LANDABLE) or pos.is_climbable():
            if not air.is_land(Tile.CHECK_LARGE) and air.is_climbable():
                options.append((0, -1))
            if not right.is_land(Tile.CHECK_LARGE):
                if self.get_tile(pos.x + 1, pos.y + 1).is_land(Tile.CHECK_LANDABLE) or right.is_climbable():
                    options.append((1, 0))
                else:
                    options.append((1, 1))
            elif not self.get_tile(pos.x + 1, pos.y - 1).is_land(Tile.CHECK_LARGE):
                options.append((1, -1))
            if not left.is_land(Tile.CHECK_LARGE):
                if self.get_tile(pos.x - 1, pos.y + 1).is_land(Tile.CHECK_LANDABLE) or left.is_climbable():
                    options.append((-1, 0))
                else:
                    options.append((-1, 1))
            elif not self.get_tile(pos.x - 1, pos.y - 1).is_land(Tile.CHECK_LARGE):
                options.append((-1, -1))
            if not ground.is_land(Tile.CHECK_LARGE) and ground.is_climbable() and ground.y < self.edge:
                options.append((0, 1))
        else:
            options.append((0, 1))
        return options
