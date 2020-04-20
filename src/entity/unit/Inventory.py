from src.game import Global


class Inventory:
    def __init__(self, host):
        self.host = host
        self.items = []

    def __str__(self):
        items = []
        for i in self.items:
            items.append('[' + i.__str__() + ']')
        items = ','.join(items)
        return '[' + items + ']'

    def load(self, p):
        from src.entity.Stock import Stock
        self.items = []
        Global.r_t.reset(self.host.tags.get('seed', 0) + 1234)
        for i in p:
            if isinstance(i, str):
                if i.startswith('?'):
                    if Global.r_t.rand_bool():
                        continue
                    else:
                        i = i[1:]
                item = Stock.get(self.host.location, i)
                if not self.is_vacant(item.get_weight()):
                    continue
            else:
                item = Stock.get(self.host.location, i[2], i)
            item.host = self.host
            self.items.append(item)

    def attempt_add(self, item):
        if self.is_vacant(item.get_weight()):
            self.add_item(item)
        else:
            from src.game import Global
            from src.tools.Dialog import Dialog
            params = [self.host.get_equipment_weight(), self.host.get_capacity(), item.get_weight()]
            Global.main.monologue.set(Dialog.get('!heavy', params))

    def is_vacant(self, weight):
        return self.host.get_capacity() >= self.host.get_equipment_weight() + weight and len(self.items) < 12

    def add_item(self, item):
        item.remove()
        item.host = self.host
        self.items.append(item)
        return len(self.items) - 1

    def get_item(self, item_index):
        if 0 <= item_index < len(self.items):
            item = self.items[item_index]
            self.items.remove(item)
            item.pos = self.host.pos
            item.on_unwield()
            return item.add()

    def update_capacity(self):
        while not self.is_vacant(0) and len(self.items) > 0:
            item = self.get_item(0)
            item.host = self.host
            item.on_unwield()

    def drop_all(self):
        while self.items:
            item = self.get_item(0)
            item.host = self.host
            item.on_unwield()

    def on_sleep(self, time):
        for i in self.items.copy():
            i.on_sleep(time)
