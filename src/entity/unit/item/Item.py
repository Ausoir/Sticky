from src.entity.Prop import Prop
from src.map.Tile import Tile


class Item(Prop):
    def __init__(self):
        super().__init__()
        self.obstruct_type = Tile.COLLIDE_ITEM
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
        from src.game import Global
        Global.location.population.remove(self)
        self.pos.things.remove(self)
        self.host.form.update_perspective()

    def on_unequip(self):
        self.vec = self.vec + 0
        self.relocate(self.host.pos.x, self.host.pos.y, force=1)
        self.host = None
        self.set_form(self.form_name)
        self.add()

    def get_value(self):
        return self.tags.get('price', 1)

    def get_display_name(self):
        return self.name

    def describe(self):
        r = self.get_display_name()
        from src.tools.Data import Data
        data = Data.get_line('raw/descriptions.txt', r)
        if data:
            r += '\n' + data[1]
        r += '\nDurability: ' + str(self.tags.get('p', 'Indefinite')) + '/' + str(self.tags.get('p>', 'Indefinite'))
        r += '\nWeight: ' + str(self.weight)
        material = self.tags.attributes.get('mat')
        if material == 'flesh':
            r += '\nThis item is an organic material.'
        if material == 'metal':
            r += '\nThis item is metallic.'
        if material == 'wood':
            r += '\nThis item is composed of wood.'
        if material == 'silver':
            r += '\nThis item has silver properties.'
        return r

    def use(self):
        self.host.action.attack()

    def get_damage(self):
        return 0, 1

    def on_attack(self, target):
        self.states.trigger(['attack', target])

    def on_sleep(self, time):
        pass
