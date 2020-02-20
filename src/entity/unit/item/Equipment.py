from src.entity.unit.item.Item import Item


class Equipment(Item):
    def get_enhance_chance(self):
        return int(100 * (1 / max(1, self.get_level() + 1)))

    def enhance(self, rng):
        if rng <= self.get_enhance_chance():
            self.tags.increment('mod', 1, add=True)
            return True
        else:
            from src.entity.Particle import Particle
            Particle.make('disintegrate', self.host.vec)
            self.die()
        return False

    def modify(self, arg):
        if arg == 'ascend':
            self.tags.remove('mod')
        elif arg == 'reinforce':
            self.host.armor.attributes.hp += 1
            self.host.armor.attributes.max_hp += 1
        else:
            return False
        return True

    def get_level(self):
        return self.tags.get('mod', 0)

    def get_display_name(self):
        level = self.get_level()
        if level > 0:
            return self.name + ' +' + str(level)
        else:
            return self.name

    def describe(self):
        r = super().describe()
        spd = self.tags.get('spd', 0)
        from src.tools.Dialog import Dialog
        if spd < 0:
            r += '\n' + Dialog.get('equipment_slow')
        elif spd > 0:
            r += '\n' + Dialog.get('equipment_fast')
        skill = self.tags.get('skill')
        if skill:
            r += '\n' + Dialog.get('equipment_skill', [skill])
            from src.tools.Data import Data
            data = Data.get_line('raw/descriptions.txt', 'sk.' + skill)
            if data:
                r += '\n' + data[1]
        return r

    def get_value(self):
        enc = 1 + (self.get_level() * self.get_level() * .05)
        r = int(max(1, int(self.tags.get('p', 0) / 10) - self.weight + super().get_value()) * enc)
        return r

    def use(self):
        self.wear()

    def wear(self, start=False):
        self.show(False)
        self.host.action.act('grab', 8)
        if self.host.weapon == self:
            host = self.host
            self.host.drop()
            self.host = host
        if not start:
            self.on_wear()
        host = self.host
        if self.host.weapon == self:
            self.host.drop()
        self.save = False
        self.host = host
        self.host.face(self.host.direction)

    def remove(self):
        if self.host:
            self.unwear()
        super().remove()

    def unwear(self):
        self.show(True)
        self.on_unwear()
        self.on_unwield()
        return self

    def on_wear(self):
        self.location.sound.register(self.pos, 3, file='wear')
        speed = self.tags.get('spd', 0)
        if speed != 0:
            self.host.tags.increment('spd', speed, add=True)
        if self.tags.get('p'):
            self.host.tags.increment('p', self.tags.get('p'))
            self.host.tags.increment('p>', self.tags.get('p>'))

    def on_unwear(self):
        self.location.sound.register(self.pos, 3, file='wear')
        speed = self.tags.get('spd', 0)
        if speed != 0:
            self.host.tags.increment('spd', -speed, remove=True)
        if self.tags.get('p'):
            self.host.tags.set('p', max(1, self.host.tags.get('p') - self.tags.get('p')))
            self.host.tags.set('p>', max(1, self.host.tags.get('p>') - self.tags.get('p>')))
