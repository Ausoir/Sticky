from src.entity.unit.item.Item import Item


class Equipment(Item):
    def __init__(self, loc):
        super().__init__(loc)
        self.max_durability = 0

    def __str__(self):
        return super().__str__() + ',' + str(self.max_durability) + ',' + str(self.weight)

    def load(self, p):
        index = super().load(p)
        self.max_durability = p[index]
        index += 1
        self.weight = p[index]
        return index + 1

    def describe(self):
        r = 'Maximum Durability: ' + str(self.max_durability) + '\n'
        r += 'Encumbrance: ' + str(self.weight) + '\n'
        return r

    def get_reduction(self, damage):
        if self.durability == -1:
            return 0, damage
        total = 0
        final_damage = max(0, min(damage, self.durability))
        self.durability = self.durability - final_damage
        damage -= final_damage
        total = max(0, total + self.durability)
        return total, damage
