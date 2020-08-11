import os

from src.entity.Stock import Stock, Global
from src.tools.Data import Data


class Mercenary:
    def __init__(self):
        self.npc = []
        self.coords = []

    def __str__(self):
        r = []
        for i in range(len(self.npc)):
            if self.coords[i]:
                coords = '[' + str(self.coords[i][0]) + ',' + str(self.coords[i][1]) + ']'
            else:
                coords = '[]'
            r.append(coords + ',[' + self.npc[i].__str__() + ']')
        return '\n'.join(r)

    def make(self):
        return
        mercenaries = Data.read('Data/raw/mercenaries.txt').split('\n')
        for i in range(24):
            if len(mercenaries) == 0:
                break
            else:
                rand_merc = mercenaries.pop(Global.r.rand_int(0, len(mercenaries) - 1))
                if rand_merc:
                    rand_merc = Data.parse(rand_merc)
                    npc = Stock.get(Global.world.location, rand_merc[1], [[0, 0]] + rand_merc)
                    self.npc.append(npc.__str__())
                    npc.remove()
                    new_coord = Global.r.rand_list(os.listdir(Data.direct('data/map')))
                    self.coords.append([int(x) for x in new_coord[1:-4].split('y')])

    def load(self, data, c_x, c_y):
        for line in data:
            npc = Stock.get(Global.world.location, line[1][1], line[1])
            if abs(line[0][0] - c_x) < 2 and abs(line[0][1] - c_y) < 2:
                self.npc.append(npc)
            else:
                self.npc.append(npc.__str__())
                npc.remove()
            self.coords.append(line[0])

    def spawn(self, c_x, c_y, o_x, o_y):
        r = []
        for i in range(len(self.npc)):
            if self.coords[i] and self.coords[i][0] == c_x and self.coords[i][1] == c_y:
                if isinstance(self.npc[i], str):
                    data = Data.parse(self.npc[i])
                    self.npc[i] = Stock.get(Global.world.location, data[1], data)
                    x = Global.r.rand_int(o_x, o_x + Global.world.CHUNK)
                    y = Global.r.rand_int(o_y, o_y + Global.world.CHUNK)
                    tile = Global.world.location.get_tile(x, y, limit=True)
                    if tile.get_yield() > -8:
                        # print('spawn ' + str(self.npc[i]))
                        self.npc[i].pos = tile
                        self.npc[i].add()
                else:
                    self.npc[i].add()
                    r.append(self.npc[i])
                self.npc[i].save = False
        return r

    def update(self, c_x, c_y, force=False):
        for i in range(len(self.npc)):
            if force or (self.coords[i][0] == c_x and self.coords[i][1] == c_y):
                if not isinstance(self.npc[i], str):
                    if self.npc[i].pos.is_seen():
                        continue
                    data = self.npc[i].__str__()
                    self.npc[i].remove()
                    self.npc[i] = data
                new_coord = Global.r.rand_list(os.listdir(Data.direct('data/map')))
                if new_coord.startswith('x'):
                    self.coords[i] = [int(x) for x in new_coord[1:-4].split('y')]
                    # print('offload to ' + str(self.coords[i]))
