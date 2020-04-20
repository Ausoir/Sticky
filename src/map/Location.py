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
    def __init__(self, name, data, make=False):
        self.name = name
        self.tags = Tag()
        self.tags.set('name', name)
        self.identity = 0
        self.update_frame = 0
        self.field = Field(self)
        self.sound = Sound(self)
        self.population = Population()
        self.tiles = [[]]
        self.push_status = [0, 0]
        self.header = None
        if data:
            self.tags.load(data[0][0])
            if make:
                seed = self.tags.get('seed', 0)
                if seed == -1:
                    self.tags.set('seed', Global.r.rand_int(1, 9999))
            self.load(data, make)
        Turn.add(self.field.turn)

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

    def save(self):
        Data.write('save/' + self.name + '.map', self.__str__())

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
            if not make:
                obj.id = self.get_id()
            obj.relocate(to=obj.pos.get_neighbor(offset[0], offset[1]), force=True)
            obj.add()
            objects.append(obj)
        if make:
            from src.entity.Other import Scripter
            for i in objects:
                if isinstance(i, Scripter):
                    i.run_make()
        return objects

    def process_terrain(self):
        for y in self.tiles:
            for x in y:
                x.connect()
                x.update_shader()

    def get_id(self):
        self.identity += 1
        return '#' + str(format(self.identity, 'x'))

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

    def collide_line(self, x1, y1, x2, y2, function, distance=10):
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
            enter_y = self.tags.get('entery')
            if enter_y is not None:
                self.tags.set('entery', self.get_height() - 1 - enter_y)
        if flip_x:
            r = []
            for y in self.tiles:
                r.append(y[::-1])
            self.tiles = r
            enter_x = self.tags.get('enterx')
            if enter_x is not None:
                self.tags.set('enterx', self.get_width() - 1 - enter_x)

    def mirror_axis(self):
        copy = []
        for x in self.tiles[0]:
            copy.append([None] * self.get_height())
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                copy[x][y] = self.tiles[y][x]
        self.tiles = copy
        enter_x = self.tags.get('enterx', 0)
        enter_y = self.tags.get('entery', 0)
        self.tags.set('enterx', enter_y, add=False)
        self.tags.set('entery', enter_x, add=False)

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

    def push_horizontal(self, left=0, right=0, offset=0):
        new = []
        for y in range(self.get_height()):
            row = []
            for x in range(left):
                row.append(Tile(self, '.', x, y))
            for x in range(20):
                row.append(self.tiles[y][x + offset])
            for x in range(right):
                row.append(Tile(self, '.', x, y))
            new.append(row)
        self.tiles = new

    def push_vertical(self, up=0, down=0, offset=0):
        new = []
        for y in range(up):
            row = []
            for x in range(self.get_width()):
                row.append(Tile(self, '.', x, y))
            new.append(row)
        for y in range(20):
            row = []
            for x in range(self.get_width()):
                row.append(self.tiles[y + offset][x])
            new.append(row)
        for y in range(down):
            row = []
            for x in range(self.get_width()):
                row.append(Tile(self, '.', x, y))
            new.append(row)
        self.tiles = new

    def push_cell(self, pos):
        cell_x = self.tags.get('x', 0)
        cell_y = self.tags.get('y', 0)
        if pos.x <= 9:
            self.push_horizontal(left=20)
            if self.push_status[1] == -1:
                topleft = Data.process_raw(Data.read('save/topleft.map'))
                left = Data.process_raw(Data.read('save/left.map'))
                self.update_objects()
                self.load(topleft, make=True)
                self.load(left, offset=[0, 20], make=True)
            elif self.push_status[1] == 1:
                botleft = Data.process_raw(Data.read('save/botleft.map'))
                left = Data.process_raw(Data.read('save/left.map'))
                self.update_objects()
                self.load(left, make=True)
                self.load(botleft, offset=[0, 20], make=True)
            else:
                data1 = Data.process_raw(Data.read('save/left.map'))
                self.update_objects()
                self.load(data1, make=True)
            self.push_status[0] = -1
        elif pos.y <= 9:
            self.push_vertical(up=20)
            if self.push_status[0] == -1:
                data1 = Data.process_raw(Data.read('save/top.map'))
                data2 = Data.process_raw(Data.read('save/topleft.map'))
                self.update_objects()
                self.load(data1, offset=[20, 0], make=True)
                self.load(data2, make=True)
            elif self.push_status[0] == 1:
                data1 = Data.process_raw(Data.read('save/top.map'))
                data2 = Data.process_raw(Data.read('save/topright.map'))
                self.update_objects()
                self.load(data1, make=True)
                self.load(data2, offset=[-20, 0], make=True)
            else:
                data1 = Data.process_raw(Data.read('save/top.map'))
                self.update_objects()
                self.load(data1, make=True)
            self.push_status[1] = -1
        elif pos.x >= self.get_width() - 9:
            self.push_horizontal(right=20, offset=-20)
            if self.push_status[1] == -1:
                topright = Data.process_raw(Data.read('save/topright.map'))
                right = Data.process_raw(Data.read('save/right.map'))
                self.update_objects()
                self.load(topright, offset=[20, 0], make=True)
                self.load(right, offset=[20, 20], make=True)
            elif self.push_status[1] == 1:
                botright = Data.process_raw(Data.read('save/botright.map'))
                right = Data.process_raw(Data.read('save/right.map'))
                self.update_objects()
                self.load(botright, offset=[20, 20], make=True)
                self.load(right, offset=[20, 0], make=True)
            else:
                right = Data.process_raw(Data.read('save/right.map'))
                self.update_objects()
                self.load(right, offset=[20, 0], make=True)
            self.push_status[0] = 1
        elif pos.y >= self.get_height() - 9:
            self.push_vertical(down=20, offset=-20)
            if self.push_status[0] == -1:
                data1 = Data.process_raw(Data.read('save/bot.map'))
                data2 = Data.process_raw(Data.read('save/botleft.map'))
                self.update_objects()
                self.load(data1, offset=[20, 20], make=True)
                self.load(data2, offset=[0, 20], make=True)
            elif self.push_status[0] == 1:
                data1 = Data.process_raw(Data.read('save/bot.map'))
                data2 = Data.process_raw(Data.read('save/botright.map'))
                self.update_objects()
                self.load(data1, offset=[0, 20], make=True)
                self.load(data2, offset=[-20, 20], make=True)
            else:
                data1 = Data.process_raw(Data.read('save/bot.map'))
                self.update_objects()
                self.load(data1, offset=[0, 20], make=True)
            self.push_status[1] = 1
        else:
            return False
        return True
