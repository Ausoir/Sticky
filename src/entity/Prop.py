from src.entity.Object import Object
from src.entity.unit.ai.Faction import Faction
from src.map.Tile import Tile


class Prop(Object):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.Buffs import Buffs
        self.durability = 1
        self.hittable = 1
        self.collide = Tile.COLLIDE_PROP
        self.faction = Faction.FFA
        self.loot = None
        self.states = Buffs(self)

    def __str__(self):
        return super().__str__() + ',' + str(self.collide) + ',' + str(self.durability) + ',' + str(self.loot) + ',[' +\
               self.states.__str__() + ']'

    def load(self, arg):
        index = super().load(arg)
        if arg[index]:
            self.collide = arg[index]
            self.depth = self.collide
        index += 1
        self.durability = arg[index]
        index += 1
        self.loot = arg[index]
        index += 1
        self.states.load(arg[index])
        index += 1
        return index

    def turn(self):
        super().turn()
        self.states.update()

    def die(self):
        if self.loot:
            from src.entity.Stock import Stock
            Stock.get(self.loot).add().relocate(self.pos[0].x, self.pos[0].y, force=1)
        self.remove()

    def hit(self, damage):
        if self.hittable:
            self.durability -= damage
            if self.durability <= 0:
                self.die()
            return 1
        return 0

    def clean_buffs(self, force=0):
        return self.states.clear(force)
