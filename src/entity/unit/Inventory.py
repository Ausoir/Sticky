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
        for i in p:
            if isinstance(i, str):
                item = Stock.get(i)
            else:
                item = Stock.get(i[2], i)
                item.show(False)
            self.items.append(item)

    def get_weight(self):
        total = 0
        for i in self.items:
            total += i.weight
        return total + self.host.weapon.weight

    def get_capacity(self):
        return self.host.armor.capacity + 8

    def attempt_add(self, item):
        if self.is_vacant(item.weight):
            self.add_item(item)
        else:
            from src.game import Global
            from src.tools.Dialog import Dialog
            Global.main.monologue.set(Dialog.get('!heavy'))

    def is_vacant(self, weight):
        return self.get_capacity() >= self.get_weight() + weight and len(self.items) < 12

    def add_item(self, item):
        if self.is_vacant(item.weight):
            item.remove()
            item.host = self.host
            self.items.append(item)
            return len(self.items) - 1

    def get_item(self, item_index):
        if 0 <= item_index < len(self.items):
            item = self.items[item_index]
            self.items.remove(item)
            return item

    def update_capacity(self):
        while not self.is_vacant(0):
            item = self.get_item(0)
            item.host = self.host
            item.on_unequip()
