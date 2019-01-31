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

    def die(self):
        self.remove()

    def hit(self, hitter, damage):
        if self.hittable:
            self.durability -= damage
            if self.durability <= 0:
                self.die()
            return 1
        return 0
