from src.entity.unit.item.Item import Item


class Equipment(Item):
    def get_enhance_chance(self):
        return int(100 * (1 / max(1, self.get_level() + 1)))

    def enhance(self, rng):
        if rng <= self.get_enhance_chance():
            self.states.add('Modified', -1, var=1)
            return True
        return False

    def get_level(self):
        mod = self.states.get('Modified')
        if mod:
            return mod.var
        return 0

    def get_display_name(self):
        level = self.get_level()
        if level > 0:
            return self.name + ' +' + str(level)
        else:
            return self.name

    def get_value(self):
        enc = 1 + (self.get_level() * self.get_level() * .05)
        r = int(max(1, self.durability - self.weight + super().get_value()) * enc)
        return r

    def describe(self):
        orig = self.name
        self.name = self.get_display_name()
        r = super().describe()
        self.name = orig
        r += '\nMarket Value: ' + str(self.get_value())
        r += '\nEncumbrance: ' + str(self.weight)
        if 'armor' in self.tags:
            r += 'This armor halves damage.'
        if 'mat' in self.tags and self.tags['mat'] == 'Metal':
            r += 'This armor shaves off 1 damage.'
        return r

    def get_reduction(self, damage):
        if 'armor' in self.tags:
            damage = int(damage * .5)
        if 'mat' in self.tags:
            if self.tags['mat'] == 'Metal':
                damage = max(0, damage - 1)
        return damage

    def on_wear(self):
        pass

    def on_unwear(self):
        pass
