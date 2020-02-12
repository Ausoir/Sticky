from src.entity.unit.item.Equipment import Equipment
from src.tools.Data import Data


class Armor(Equipment):
    def __init__(self):
        super().__init__()
        self.armor = 0
        self.capacity = 0

    def __str__(self):
        r = super().__str__()
        r += ',' + str(self.armor) + ',' + str(self.capacity)
        return r

    def load(self, p):
        index = super().load(p)
        self.armor = p[index]
        index += 1
        self.capacity = p[index]
        return index + 1

    def set_form(self, arg):
        self.form_name = arg
        self.form = Data.get_form(arg, form='Armor')

    def die(self):
        if self.host:
            self.host.unarmor()
        super().die()

    def get_value(self):
        return super().get_value() + self.armor + self.capacity

    def get_defense(self):
        min_d = 0
        armor = self.tags.get('armor')
        if armor:
            min_d += armor
        return min_d, self.armor + min_d

    def describe(self):
        r = super().describe()
        r += '\nCan hold items up to ' + str(self.capacity) + 'kg'
        min_d, max_d = self.get_defense()
        r += '\nDefense: ' + str(min_d) + ' ~ ' + str(max_d)
        return r

    def modify(self, arg):
        if super().modify(arg):
            pass
        elif arg == 'reinforce':
            self.armor += 1
        elif arg == 'refit':
            self.capacity += 1
        else:
            return False
        return True

    def wear(self, start=False):
        if self.host.armor:
            self.host.unarmor()
        super().wear(start)
        self.host.form.set_model(self.form_name)
        self.host.armor = self
        host = self.host
        if self.host.weapon == self:
            self.host.drop()
        self.host = host
        self.host.face(self.host.direction)

    def on_wear(self):
        super().on_wear()
        from src.entity.unit.Character import Character
        if isinstance(self.host, Character):
            t = self.capacity
            self.capacity = 0
            self.host.inventory.update_capacity()
            self.capacity = t

    def on_unwear(self):
        super().on_unwear()
        from src.entity.unit.Character import Character
        if isinstance(self.host, Character):
            t = self.capacity
            self.capacity = 0
            self.host.inventory.update_capacity()
            self.capacity = t
