from src.entity.Prop import Prop
from src.game.Tags import Tags
from src.map.Tile import Tile


class Item(Prop):
    description = {}

    def __init__(self, loc):
        super().__init__(loc)
        self.collision_type = Tile.COLLIDE_ITEM
        self.host = None
        self.rotation = 60
        self.range = [1]
        self.volume = [1, 1]
        self.weight = 1  # not recorded
        self.speed = 5
        self.damage = 1

    def __str__(self):
        return super().__str__() + ',[' + str(self.volume[0]) + ',' + str(self.volume[1]) + ']'

    def load(self, arg):
        index = super().load(arg)
        if Tags.lightweight in self.tags:
            self.weight = 0
        self.volume = arg[index]
        return index + 1

    def die(self):
        if self.host:
            if self.host.weapon == self:
                self.host.drop()
            elif self.host.offhand == self:
                host = self.host
                host.swap()
                host.drop()
                host.swap()
            elif self in self.host.armor.items:
                self.host.armor.get_item(self.host.armor.items.index(self))
        super().die()

    def face(self, direction):
        self.form.direction = direction

    def on_equip(self, host):
        self.face(host.direction)
        self.rotation = 60
        self.host = host
        host.weapon = self
        self.vec = host.vec
        self.remove()

    def on_unequip(self):
        self.vec = self.vec + 0
        self.relocate(self.host.pos.x, self.host.pos.y, force=1)
        self.host = None
        self.set_form(self.form_name)
        self.add()

    def get_value(self):
        return 1

    def get_display_name(self):
        return self.name

    def describe(self):
        r = self.get_display_name()
        if r in Item.description:
            r += '\n' + Item.description[r]
        if self.durability == -1:
            r += '\nDurability: Unbreakable'
        else:
            r += '\nDurability: ' + str(self.durability)
        r += '\nVolume: ' + str(self.volume[0]) + 'x' + str(self.volume[1])
        if Tags.flesh in self.tags:
            r += '\nThis item is an organic material.'
        if Tags.insubstantial in self.tags:
            r += '\nThis item is insubstantial.'
        if Tags.metal in self.tags:
            r += '\nThis item is metallic.'
        if Tags.wood in self.tags:
            r += '\nThis item is composed of wood.'
        if Tags.silver in self.tags:
            r += '\nThis item has silver properties.'
        if Tags.sharp in self.tags:
            r += '\nThis item is sharp.'
        return r

    def use(self):
        self.host.action.set('swing')

    def attack(self, chance=0, delay=1, callback=None):
        def on_attack(target):
            self.location.sound.register(target.pos, 5)
            self.hit(1)
            self.states.trigger(['attack', target])
            if Tags.sharp in self.tags:
                target.states.add('Bleed', 40)
            if callback:
                callback(target)
        acc = self.damage + chance + self.host.get_proficiency(self.name)
        dmg = self.weight
        from src.entity.unit.Character import Character
        if Character.check_var(self.host, 'power', 'Warrior'):
            acc += 10
            dmg *= 2

        def fn(prev, tile):
            return None
        for i in self.range:
            tile = self.host.location.collide_line(self.host.pos,
                                                   self.host.next_target.x, self.host.next_target.y, fn,
                                                   distance=i)
            self.location.attack.register(dmg, tile, chance=acc, delay=delay, type='batter',
                                          hitter=self.host, callback=on_attack)

    def update(self):
        pass
