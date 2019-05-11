from src.entity.Prop import Prop
from src.game.Global import DEPTH_ITEM
from src.game.Tags import Tags
from src.map.Tile import Tile


class Item(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.collide = Tile.COLLIDE_ITEM
        self.host = None
        self.depth = DEPTH_ITEM
        self.rotation = 60
        self.range = [[1, 0]]
        self.volume = [1, 1]
        self.weight = 8  # not recorded
        self.speed = 5
        self.damage = 1

    def __str__(self):
        return super().__str__() + ',[' + str(self.volume[0]) + ',' + str(self.volume[1]) + ']'

    def load(self, arg):
        index = super().load(arg)
        self.volume = arg[index]
        return index + 1

    def die(self):
        if self.host and self.host.weapon == self:
            self.host.drop()
        super().die()

    def on_equip(self, host):
        self.host = host
        host.weapon = self
        self.vec = host.vec
        self.host.face(self.host.direction)
        self.remove()

    def on_unequip(self):
        self.form.rotate(0)
        self.vec = self.vec + 0
        self.relocate(self.host.pos[0].x, self.host.pos[0].y, force=1)
        self.host = None
        self.form.rotate(0)
        self.add()

    def describe(self):
        r = self.name
        if self.durability == -1:
            dur = 'Unbreakable'
        else:
            dur = str(self.durability)
        r += '\nDurability: ' + dur
        r += '\nVolume: ' + str(self.volume[0]) + 'x' + str(self.volume[1])
        return r

    def use(self):
        host = self.host
        self.host.drop()
        host.armor.add_item(self)
        host.action.set('rest')

    def attack(self, damage=None, callback=None):
        def cb(target):
            if self.states.get('Fire'):
                target.states.add('Burn', 8)
            if self.states.get('Shock'):
                target.states.add('Stun', 40)
                self.states.get('Shock').end()
            if Tags.sharp in self.tags:
                target.states.add('Bleed', 60)
            if callback:
                callback(target)
        for i in self.range:
            if damage is None:
                damage = self.damage
            self.location.attack.register(damage, self.host.get_offset_tile(i[0] * self.host.direction, i[1]),
                                          type='batter', faction=self.host.faction, callback=cb)
