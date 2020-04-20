from src.entity.unit.item.Equipment import Equipment
from src.tools.Data import Data


class Armor(Equipment):
    def set_form(self, arg):
        self.form_name = arg
        self.form = Data.get_form(arg, form='Armor')

    def die(self):
        if self.host:
            self.host.unarmor()
        super().die()

    def get_value(self):
        return super().get_value() + self.tags.get('def', 0) + self.tags.get('space', 0)

    def wear(self, start=False):
        if self.host.armor:
            self.host.unarmor()
        else:
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
