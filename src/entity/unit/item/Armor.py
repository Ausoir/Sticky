from src.entity.unit.item.Equipment import Equipment
from src.tools.Data import Data


class Armor(Equipment):
    NONE = 1
    VACANT = 2
    OCCUPIED = 3

    def __init__(self, loc):
        super().__init__(loc)
        self.inventory = []
        self.items = []
        self.pockets = [0]
        self.form_armL = None
        self.form_armR = None
        self.form_legL = None
        self.form_legR = None
        self.armor = 0

    def __str__(self):
        r = super().__str__()
        inventory = ','.join(str(x[0]) + str(x[1]) + str(x[2]) for x in self.inventory)
        items = []
        for i in self.items:
            items.append('[' + i.__str__() + ']')
        items = ','.join(items)
        pockets = ','.join(str(x) for x in self.pockets)
        r += ',' + str(self.armor) + ',[' + inventory + '],[' + items + '],[' + pockets + ']'
        return r

    def load(self, p):
        from src.entity.Stock import Stock
        index = super().load(p)
        self.armor = p[index]
        index += 1
        self.inventory = []
        for i in p[index]:
            row = []
            for c in str(i):
                row.append(int(c))
            self.inventory.append(row)
        index += 1
        self.items = []
        for i in p[index]:
            item = Stock.get(i[2], i)
            self.items.append(item)
        index += 1
        self.pockets = p[index]
        return index + 1

    def set_form(self, arg):
        Data.initialize_image(self.name, arg, (16, 32))
        super().set_form(self.name + '_0x0')
        self.form_armL = Data.run_cache(self.name + '_1x0')
        self.form_armR = self.form_armL.clone()
        self.form_legL = Data.run_cache(self.name + '_2x0')
        self.form_legR = self.form_legL.clone()
        self.form_name = arg

    def die(self):
        pos = self.pos
        if self.host:
            pos = self.host.pos
            self.host.unarmor()
        while self.items:
            item = self.items.pop(0)
            item.relocate(pos.x, pos.y, force=1)
            item.add()
        super().die()

    def get_value(self):
        inv = 0
        for row in self.inventory:
            for cell in row:
                if cell != 1:
                    inv += 1
        inv += len(self.pockets)
        r = super().get_value() + self.armor + inv
        return r

    def describe(self):
        r = super().describe()
        r += '\nInventory Space: ' + str(self.get_inventory_slots())
        r += '\nDefense: ' + str(self.armor)
        r += '\nPockets: ' + str(len(self.pockets))
        return r

    def get_inventory_slots(self):
        inv = 0
        for row in self.inventory:
            for slot in row:
                if slot == Armor.VACANT:
                    inv += 1
        return inv

    def use(self):
        self.host.action.set('wait')
        if self.host.attributes.agility >= self.weight + self.host.headgear.weight:
            if self.host.is_armored():
                self.host.unarmor()
            self.host.armor = self
            host = self.host
            if self.host.weapon == self:
                self.host.drop()
            host.face(1)
            forms = [self.form_armL, self.form_legL, self.form_legR, None, self.form, self.form_armR]
            for k, i in enumerate(host.form.organs):
                if forms[k]:
                    i.set(forms[k])
            self.remove()
            host.update_durability(0)
            self.host = host
            for i in self.items:
                i.host = host
        else:
            self.host.say('Total encumbrance exceeds Agility!')

    def is_vacant(self, item, x, y):
        for ix in range(x, x + item.volume[0]):
            for iy in range(y, y + item.volume[1]):
                if ix > 2 or iy > 1 or self.inventory[iy][ix] != Armor.VACANT:
                    return 0
        return 1

    def add_item(self, item):
        for ix in range(3):
            for iy in range(2):
                if self.is_vacant(item, ix, iy):
                    return self.add_inventory(item, ix, iy)

    def add_inventory(self, item, x, y):
        item.remove()
        item.pos = self.location.get_tile((x, y))
        item.host = self.host
        self.items.append(item)
        self.modify_inventory(item, Armor.VACANT, Armor.OCCUPIED)
        self.host.update_durability(0)
        return len(self.items) - 1

    def get_item_at(self, x, y, pop=0):
        r = None
        for k, i in enumerate(self.items):
            if i.pos.x <= x < i.pos.x + i.volume[0] and i.pos.y <= y < i.pos.y + i.volume[1]:
                r = i
                if pop:
                    self.get_item(k)
                break
        return r

    def get_item(self, item_index):
        if 0 <= item_index < len(self.items):
            for k, v in enumerate(self.pockets):
                if v == item_index:
                    self.pockets[k] = -1
            item = self.items[item_index]
            self.modify_inventory(item, Armor.OCCUPIED, Armor.VACANT)
            self.items.remove(item)
            if self.host:
                self.host.update_durability(0)
            return item

    def modify_inventory(self, item, state_from, state_to):
        for iy in range(item.pos.y, item.pos.y + item.volume[1]):
            for ix in range(item.pos.x, item.pos.x + item.volume[0]):
                if self.inventory[iy][ix] == state_from:
                    self.inventory[iy][ix] = state_to
