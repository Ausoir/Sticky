from src.entity.Prop import Prop
from src.entity.unit.action.Attack import Attack
from src.map.Tile import Tile


class Item(Prop):
    def __init__(self, form, seed, loc):
        super().__init__(form, seed, loc)
        self.collide = Tile.CHECK_ITEM
        self.host = None
        self.range = [1]

    def on_equip(self, host):
        self.host = host
        self.remove()

    def on_unequip(self, host):
        self.host = None
        self.add()

    def attack(self, delay=0, on_hit=None):
        for i in self.range:
            tile = self.host.location.collide_line(self.host.get_interact_pos(),
                                                   self.host.next_target[0], self.host.next_target[1],
                                                   max=i, flag=Tile.CHECK_NONE)
            self.location.attack.register(self.host, 1, tile, delay, Attack.BLOODY, faction=self.host.faction, callback=on_hit)
