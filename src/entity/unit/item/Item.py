from src.entity.Prop import Prop
from src.game.Tags import Tags
from src.map.Tile import Tile


class Item(Prop):
    description = {}
    price = {}

    def __init__(self, loc):
        super().__init__(loc)
        self.collision_type = Tile.COLLIDE_ITEM
        self.host = None
        self.weight = 5

    def __str__(self):
        return super().__str__() + ',' + str(self.weight)

    def load(self, arg):
        index = super().load(arg)
        self.weight = arg[index]
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
        self.form.face_cardinal(direction)

    def on_equip(self, host):
        self.dynamic_depth = True
        self.show(True)
        self.host = host
        host.weapon = self
        self.vec = host.vec
        self.location.record.remove(self)
        self.pos.things.remove(self)
        self.host.form.update_perspective()

    def on_unequip(self):
        self.dynamic_depth = False
        self.vec = self.vec + 0
        self.relocate(self.host.pos.x, self.host.pos.y, force=1)
        self.host = None
        self.set_form(self.form_name)
        self.add()

    def get_value(self):
        if self.name in Item.price:
            return Item.price[self.name]
        return 1

    def get_display_name(self):
        return self.name

    def describe(self):
        r = self.get_display_name()
        if r in Item.description:
            r += '\n' + Item.description[r]
        r += '\nWeight: ' + str(self.weight)
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
        self.host.action.swing()

    def attack(self, damage=1, chance=1, delay=1, callback=None):
        def on_attack(target):
            self.on_attack(target)
            if callback:
                callback(target)
        tile = self.host.get_front_tile(self.host.direction, mag=1)
        self.location.attack.register(damage, tile, chance=chance, delay=delay,
                                      hitter=self, callback=on_attack)

    def on_attack(self, target):
        self.location.sound.register(target.pos, 5)
        self.states.trigger(['attack', target])
        if Tags.sharp in self.tags:
            target.states.add('Bleed', 40)

    def on_sleep(self, time):
        pass
