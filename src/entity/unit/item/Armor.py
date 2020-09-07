from src.entity.unit.item.Equipment import Equipment
from src.tools.Data import Data


class Armor(Equipment):
    def set_form(self, arg):
        self.form_name = arg
        self.form = Data.get_form(arg, form='Armor')

    def remove(self):
        if self.host and self.host.armor == self:
            self.unwear()
        super().remove()

    def wear(self, start=False):
        if self.host.armor:
            self.host.unarmor()
        else:
            self.host.armor = self
            super().wear(start)
            self.host.form.set_model(self.form_name)
            self.show(False)

    def unwear(self):
        if self.host.removed == 0:
            line = Data.get_line('model.txt', self.host.form_name)
            self.host.form.set_model(line[2])
        self.host.armor = None
        super().unwear()
