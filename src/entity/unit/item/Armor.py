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

    def describe(self):
        inv = 0
        for row in self.inventory:
            for i in str(row):
                if i == '1':
                    inv += 1
        r = 'Encumbrance: ' + str(self.encumbrance) + '\n'
        r += 'Inventory: ' + str(inv) + '\n'
        return r

    def use(self, host=None):
        if not host:
            host = self.host
        host.armor = self
        host.face(1)
        for i in host.form.organs:
            if i.part != 3:
                i.set(self.form_name + '_'+str(i.part)+'x0')
        if host.weapon == self:
            host.drop()
        self.remove()

    def get_inventory(self):
        r = []
        for i in self.inventory:
            if i == 0:
                r.append([0, 0, 0])
            elif i == 100:
                r.append([1, 0, 0])
            elif i == 10:
                r.append([0, 1, 0])
            elif i == 1:
                r.append([0, 0, 1])
            elif i == 110:
                r.append([1, 1, 0])
            elif i == 11:
                r.append([0, 1, 1])
            elif i == 101:
                r.append([1, 0, 1])
            elif i == 111:
                r.append([1, 1, 1])
        return r
