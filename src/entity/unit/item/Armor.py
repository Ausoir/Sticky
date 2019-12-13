from src.entity.unit.item.Equipment import Equipment
from src.tools.Data import Data


class Armor(Equipment):
    def __init__(self, loc):
        super().__init__(loc)
        self.capacity = 0
        self.pockets = [0]
        self.armor = 0

    def __str__(self):
        r = super().__str__()
        pockets = ','.join(str(x) for x in self.pockets)
        r += ',' + str(self.armor) + ',' + str(self.capacity) + ',[' + pockets + ']'
        return r

    def load(self, p):
        index = super().load(p)
        self.armor = p[index]
        self.capacity = p[index]
        index += 1
        self.pockets = p[index]
        return index + 1

    def set_form(self, arg):
        self.form_name = arg
        self.form = Data.get_form(arg, form='Humanoid')

    def die(self):
        if self.host:
            self.host.unarmor()
        super().die()

    def get_value(self):
        return super().get_value() + self.armor + len(self.pockets) + self.capacity

    def describe(self):
        r = super().describe()
        r += '\nCan hold items up to ' + str(self.capacity) + 'kg'
        r += '\nDefense: ' + str(self.armor)
        r += '\nPockets: ' + str(len(self.pockets))
        return r

    def use(self):
        self.host.action.set('wait')
        if self.host.is_armored():
            self.host.unarmor()
        self.host.armor = self
        host = self.host
        if self.host.weapon == self:
            self.host.drop()
        self.remove()
        host.update_durability(0)
        self.host = host
        self.host.face(self.host.direction)

    def on_wear(self):
        self.host.attributes.max_hp += self.durability
