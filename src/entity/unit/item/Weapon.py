from src.entity.unit.item.Item import Item


class Weapon(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.damage = 1

    def __str__(self):
        return super().__str__() + ',' + str(self.damage)

    def load(self, arg):
        index = super().load(arg)
        self.damage = arg[index]
        return index + 1

    def set_form(self, arg):
        if not self.form:
            super().set_form(arg)
            self.form.rotation = -75

    def on_unequip(self):
        super().on_unequip()
        self.form.rotation = -75

    def describe(self):
        r = super().describe()
        min_d, max_d = self.get_damage()
        r += '\nDamage: ' + str(min_d) + ' ~ ' + str(max_d)
        return r

    def get_damage(self):
        min_d = 0
        acc = self.tags.get('acc')
        if acc:
            min_d += acc
        return min_d, self.damage

    def get_value(self):
        other = 0
        if self.tags.get('sharp'):
            other += 1
        if self.tags.get('silver'):
            other += 1
        from src.entity.unit.item.Item import Item
        score = Item.get_value(self) + other + self.weight
        return max(1, score)
