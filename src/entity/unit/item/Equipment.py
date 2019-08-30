from src.entity.unit.item.Item import Item


class Equipment(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.max_durability = 0

    def __str__(self):
        return super().__str__() + ',' + str(self.max_durability) + ',' + str(self.weight)

    def load(self, p):
        index = super().load(p)
        self.max_durability = p[index]
        index += 1
        self.weight = p[index]
        return index + 1

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
        r = max(1, int(self.durability / 3) - self.weight + 1)
        return r

    def describe(self):
        orig = self.name
        self.name = self.get_display_name()
        r = super().describe()
        self.name = orig
        if self.durability != -1:
            if self.max_durability == -1:
                r += '\nMaximum Durability: Unbreakable'
            else:
                r += '\nMaximum Durability: ' + str(self.max_durability)
        r += '\nMarket Value: ' + str(self.get_value())
        r += '\nEncumbrance: ' + str(self.weight)
        return r

    def get_reduction(self, damage):
        if self.durability == -1:
            return 0, damage
        total = 0
        final_damage = max(0, min(damage, self.durability))
        self.durability = self.durability - final_damage
        damage -= final_damage
        total = max(0, total + self.durability)
        return total, damage
