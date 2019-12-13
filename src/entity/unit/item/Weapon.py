from src.entity.unit.item.Equipment import Equipment


class Weapon(Equipment):
    def __str__(self):
        return super().__str__() + ',' + str(self.form.image.height - self.form.image.anchor_y)

    def load(self, arg):
        index = super().load(arg)
        self.form.image.anchor_y = self.form.image.height - arg[index]
        return index + 1

    def set_form(self, arg):
        if not self.form:
            super().set_form(arg)

    def get_value(self):
        other = 0
        if 'ps' in self.tags:
            other += 1
        if 'is' in self.tags:
            other += 1
        from src.entity.unit.item.Item import Item
        score = Item.get_value(self) + other + self.weight
        return max(1, score)
