from src.entity.Prop import Prop
from src.map.Tile import Tile


class Item(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.collide = Tile.COLLIDE_ITEM
        self.host = None
        self.range = [1]
        self.volume = [1, 1]
        self.hit_type = 'batter'

    def __str__(self):
        return super().__str__() + ',[' + str(self.volume[0]) + ',' + str(self.volume[1]) + '],' + self.hit_type

    def load(self, arg):
        index = super().load(arg)
        self.volume = arg[index]
        self.hit_type = arg[index + 1]
        return index + 2

    def on_equip(self, host):
        self.host = host
        host.weapon = self
        self.remove()

    def on_unequip(self):
        self.host = None
        self.add()

    def interact(self, host):
        self.on_equip(host)

    def use(self):
        self.host.action.set('attack')

    def attack(self, delay=0, callback=None):
        for i in self.range:
            tile = self.host.location.collide_line(self.host.get_interact_pos(),
                                                   self.host.next_target.x, self.host.next_target.y,
                                                   distance=i, flag=Tile.CHECK_NONE)
            cb = callback
            if self.states.get('fire'):
                def burn(target):
                    target.states.add('burn', 4)
                    if callback:
                        callback()
                cb = burn
            self.location.attack.register(1, tile, delay, self.hit_type,
                                          faction=self.host.faction, callback=cb)
