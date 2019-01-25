from src.game.Turn import Turn
from src.map.Tile import Tile


class Pilot:
    def __init__(self, host):
        Turn.queue.insert(0, self)
        self.host = host
        self.delay = 0

    def turn(self):
        self.dodge()
        # self.host.input('punch', self.host.location.get_tile(self.host.pos + (self.host.direction, 0)).to_list())

    def dodge(self):
        for i in self.host.location.attack.registry:
            if self.host.will_hit(i[1]):
                if not self.host.location.get_tile(self.host.pos + (1, 0)).is_land(Tile.CHECK_ANY):
                    self.host.input('right', self.host.pos.to_list())
                elif not self.host.location.get_tile(self.host.pos + (-1, 0)).is_land(Tile.CHECK_ANY):
                    self.host.input('left', self.host.pos.to_list())
                elif not self.host.location.get_tile(self.host.pos + (1, -1)).is_land(Tile.CHECK_ANY):
                    self.host.input('jump', self.host.location.get_tile(self.host.pos + (1, -1)).to_list())
                elif not self.host.location.get_tile(self.host.pos + (-1, -1)).is_land(Tile.CHECK_ANY):
                    self.host.input('jump', self.host.location.get_tile(self.host.pos + (-1, -1)).to_list())
