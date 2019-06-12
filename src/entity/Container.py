from src.entity.Prop import Prop
from src.tools.Random import Random


class Container(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.loots = None

    def __str__(self):
        return super().__str__() + ',[' + ','.join(self.loots) + ']'

    def load(self, arg):
        index = super().load(arg)
        self.loots = arg[index]
        return index + 1

    def add(self):
        super().add()
        return self

    def die(self):
        if self.loots:
            from src.entity.Stock import Stock
            loot = self.loots[Random.rand_int(0, len(self.loots) - 1)]
            Stock.make(loot, self.pos[0])
        super().die()
