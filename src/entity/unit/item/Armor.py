from src.entity.unit.item.Item import Item
from src.game.Tags import Tags
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
        self.form_arm = None
        self.form_leg = None

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
            item = Stock.get(i[2], i)
            self.items.append(item)
        return index + 3

    def make_form(self, arg):
        Data.initialize_image(self.name, arg, (16, 48))
        super().make_form(self.name + '_0x0')
        self.form_arm = Data.run_cache(self.name + '_1x0')
        self.form_leg = Data.run_cache(self.name + '_2x0')
        self.form_name = arg
        self.form.rotation = 180

    def die(self):
        pos = self.pos[0]
        if self.host:
            pos = self.host.pos[0]
            self.host.unarmor()
        while self.items:
            item = self.items.pop(0)
            item.relocate(pos.x, pos.y, force=1)
            item.add()
        super().die()

    def on_unequip(self):
        super().on_unequip()
        self.form.rotation = 180
        self.form.size.y = 48
        self.form.pivot.y = 24

    def describe(self):
        inv = 0
        for row in self.inventory:
            for slot in row:
                if slot == Armor.VACANT:
                    inv += 1
        r = super().describe()
        r += '\nEncumbrance: ' + str(self.encumbrance)
        r += '\nInventory: ' + str(inv)
        return r

    def use(self, host=None):
        if not host:
            host = self.host
        host.action.set('rest')
        if not host.is_armored():
            host.armor = self
            if host.weapon == self:
                host.drop()
            host.face(1)
            for i in host.form.organs:
                if i.part == 0:
                    i.set(self.form)
                elif i.part == 1:
                    i.set(self.form_arm)
                elif i.part == 2:
                    i.set(self.form_leg)
            self.host = host
            self.remove()
            self.host.update_durability()
        else:
            host.unarmor()

    def is_vacant(self, item, x, y):
        for ix in range(x, x + item.volume[0]):
            for iy in range(y, y + item.volume[1]):
                if ix > 2 or iy > 3 or self.inventory[iy][ix] != Armor.VACANT:
                    return 0
        return 1

    def add_item(self, item):
        for ix in range(3):
            for iy in range(4):
                if self.is_vacant(item, ix, iy):
                    self.add_inventory(item, ix, iy)
                    return 1
        return 0

    def add_inventory(self, item, x, y):
        item.remove()
        item.pos[0] = self.location.get_tile(x, y)
        self.items.append(item)
        self.modify_inventory(item, Armor.VACANT, Armor.OCCUPIED)
        self.host.update_durability()

    def get_item_at(self, x, y, pop=0):
        r = None
        for i in self.items:
            if i.pos[0].x <= x < i.pos[0].x + i.volume[0] and i.pos[0].y <= y < i.pos[0].y + i.volume[1]:
                r = i
                break
        if r and pop:
            self.modify_inventory(r, Armor.OCCUPIED, Armor.VACANT)
            self.items.remove(r)
            if self.host:
                self.host.update_durability()
        return r

    def modify_inventory(self, item, state_from, state_to):
        for iy in range(item.pos[0].y, item.pos[0].y + item.volume[1]):
            for ix in range(item.pos[0].x, item.pos[0].x + item.volume[0]):
                if self.inventory[iy][ix] == state_from:
                    self.inventory[iy][ix] = state_to

    def get_reduction(self, damage):
        total = 0
        armors = []
        for i in self.items:
            if Tags.armor in i.tags:
                final_damage = max(0, min(damage, i.durability))
                i.durability = i.durability - final_damage
                damage -= final_damage
                total += i.durability
                if i.durability == 0:
                    armors.append(i)
        final_damage = max(0, min(damage, self.durability))
        self.durability = self.durability - final_damage
        damage -= final_damage
        total = max(0, total + self.durability)
        for i in armors:
            x, y = i.pos[0].x, i.pos[0].y
            scrap = Tags.scrap in i.tags
            self.get_item_at(x, y, pop=1)
            if scrap:
                from src.entity.Stock import Stock
                self.add_inventory(Stock.get('Scrap'), x, y)
        return total, damage
