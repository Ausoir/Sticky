from src.entity.unit.item.Item import Item


class Headgear(Item):
    @classmethod
    def make(cls, fn):
        getattr(cls, fn)()

    def __init__(self, loc):
        super().__init__(loc)
        self.encumbrance = None

    def __str__(self):
        return super().__str__() + ',' + str(self.encumbrance)

    def load(self, p):
        index = super().load(p)
        self.encumbrance = p[index]
        return index + 1

    def die(self):
        if self.host:
            self.host.unheadgear()
        super().die()

    def describe(self):
        r = 'Encumbrance: ' + str(self.encumbrance) + '\n'
        return r

    def use(self):
        self.host.headgear = self
        host = self.host
        if self.host.weapon == self:
            self.host.drop()
        self.remove()
        host.update_durability()
        self.host = host

    def get_reduction(self, damage):
        if self.durability == -1:
            return 0, damage
        total = 0
        final_damage = max(0, min(damage, self.durability))
        self.durability = self.durability - final_damage
        damage -= final_damage
        total = max(0, total + self.durability)
        return total, damage
