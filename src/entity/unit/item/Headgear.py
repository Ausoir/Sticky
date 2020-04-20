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
        from src.form.Body import Body
        self.form.switch(Body.TEXTURE_DIRECTION[direction])
        self.form.reset()
        super().face(direction)

    def wear(self, start=False):
        self.host.unheadgear()
        self.host.headgear = self
        super().wear(start)
        self.show(True)

    def unwear(self):
        self.host.headgear = None
        super().unwear()

    def set_form(self, arg):
        from src.tools.Data import Data
        self.form_name = arg
        self.form = Data.get_form(arg, form='Head')

    def activate(self):
        spell = self.tags.get('spell')
        if spell:
            charge = self.tags.get('charge', 0)
            if charge > 0:
                self.tags.increment('charge', -1)
                self.host.action.act('grab', 8)
                from src.entity.unit.item.Spell import Spell
                from src.game import Global
                if self.host == Global.player.character:
                    Spell.cast(self.host, 'Wand', spell)

    def on_sleep(self, time):
        if time > 0:
            self.tags.set('charge', 1)
