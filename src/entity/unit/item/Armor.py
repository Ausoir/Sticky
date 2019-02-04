from src.entity.unit.item.Item import Item


class Armor(Item):
    def __init__(self, form, seed, loc, encumbrance, dimensions):
        self.form_name = form
        super().__init__(form + '_0x0', seed, loc)
        self.encumbrance = encumbrance
        self.inventory = dimensions

    def __str__(self):
        r = super().__str__()
        r += ',' + str(self.encumbrance) + ',' + ('[' + ','.join(str(x) for x in self.inventory) + ']')
        return r

    def load(self, p):
        index = super().load(p)
        self.encumbrance = p[index]
        self.inventory = p[index + 1]
        return index + 2

    def use(self, host=None):
        if not host:
            host = self.host
        host.armor = self
        host.face(1)
        for i in host.form.organs:
            if i.part != 3:
                i.set(self.form_name + '_'+str(i.part)+'x0')
        host.drop()
        self.remove()
