from src.entity.unit.item.Item import Item
from src.tools.Data import Data


class Armor(Item):
    NONE = 1
    VACANT = 2
    OCCUPIED = 3

    def __init__(self, loc):
        super().__init__(loc)
        self.encumbrance = None
        self.items = []
        self.inventory = []

    def __str__(self):
        r = super().__str__()
        inventory = ','.join(str(x[0]) + str(x[1]) + str(x[2]) for x in self.inventory)
        items = []
        for i in self.items:
            items.append('[' + i.__str__() + ']')
        items = ','.join(items)
        r += ',' + str(self.encumbrance) + ',[' + inventory + '],[' + items + ']'
        return r

    def load(self, p):
        from src.entity.Stock import Stock
        index = super().load(p)
        self.encumbrance = p[index]
        self.inventory = []
        for i in p[index + 1]:
            row = []
            for c in str(i):
                row.append(int(c))
            self.inventory.append(row)
        self.items = []
        for i in p[index + 2]:
            self.items.append(Stock.get(i[2], self.location, i))
        return index + 3

    def make_form(self, arg):
        Data.initialize_image(self.name, arg, (16, 48))
        super().make_form(self.name + '_0x0')
        self.form_name = arg

    def describe(self):
        inv = 0
        for row in self.inventory:
            for slot in row:
                if slot == Armor.VACANT:
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
                i.set(self.name + '_'+str(i.part)+'x0')
        if host.weapon == self:
            host.drop()
        self.remove()

    def is_vacant(self, item, x, y):
        for ix in range(x, x + item.volume[0]):
            for iy in range(y, y + item.volume[1]):
                if ix > 2 or iy > 3 or self.inventory[iy][ix] != Armor.VACANT:
                    return 0
        return 1

    def add_inventory(self, item, x, y):
        item.pos[0] = self.location.get_tile(x, y)
        self.items.append(item)
        self.modify_inventory(item, Armor.VACANT, Armor.OCCUPIED)

    def get_item_at(self, x, y, pop=0):
        r = None
        for i in self.items:
            if i.pos[0].x <= x <= i.pos[0].x + i.volume[0] and i.pos[0].y <= y <= i.pos[0].y + i.volume[1]:
                r = i
                break
        if r and pop:
            self.modify_inventory(r, Armor.OCCUPIED, Armor.VACANT)
            self.items.remove(r)
        return r

    def modify_inventory(self, item, state_from, state_to):
        for iy in range(item.pos[0].y, item.pos[0].y + item.volume[1]):
            for ix in range(item.pos[0].x, item.pos[0].x + item.volume[0]):
                if self.inventory[iy][ix] == state_from:
                    self.inventory[iy][ix] = state_to
