from src.entity.Prop import Prop
from src.map.Tile import Tile
from src.tools.Dialog import Dialog


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

    def describe(self):
        r = super().describe()
        stat = self.tags.get('sth')
        if stat:
            r += '\n' + Dialog.get('equipment_sth', [Dialog.sign(stat)])
        space = self.tags.get('str', 0)
        if space > 0:
            r += '\n' + Dialog.get('equipment_inv', [Dialog.sign(space)])
        end = self.tags.get('end', 0)
        if end > 0:
            r += '\n' + Dialog.get('equipment_end', [Dialog.sign(end)])
        defense = self.tags.get('DEF', 0)
        if defense > 0:
            r += '\n' + Dialog.get('equipment_def', [Dialog.sign(defense)])
        skill = self.tags.get('skill')
        if skill:
            r += '\n' + Dialog.get('equipment_skill', [skill.title()])
        return r

    def on_wield(self, host, start=False):
        self.save = False
        self.host = host
        host.weapon = self
        self.host.face(self.host.direction)
        if not start:
            self.host.tags.increment('dmg', self.tags.get('dmg', 0), default=1)

    def on_unwield(self):
        self.update_vec()
        self.save = True
        if self.host:
            self.host.tags.increment('dmg', -self.tags.get('dmg', 0), remove=1)
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
        if rng <= int(100 * (1 / max(1, self.tags.get('mod', 0) + 1))):
            from src.entity.Particle import Particle
            Particle.make('shock', self.pos)
            self.location.sound.register(self.pos, 1, file='heal', priority=2)
            self.tags.increment('mod', 1)
            return True
        else:
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
        if v:
            return v * (self.tags.get('rare', 0) + 1)
        else:
            r = 0
            for i in ['def', 'DEF', 'dmg', 'str', 'sth']:
                r += self.tags.get(i, 0)
            r += min(8, int(self.tags.get('p', 32) / 4))
            if self.tags.get('skill'):
                r += 8
            if self.tags.get('spell'):
                r += 10
            return max(1, int((r - self.tags.get('w', 1)) / 2))
