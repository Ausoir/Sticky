from src.entity.unit.item.Equipment import Equipment
from src.tools.Data import Data


class Armor(Equipment):
    def __init__(self, location):
        super().__init__(location)
        self.armor = 0

    def __str__(self):
        r = super().__str__()
        r += ',' + str(self.armor)
        return r

    def load(self, p):
        index = super().load(p)
        self.armor = p[index]
        return index + 1

    def set_form(self, arg):
        self.form_name = arg
        self.form = Data.get_form(arg, form='Armor')

    def die(self):
        if self.host:
            self.host.unarmor()
        super().die()

    def get_value(self):
        return super().get_value() + self.armor + self.get_weight()

    def describe(self):
        r = super().describe()
        r += '\nCan hold items up to ' + str(self.get_weight()) + 'kg'
        r += '\nDefense: ' + str(self.armor)
        return r

    def modify(self, arg):
        if super().modify(arg):
            pass
        elif arg == 'reinforce':
            self.armor += 1
        else:
            return False
        return True

    def wear(self, start=False):
        self.host.unarmor()
        self.host.armor = self
        super().wear(start)
        self.host.form.set_model(self.form_name)

    def unwear(self):
        from src.tools.Data import Data
        line = Data.get_line('model.txt', self.host.form_name)
        self.host.form.set_model(line[2])
        self.host.armor = None
        super().unwear()

    def on_wear(self):
        super().on_wear()
        self.host.inventory.update_capacity()

    def on_unwear(self):
        super().on_unwear()
        self.host.inventory.update_capacity()
