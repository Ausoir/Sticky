from src.entity.unit.item.Equipment import Equipment
from src.tools.Dialog import Dialog


class Headgear(Equipment):
    def describe(self):
        r = super().describe()
        spell = self.tags.get('spell')
        if spell:
            r += '\n' + Dialog.get('artifact', [spell])
        charge = self.tags.get('charge')
        if charge:
            if charge > 0:
                r += '\n' + Dialog.get('charged')
            else:
                r += '\n' + Dialog.get('!charged')
        return r

    def die(self):
        if self.host:
            self.host.unheadgear()
        super().die()

    def face(self, direction):
        if super().face(direction):
            from src.form.Body import Body
            self.form.switch(Body.TEXTURE_DIRECTION[self.direction])
            self.form.reset()
            if self.direction == 1:
                self.form.scale_x *= -1

    def wear(self, start=False):
        if self.host.headgear:
            self.host.unheadgear()
        else:
            self.host.headgear = self
            super().wear(start)
            self.direction = self.host.direction + 1  # force face
            self.face(self.host.direction)

    def unwear(self):
        self.host.headgear = None
        super().unwear()

    def set_form(self, arg):
        from src.tools.Data import Data
        self.form_name = arg
        self.form = Data.get_form(arg, form='Head')

    def on_sleep(self, time):
        if time > 0:
            self.tags.set('charge', 1)


class Talisman(Headgear):
    def die(self):
        if self.host:
            spell = self.tags.get('spell')
            if spell:
                from src.entity.unit.item.Spell import Spell
                Spell.get(spell, power=self.tags.get('power', 0)).cast_on(self.host)
        super().die()
