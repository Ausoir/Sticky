from src.entity.unit.item.Item import Item


class Weapon(Item):
    def __init__(self, form, seed, loc):
        super().__init__(form, seed, loc)

    def __str__(self):
        return super().__str__() + ',' + str(self.form.pivot.x) + ',[' + ','.join(str(x) for x in self.range) + ']'

    def load(self, arg):
        index = super().load(arg)
        self.form.pivot.x = arg[index]
        self.range = arg[index + 1]
        return index + 2
