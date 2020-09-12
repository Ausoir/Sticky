from src.entity.Prop import Prop
from src.map.Tile import Tile
from src.tools.Dialog import Dialog


class Item(Prop):
    def __init__(self):
        super().__init__()
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

    def describe(self):
        r = super().describe()
        skill = self.tags.get('skill')
        if skill:
            r += '\n' + Dialog.get(':equipment_skill', [skill.title()])
        return r

    def on_wield(self, host):
        self.is_save = False
        self.host = host
        host.weapon = self
        self.host.face(self.host.direction)

    def on_unwield(self):
        self.update_vec()
        self.is_save = True
        self.host = None

    def use(self):
        spell = self.tags.get('spell')
        if spell:
            from src.entity.unit.item.Spell import Spell
            spell_cast = Spell.get(spell)
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
        from src.entity.Particle import Particle
        if rng <= int(100 * (1 / max(1, self.tags.get('mod', 0) + 2))):
            Particle.make('shine', self.pos)
            self.pos.location.sound.register(self.pos, 1, file='heal')
            self.tags.increment('mod', 1)
            return True
        else:
            Particle.make('shock', self.pos)
            self.pos.location.sound.register(self.pos, 1, file='down')
            if rng >= 75:
                self.die()
        return False

    def relocate(self, to=None, x=None, y=None, force=False):
        if self.host:
            super().relocate(to=self.host.pos, force=force)
        else:
            super().relocate(to, x, y, force)

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

    def get_value(self):
        v = self.tags.get('$')
        if v is not None:
            return v * (self.tags.get('rare', 0) + 1)
        else:
            r = self.tags.get_level()
            r += self.tags.get('DEF', 0)
            if not self.tags.get('p'):
                r += 1
            if self.tags.get('skill'):
                r += 1
            if self.tags.get('spell'):
                r += 2
            return max(0, r - self.tags.get('w', 1))

    def drown(self):
        if not self.host:
            super().drown()
