class Inventory:
    def __init__(self, host):
        self.host = host
        self.items = None

    def __str__(self):
        items = []
        for i in self.items:
            if isinstance(i, str):
                items.append(i)
            else:
                items.append('[' + i.__str__() + ']')
        items = ','.join(items)
        return '[' + items + ']'

    def load(self, p):
        self.items = []
        seed = None
        from src.entity.Stock import Stock
        for k, i in enumerate(p):
            if isinstance(i, str):
                if i.startswith('?'):
                    if seed is None:
                        seed = bin(self.host.get_seed() % (2 ** len(p)))[2:]
                        while len(seed) < len(p):
                            seed = '0' + seed
                    if seed[k] == '1':
                        if Stock.check(i[1:]):
                            self.items.append(i[1:])
                else:
                    if Stock.check(i):
                        self.items.append(i)
            else:
                item = Stock.get(self.host.location, i[2], i)
                item.host = self.host
                self.items.append(item)

    def attempt_add(self, item, insert=False):
        if self.host.is_vacant(item.get_weight()):
            self.add_item(item, insert=insert)
        else:
            from src.game import Global
            if self.host == Global.player.character:
                from src.tools.Dialog import Dialog
                params = [self.host.get_equipment_weight(), self.host.get_capacity(), item.get_weight()]
                Global.main.monologue.set(Dialog.get('!heavy', params))

    def add_item(self, item, insert=False):
        item.remove()
        item.host = self.host
        if insert:
            self.items.insert(0, item)
        else:
            self.items.append(item)
        return len(self.items) - 1

    def get_weight(self):
        r = 0
        for i in self.get_range():
            r += self.get_item(i).get_weight()
        return r

    def get_range(self):
        return range(len(self.items))

    def get_all_items(self):
        r = []
        for i in self.get_range():
            r.append(self.get_item(i))
        return r

    def get_item_index(self, item_name):
        for k, i in enumerate(self.items):
            if i.name == item_name:
                return k

    def get_item(self, index):
        if self.validate_index(index):
            from src.entity.Stock import Stock
            item = self.items[index]
            if isinstance(item, str):
                item = Stock.get(self.host.location, item)
                if item:
                    self.items[index] = item
            return item

    def validate_index(self, index):
        if 0 <= index < len(self.items):
            return True

    def take_item(self, item_index):
        if 0 <= item_index < len(self.items):
            item = self.get_item(item_index)
            self.items.remove(item)
            item.pos = self.host.pos
            item.on_unwield()
            return item.add()

    def find_weapon(self):
        for i in self.get_range():
            item = self.get_item(i)
            if item.tags.get('dmg', 0) > 0 or item.tags.get('DMG', 0) > 0:
                return i

    def update_capacity(self):
        while not self.host.is_vacant(0) and len(self.items) > 0:
            item = self.take_item(0)
            item.host = self.host
            item.on_unwield()

    def drop_all(self):
        while self.items:
            item = self.take_item(0)
            item.host = self.host
            item.on_unwield()

    def prioritize(self, index):
        self.items[0], self.items[index] = self.items[index], self.items[0]
