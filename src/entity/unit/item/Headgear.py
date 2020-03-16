from src.entity.unit.item.Equipment import Equipment
from src.tools import Direction
from src.tools.Dialog import Dialog


class Headgear(Equipment):
    def describe(self):
        r = super().describe()
        spell = self.tags.get('spell')
        if spell:
            r += '\n' + Dialog.get('artifact', [spell])
        if self.tags.get('charge', 0) == 0:
            r += '\n' + Dialog.get('!charged')
        else:
            r += '\n' + Dialog.get('charged')
        return r

    def die(self):
        if self.host:
            self.host.unheadgear()
        super().die()

    def face(self, direction):
        self.form.switch(Direction.numeral[direction])
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
                self.tags.increment('charge', -self.tags.get('spend', charge))
                self.host.action.act('grab', 8)
                from src.entity.unit.item.Spell import Spell
                from src.game import Global
                if self.host == Global.player.character:
                    tile = Global.player.control.get_mark()
                    if tile:
                        for i in tile.things:
                            from src.entity.unit.item.Spell import Spell
                            Spell.perform(i, spell)
                            return

    def on_sleep(self, time):
        self.tags.increment('charge', time)
        self.tags.minmax('charge', self.tags.get('charge<', -999), self.tags.get('charge>', 999))
