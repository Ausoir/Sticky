from src.entity.Space import Space
from src.entity.Stock import Stock
from src.game import Global
from src.game.Turn import Turn
from src.map.Terrain import Terrain
from src.map.Tile import Tile
from src.tools.Data import Data
from src.tools.List import List
from src.tools.Math import Math


# Handles both map and save functions
class Location:
    def __init__(self, data):
        Turn.queue.append(self)
        from src.entity.unit.action.Attack import Attack
        self.name = data[0]
        self.attack = Attack()
        self.delay = 0
        self.tiles = {}
        self.record = List()
        self.load(Data.process_raw(Data.read('save/'+data[0]+'.map')))

    def __str__(self):
        ry = []
        for k, v in self.tiles.items():
            rx = []
            for k2, v2 in v.items():
                tile = v2.__str__()
                if tile:
                    rx.append(tile)
            if rx:
                ry.append(','.join(rx))
        tiles = ','.join(ry)

        r = []
        for i in self.record:
            r.append('['+i.__str__()+']')
        objects = ','.join(r)
        return tiles + '\n' + objects + '\n'

    def load(self, arg):
        for i in arg[0]:
            x = i[0][0]
            y = i[0][1]
            tile = self.get_tile(x, y)
            tile.terrain = Terrain.load(tile * [Global.BLOCK, Global.BLOCK], i[1])
        for i in arg[1]:
            obj = Stock.get(i[1], self)
            obj.load(i)
            obj.add()

    def remove(self, arg):
        if arg in self.record:
            self.record.remove(arg)

    def turn(self):
        Data.write('save/map.map', self.__str__())

    def draw(self, surface):
        for k, v in self.tiles.items():
            for k2, v2 in v.items():
                v2.draw(surface)

    def draw_objects(self, surface):
        for k, v in self.tiles.items():
            for k2, v2 in v.items():
                v2.draw_objects(surface)

    def get_tile(self, x=None, y=None, create=1):
        if y:
            tmp = Space(x, y)
        else:
            tmp = Space(x)
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
        return self.get_tile(int(x / Global.BLOCK), int(y / Global.BLOCK))

    def collide_line(self, vec_from, x, y, max=-1, flag=Tile.CHECK_TERRAIN):
        target_pos = vec_from + (x, y)
        degree = Space(x, y).get_atan()
        current = ((vec_from * Global.BLOCK)+(Global.BLOCK/2, Global.BLOCK/2)).to_list()
        prev_tile = vec_from
        while max and (prev_tile.x != target_pos.x or prev_tile.y != target_pos.y):
            max -= 1
            current = [current[0] - Math.cos(degree)*Global.BLOCK, current[1] + Math.sin(degree)*Global.BLOCK]
            tile = self.get_tile_from_vec(current[0], current[1])
            if tile.is_land(flag):
                return prev_tile
            prev_tile = tile
        return prev_tile
