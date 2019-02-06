from src.entity.Object import Object
from src.entity.unit.ai.Faction import Faction
from src.map.Tile import Tile


class Prop(Object):
    def __init__(self, form, seed, loc):
        super().__init__(form, seed, loc)
        self.durability = 1
        self.hittable = 1
        self.collide = Tile.CHECK_PROP
        self.faction = Faction(Faction.FFA)
        self.loot = None

    def __str__(self):
        return super().__str__() + ',' + str(self.durability) + ',' + str(self.loot)

    def load(self, arg):
        index = super().load(arg)
        self.durability = arg[index]
        self.loot = arg[index + 1]
        return index + 2

    def die(self):
        if self.loot:
            from src.entity.Stock import Stock
            Stock.get(self.loot, self.location).add().relocate(self.pos[0].x, self.pos[0].y)
        self.remove()

    def hit(self, hitter, damage):
        if self.hittable:
            self.durability -= damage
            if self.durability <= 0:
                self.die()
            return 1
        return 0
