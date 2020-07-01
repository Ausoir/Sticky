from src.entity.Prop import Prop
from src.map.Tile import Tile


class Item(Prop):
    def __init__(self, location):
        super().__init__(location)
        self.obstruct_type = Tile.COLLIDE_ITEM
        self.host = None

    def load(self, arg):
        r = super().load(arg)
        if self.tags.get('rare', 0) > 0:
            if self.states.get('Effect') is None:
                self.states.add('Effect', -1, 'shine')
        return r

    def remove(self):
        if self.host:
            if self.host.weapon == self:
                self.host.drop()
            elif self in self.host.inventory.items:
                self.host.inventory.items.remove(self)
        super().remove()

    def on_wield(self, host):
        self.save = False
        self.host = host
        host.weapon = self
        self.host.face(self.host.direction)

    def on_unwield(self):
        self.update_vec()
        self.save = True
        self.host = None

    def use(self):
        spell = self.tags.get('spell')
        if spell:
            from src.entity.unit.item.Spell import Spell
            spell_cast = Spell.get(spell, self.tags.get('power', 0))
            spell_cast.cast(self.host, self.tags.get('motion', 'cast'), self.tags.get('delay', 4))
        else:
            self.host.action.attack()

    def on_attack(self, target):
        self.states.trigger(['attack', target])

    def update(self):
        if not self.host:
            super().update()

    def set_row(self, row):
        if not self.host:
            super().set_row(row)

    def enhance(self, rng):
        if rng >= int(100 * (1 / max(1, self.tags.get('mod', 0) + 1))):
            self.tags.increment('mod', 1)
            return True
        else:
            self.die()
        return False

    def get_display_name(self):
        r = super().get_display_name()
        if self.tags.get('rare', 0) > 0:
            from src.tools.Dialog import Dialog
            r = Dialog.get('Rare') + ' ' + r
        level = self.tags.get('mod', 0)
        if level > 0:
            return r + ' +' + str(level)
        else:
            return r
