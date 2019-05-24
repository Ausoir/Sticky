from src.entity.Prop import Prop
from src.game.Tags import Tags
from src.map.Tile import Tile
from src.tools.Random import Random


class Item(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.collide = Tile.COLLIDE_ITEM
        self.host = None
        self.rotation = 60
        self.direction = 1
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

    def face(self, direction):
        if self.direction != direction:
            self.direction = direction
            self.form.flip(1, 0)

    def on_equip(self, host):
        self.face(host.direction)
        self.rotation = 60
        self.host = host
        host.weapon = self
        self.vec = host.vec
        self.remove()

    def on_unequip(self):
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

    def attack(self, damage=0, callback=None):
        dmg = self.damage + damage + self.host.get_proficiency(self.name)
        for i in self.range:
            tile = self.host.location.collide_land(self.host.get_interact_pos(),
                                                   self.host.next_target.x, self.host.next_target.y,
                                                   distance=i, flag=[])
            self.location.attack.register(1, tile, chance=dmg, type='batter', faction=self.host.faction,
                                          callback=self.on_attack)
            if callback:
                self.location.attack.register(0, tile, chance=dmg, faction=self.host.faction, callback=callback)

    def on_attack(self, target):
        if Random.rand_int(1, 16) == 1:
            self.hit(1)
        if self.states.get('Fire'):
            target.states.add('Burn', 8)
        if Tags.sharp in self.tags:
            target.states.add('Bleed', 40)
