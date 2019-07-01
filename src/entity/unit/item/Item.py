from src.entity.Prop import Prop
from src.game.Tags import Tags
from src.map.Tile import Tile


class Item(Prop):
    description = {}

    def __init__(self, loc):
        super().__init__(loc)
        self.collide = Tile.COLLIDE_ITEM
        self.host = None
        self.rotation = 60
        self.range = [[1, 0]]
        self.volume = [1, 1]
        self.weight = 4  # not recorded
        self.speed = 5
        self.damage = 1

    def __str__(self):
        return super().__str__() + ',[' + str(self.volume[0]) + ',' + str(self.volume[1]) + ']'

    def load(self, arg):
        index = super().load(arg)
        self.volume = arg[index]
        return index + 1

    def die(self):
        if self.host:
            if self.host.weapon == self:
                self.host.drop()
            elif self.host.offhand == self:
                self.host.swap()
                self.host.drop()
                self.host.swap()
            elif self in self.host.armor.items:
                self.host.armor.get_item(self.host.armor.items.index(self))
        super().die()

    def face(self, direction):
        self.form.direction = [direction, 0]

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

    def get_value(self):
        return 1

    def describe(self):
        r = self.name
        if r in Item.description:
            r += '\n' + Item.description[r]
        if self.durability == -1:
            r += '\nDurability: Unbreakable'
        else:
            r += '\nDurability: ' + str(self.durability)
        r += '\nVolume: ' + str(self.volume[0]) + 'x' + str(self.volume[1])
        return r

    def use(self):
        self.host.action.set('idle')

    def attack(self, chance=0, damage=1, callback=None):
        def on_attack(target):
            self.hit(1)
            if self.states.get('Fire'):
                target.states.add('Burn', 8)
            if Tags.sharp in self.tags:
                target.states.add('Bleed', 40)
            if callback:
                callback(target)

        dmg = self.damage + chance + self.host.get_proficiency(self.name)
        for i in self.range:
            tile = self.host.location.collide_land(self.host.get_interact_pos(),
                                                   self.host.next_target.x, self.host.next_target.y,
                                                   distance=i, flag=[])
            self.location.attack.register(damage, tile, chance=dmg, type='batter', faction=self.host.faction,
                                          hitter=self.host, callback=on_attack)
