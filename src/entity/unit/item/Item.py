from src.entity.Prop import Prop
from src.map.Tile import Tile


class Item(Prop):
    def __init__(self, location):
        super().__init__(location)
        self.obstruct_type = Tile.COLLIDE_ITEM
        self.host = None

    def remove(self):
        if self.host:
            if self.host.weapon == self:
                self.host.drop()
        super().remove()

    def face(self, direction):
        self.form.face_cardinal(direction)

    def on_wield(self, host):
        self.save = False
        self.host = host
        host.weapon = self
        self.host.face(self.host.direction)

    def on_unwield(self):
        self.save = True
        self.host = None

    def get_value(self):
        return self.tags.get('price', 1)

    def get_display_name(self):
        return self.name

    def describe(self):
        r = self.get_display_name()
        from src.tools.Data import Data
        from src.tools.Dialog import Dialog
        data = Data.get_line('descriptions.txt', r)
        if data:
            r += '\n' + data[1]
        hp = self.tags.get('p')
        if hp:
            max_hp = self.tags.get('p>')
            r += '\n' + Dialog.durability(hp, max_hp)
        r += '\nWeight: ' + str(self.get_weight())
        mat = Dialog.material(self.tags.attributes.get('mat'))
        if mat:
            r += '\n' + mat
        return r

    def use(self):
        self.host.action.attack()

    def get_weight(self):
        return self.tags.get('w', 1)

    def get_damage(self):
        return 0

    def on_attack(self, target):
        self.states.trigger(['attack', target])
        for i in self.states.buffs:
            target.states.add(i.name, 40, i.var)

    def update(self):
        if not self.host:
            super().update()

    def set_row(self, row):
        if not self.host:
            super().set_row(row)
