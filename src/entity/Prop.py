from src.entity.Object import Object
from src.entity.unit.ai.Faction import Faction
from src.game.Tags import Tags
from src.map.Tile import Tile


class Prop(Object):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.Buffs import Buffs
        self.durability = 1
        self.hittable = 1
        self.collide = Tile.COLLIDE_PROP
        self.faction = Faction.FFA
        self.states = Buffs(self)
        self.tags = []

    def __str__(self):
        tags = ','.join(self.tags)
        return super().__str__() + ',[' + tags + '],' + str(self.durability) + ',[' + self.states.__str__() + ']'

    def load(self, arg):
        index = super().load(arg)
        self.tags = arg[index]
        index += 1
        self.durability = arg[index]
        index += 1
        self.states.load(arg[index])
        index += 1
        return index

    def turn(self):
        super().turn()
        self.states.update()

    def die(self):
        if Tags.wood in self.tags:
            from src.entity.Stock import Stock
            Stock.get('Wood').add().relocate(self.pos[0].x, self.pos[0].y, force=1)
        self.remove()

    def hit(self, damage):
        if self.hittable:
            if self.durability != -1:
                self.durability = max(0, self.durability - damage)
                if self.durability == 0:
                    self.die()
            return 1
        return 0

    def clean_buffs(self, force=0):
        return self.states.clear(force)
