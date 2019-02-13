from src.entity.Prop import Prop
from src.entity.Space import Space
from src.map.Tile import Tile


class Projectile(Prop):
    def __init__(self, loc):
        super().__init__(loc)
        self.count = 1
        self.gravity = 0

    def __str__(self):
        return super().__str__() + ',' + str(self.count)

    def load(self, arg):
        index = super().load(arg)
        self.count = arg[index]
        return index + 1

    def turn(self):
        if self.count == 0:
            self.remove()
        else:
            self.effect()
        self.count -= 1

    def add_to(self, faction, pos):
        super().add()
        self.faction = faction
        self.relocate(pos.x, pos.y, force=1)
        return self

    def effect(self):
        pass

    def crash(self, callback=None):
        self.location.attack.register(1, self.pos[0], 1, faction=self.faction, callback=callback)

    def fly(self, tx, ty, distance, flag=Tile.CHECK_TERRAIN):
        self.form.rotation = Space(tx, ty).get_atan() + 180
        self.move(tx, ty, distance=distance, flag=flag)
