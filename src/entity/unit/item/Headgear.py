from src.entity.unit.item.Equipment import Equipment
from src.tools import Direction


class Headgear(Equipment):
    def die(self):
        if self.host:
            self.host.unheadgear()
        super().die()

    def face(self, direction):
        self.form.switch(Direction.numeral[direction])
        self.form.reset()
        super().face(direction)

    def on_equip(self, host):
        super().on_equip(host)
        self.face(1)

    def wear(self, start=False):
        if self.host.headgear:
            self.host.unheadgear()
        self.host.headgear = self
        super().wear(start)
        self.host.face(self.host.direction)

    def set_form(self, arg):
        from src.tools.Data import Data
        self.form_name = arg
        self.form = Data.get_form(arg, form='Head')

    def activate(self):
        self.host.action.act('grab', 8)
