from src.entity.Stock import Stock
from src.game import Global
from src.tools.Data import Data


class Mercenary:
    def __init__(self):
        self.npc = []

    def __str__(self):
        return ','.join(self.npc)

    def make(self):
        mercenaries = Data.read('Data/raw/mercenaries.txt').split('\n')
        for i in range(24):
            if len(mercenaries) == 0:
                break
            else:
                rand_merc = mercenaries.pop(Global.r.rand_int(0, len(mercenaries) - 1))
                if rand_merc:
                    self.npc.append(rand_merc.split(',')[0])

    def load(self, data):
        for line in data:
            self.npc.append(line)

    def spawn(self, o_x, o_y):
        if self.npc and Global.r.rand_int(1, 16) == 1:
            x = Global.r.rand_int(o_x, o_x + Global.world.CHUNK - 1)
            y = Global.r.rand_int(o_y, o_y + Global.world.CHUNK - 1)
            tile = Global.world.location.get_tile(x, y)
            if tile and tile.get_yield() > -8 and not tile.things and not tile.is_seen():
                npc = self.npc.pop()
                npc = Stock.get(npc)
                npc.pos = tile
                npc.add()
                return npc
