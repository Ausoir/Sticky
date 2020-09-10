from src.entity.unit.item.Equipment import Equipment
from src.tools.Dialog import Dialog


class Headgear(Equipment):
    def remove(self):
        if self.host and self.host.headgear == self:
            self.unwear()
        super().remove()

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


class Talisman(Headgear):
    def wear(self, start=False):
        super().wear(start)
        from src.game import Global
        if not start and self.host == Global.player.character:
            Global.main.monologue.set(Dialog.get(':talisman'))

    def describe(self):
        r = super().describe()
        spell = self.tags.get('spell')
        if spell:
            r += '\n' + Dialog.get(':artifact', [spell.title()])
        return r

    def trigger(self):
        if self.host:
            spell = self.tags.get('spell')
            if spell:
                from src.entity.unit.item.Spell import Spell
                Spell.get(spell).cast_on(self.host)
            effect = self.tags.get('effect')
            if effect:
                self.host.states.add(effect, self.tags.get('dur', 0), self.tags.get('var', 0))
            self.decay(1)
