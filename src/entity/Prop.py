from src.entity.Object import Object
from src.game.Tags import Tags
from src.map.Tile import Tile


class Prop(Object):
    def __init__(self, loc):
        super().__init__(loc)
        from src.entity.unit.Buffs import Buffs
        self.durability = -1
        self.hittable = 1
        self.collide = Tile.COLLIDE_PROP
        self.faction = 0
        self.loot = []
        self.states = Buffs(self)
        self.tags = []
        self.depth = 2

    def __str__(self):
        tags = '[' + ','.join(self.tags) + ']'
        loot = '[' + ','.join(str(x) for x in self.loot) + ']'
        return ','.join([super().__str__(), tags, str(self.durability), loot, '[' + self.states.__str__() + ']'])

    def load(self, arg):
        index = super().load(arg)
        self.tags = arg[index]
        index += 1
        if arg[index] >= -1:
            self.durability = arg[index]
        else:
            from src.game import Global
            variance = int(-arg[index] / 2)
            self.durability = Global.r.rand_int(-arg[index] - variance, -arg[index] + variance)
        index += 1
        if arg[index]:
            self.loot = arg[index]
        index += 1
        self.states.load(arg[index])
        index += 1
        if Tags.float in self.tags:
            self.gravity = 0
        if Tags.back in self.tags:
            self.depth = 1
        if Tags.front in self.tags:
            self.depth = 5
        if Tags.fog in self.tags:
            self.collide = Tile.COLLIDE_FOG
        if Tags.indestructible in self.tags:
            self.hittable = 0
        if Tags.intangible in self.tags:
            self.collide = 0
        elif Tags.land in self.tags:
            self.collide = Tile.COLLIDE_DOODAD
        return index

    def turn(self):
        super().turn()
        self.states.update()

    def die(self):
        if self.loot:
            from src.entity.Stock import Stock
            from src.game import Global
            loot = Global.r.rand_list(self.loot)
            if loot:
                Stock.make(loot, self.pos[0])
        self.remove()

    def is_hit(self, chance, faction=0):
        if self.hittable and self.faction != faction:
            if Tags.metal in self.tags:
                return chance > 4
            elif Tags.wood in self.tags:
                return chance > 2
            return 1

    def hit(self, damage):
        if self.durability != -1:
            self.durability = max(0, self.durability - damage)
            if self.durability == 0:
                self.die()
                return 1
