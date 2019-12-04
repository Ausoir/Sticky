from src.entity.Prop import Prop
from src.game import Global
from src.game.Tags import Tags
from src.map.Tile import Tile


class Item(Prop):
    description = {}
    price = {}

    def __init__(self, loc):
        super().__init__(loc)
        self.collision_type = Tile.COLLIDE_ITEM
        self.host = None
        self.rotation = 60
        self.reach = 1
        self.volume = [1, 1]
        self.weight = 1
        self.speed = 5
        self.accuracy = 1
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
        self.form.face_cardinal(direction)

    def on_equip(self, host):
        self.host = host
        host.weapon = self
        self.vec = host.vec
        self.remove()
        self.form.show(True)

    def on_unequip(self):
        self.form.group = Global.draw_group.objects
        self.form.rotation = 0
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
            self.on_attack(target)
            if callback:
                callback(target)
        acc = self.accuracy + chance
        for i in range(self.reach):
            tile = self.host.location.collide_line(self.host.pos, self.host.next_target.x, self.host.next_target.y,
                                                   lambda arg1, arg2: None, distance=i + 1)
            self.location.attack.register(self.damage, tile, chance=acc, delay=delay,
                                          hitter=self, callback=on_attack)

    def on_attack(self, target):
        self.location.sound.register(target.pos, 5)
        self.hit(1)
        self.states.trigger(['attack', target])
        if Tags.sharp in self.tags:
            target.states.add('Bleed', 40)

    def on_sleep(self, time):
        pass
