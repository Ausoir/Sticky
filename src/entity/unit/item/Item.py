from src.entity.Prop import Prop
from src.map.Tile import Tile


class Item(Prop):
    description = {}
    price = {}

    def __init__(self, loc):
        super().__init__(loc)
        self.collision_type = Tile.COLLIDE_ITEM
        self.host = None
        self.weight = 1

    def __str__(self):
        return super().__str__() + ',' + str(self.weight)

    def load(self, arg):
        index = super().load(arg)
        self.weight = arg[index]
        return index + 1

    def remove(self):
        if self.host:
            if self.host.weapon == self:
                self.host.drop()
        super().remove()

    def face(self, direction):
        self.form.face_cardinal(direction)

    def on_equip(self, host):
        self.show(True)
        self.host = host
        host.weapon = self
        self.vec = host.vec
        self.location.record.remove(self)
        self.pos.things.remove(self)
        self.host.form.update_perspective()

    def on_unequip(self):
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
        r += '\nDurability: ' + str(self.tags.get('p', 'Indefinite')) + '/' + str(self.tags.get('p>', 'Indefinite'))
        r += '\nWeight: ' + str(self.weight)
        from src.entity.Attribute import Attribute
        if self.tags.attributes.get(Attribute.flesh):
            r += '\nThis item is an organic material.'
        if self.tags.attributes.get(Attribute.insubstantial):
            r += '\nThis item is insubstantial.'
        if self.tags.attributes.get(Attribute.metal):
            r += '\nThis item is metallic.'
        if self.tags.attributes.get(Attribute.wood):
            r += '\nThis item is composed of wood.'
        if self.tags.attributes.get('silver'):
            r += '\nThis item has silver properties.'
        if self.tags.attributes.get('sharp'):
            r += '\nThis item is sharp.'
        return r

    def use(self):
        self.host.action.swing()

    def get_damage(self):
        return 0, 1

    def attack(self, damage=0, delay=1, callback=None):
        def on_attack(target):
            self.on_attack(target)
            if callback:
                callback(target)
        tile = self.host.get_front_tile(self.host.direction, mag=1)
        from src.game import Global
        min_d, max_d = self.get_damage()
        dmg = Global.r.rand_int(min_d + damage, min_d + damage + max_d)
        self.location.attack.register(dmg, tile, delay=delay, hitter=self, callback=on_attack, sound=['swing', 2])

    def on_attack(self, target):
        self.states.trigger(['attack', target])

    def on_sleep(self, time):
        pass
