from src.entity.Prop import Prop


class Container(Prop):
    def __init__(self):
        super().__init__()
        from src.entity.unit.Inventory import Inventory
        self.inventory = Inventory(self)

    def __str__(self):
        return super().__str__() + ',' + self.inventory.__str__()

    def load(self, arg):
        index = super().load(arg)
        self.inventory.load(arg[index])
        return index + 1

    def load_content(self):
        have = self.tags.remove('have', 0)
        if have > 0:
            for i in range(have):
                loot = self.get_loot()
                if loot:
                    self.inventory.items.append(loot)
            self.tags.remove('loot')

    def die(self):
        self.load_content()
        self.inventory.drop_all()
        super().die()

    def is_vacant(self, weight):
        return self.tags.get('str', 0) >= self.inventory.get_weight() + weight
