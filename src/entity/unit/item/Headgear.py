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

    def use(self):
        super().use()
        self.host.headgear = self
        self.remove()
        self.form.show(True)
        self.host.face(self.host.direction)

    def set_form(self, arg):
        from src.tools.Data import Data
        self.form_name = arg
        self.form = Data.get_form(arg, form='Head')

    def activate(self):
        self.host.action.set('wait')
