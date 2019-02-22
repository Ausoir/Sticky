from src.entity.Prop import Prop
from src.entity.Space import Space
from src.entity.unit.ai.Faction import Faction
from src.game.Global import DEPTH_EFFECT
from src.map.Tile import Tile


class Projectile(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.faction = Faction.PROJECTILE
        self.lifetime = 2
        self.gravity = 0
        self.hittable = 0
        self.durability = 999
        self.depth = DEPTH_EFFECT

    def __str__(self):
        return super().__str__() + ',' + str(self.lifetime)

    def load(self, arg):
        index = super().load(arg)
        self.lifetime = arg[index]
        return index + 1

    def turn(self):
        if self.lifetime == 0:
            self.remove()
        else:
            self.effect()
        self.lifetime -= 1

    def effect(self):
        pass

    def crash(self, callback=None):
        self.location.attack.register(1, self.pos[0], 1, faction=Faction.PROJECTILE, callback=callback)

    def fly(self, tx, ty, distance, flag=Tile.CHECK_TERRAIN):
        self.form.rotation = Space(tx, ty).get_atan() + 180
        return self.pos[0] != self.move(tx, ty, distance=distance, flag=flag)
