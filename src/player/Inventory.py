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
            item = Stock.get(i[2], i)
            self.items.append(item)

    def get_weight(self):
        total = 0
        for i in self.items:
            total += i.weight
        return total

    def get_capacity(self):
        return self.host.armor.capacity

    def attempt_add(self, item):
        if self.is_vacant(item):
            self.add_item(item)
        else:
            from src.game import Global
            Global.main.monologue.set('Does not fit in inventory')

    def is_vacant(self, item):
        return self.get_capacity() >= self.get_weight() + item.weight

    def add_item(self, item):
        if self.is_vacant(item):
            item.remove()
            item.host = self.host
            self.items.append(item)
            return len(self.items) - 1

    def get_item(self, item_index):
        if 0 <= item_index < len(self.items):
            for k, v in enumerate(self.host.armor.pockets):
                if v == item_index:
                    self.host.armor.pockets[k] = -1
            item = self.items[item_index]
            self.items.remove(item)
            return item
